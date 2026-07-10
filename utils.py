import bpy
import math
import bmesh
from mathutils import Vector

# ---------------------------------------------------
# Collection and Object Helpers
# ---------------------------------------------------

def create_or_get_collection(parent_collection, collection_name):
    """Creates a new collection or gets an existing one, avoiding duplicate naming."""
    # 1. Check if the collection is already linked as a child of parent_collection
    if collection_name in parent_collection.children:
        return parent_collection.children[collection_name]
        
    # 2. Check if the collection exists globally in bpy.data.collections
    if collection_name in bpy.data.collections:
        existing_coll = bpy.data.collections[collection_name]
        # Link it to the parent if not already linked
        if existing_coll.name not in parent_collection.children:
            parent_collection.children.link(existing_coll)
        return existing_coll
        
    # 3. Create a new collection and link it to the parent
    new_collection = bpy.data.collections.new(collection_name)
    parent_collection.children.link(new_collection)
    return new_collection

def get_target_parent_collection(context):
    """Retrieves or creates the parent collection based on scene properties."""
    scene = context.scene
    if scene.custom_light_auto_collection:
        if scene.custom_light_target_coll_type == 'EXISTING' and scene.custom_light_target_coll_ptr:
            return scene.custom_light_target_coll_ptr
        else:
            name = scene.custom_light_target_coll_name.strip()
            if not name:
                name = "Custom Lights"
            return create_or_get_collection(scene.collection, name)
    return context.collection

def add_object_to_collection(context, obj, collection_name):
    """
    Adds an object to a specified collection or the scene collection,
    based on the 'custom_light_auto_collection' setting.
    """
    scene = context.scene

    # Unlink from all other collections first to ensure it's only in one place.
    for coll in obj.users_collection[:]:
        coll.objects.unlink(obj)

    if scene.custom_light_auto_collection:
        # Get target parent collection (e.g., "Custom Lights" or user chosen)
        parent_coll = get_target_parent_collection(context)
        
        # Ensure parent collection is active/included in the view layer!
        # This solves the user's logic requirements when the collection is excluded or unactive
        lc = find_layer_collection(context.view_layer.layer_collection, parent_coll)
        if lc:
            lc.exclude = False
            lc.hide_viewport = False
            
        target_collection = create_or_get_collection(parent_coll, collection_name)
        
        # Also ensure sub-collection is active/included
        lc_sub = find_layer_collection(context.view_layer.layer_collection, target_collection)
        if lc_sub:
            lc_sub.exclude = False
            lc_sub.hide_viewport = False
            
        if obj.name not in target_collection.objects:
            target_collection.objects.link(obj)
    else:
        # Auto-collection is OFF: Link directly to the active collection
        target_collection = context.collection
        if obj.name not in target_collection.objects:
            target_collection.objects.link(obj)

    # Make the new object active and selected
    try:
        bpy.ops.object.select_all(action='DESELECT')
        scene["bypass_auto_solo"] = True
        context.view_layer.objects.active = obj
        obj.select_set(True)
    except RuntimeError:
        pass

def get_all_collections(root_collection):
    """Recursively collects all child collections of root_collection."""
    collections = []
    for coll in root_collection.children:
        collections.append(coll)
        collections.extend(get_all_collections(coll))
    return collections

# ---------------------------------------------------
# Light Property Helpers
# ---------------------------------------------------

def setup_light_properties(light_data, type='POINT', energy=1000, color=(1,1,1)):
    """Sets up common light properties."""
    light_data.type = type
    light_data.energy = energy
    light_data.color = color

def blackbody_base(temperature):
    """Calculates the base blackbody color."""
    temperature = max(1000, min(12000, temperature)) / 100.0
    # This is a standard algorithm for blackbody calculation.
    # Red
    if temperature <= 66: red = 255
    else: red = 329.698727446 * ((temperature - 60) ** -0.1332047592)
    # Green
    if temperature <= 66: green = 99.4708025861 * math.log(temperature) - 161.1195681661
    else: green = 288.1221695283 * ((temperature - 60) ** -0.0755148492)
    # Blue
    if temperature >= 66: blue = 255
    elif temperature <= 19: blue = 0
    else: blue = 138.5177312231 * math.log(temperature - 10) - 305.0447927307
    return (max(0, min(255, red))/255.0, max(0, min(255, green))/255.0, max(0, min(255, blue))/255.0)

def adjusted_blackbody_to_rgb(temperature):
    """Calculates an adjusted blackbody color with red/blue multipliers."""
    base_r, base_g, base_b = blackbody_base(temperature)
    if temperature <= 5500:
        red_multiplier = 5 - ((temperature - 1000) / 4500) * 4
    else:
        red_multiplier = 1
    if temperature >= 5500:
        blue_multiplier = 1 + ((temperature - 5500) / 6500) * 0.25
    else:
        blue_multiplier = 1
    return (base_r * red_multiplier, base_g, base_b * blue_multiplier)

# ---------------------------------------------------
# UI and Panel Helpers
# ---------------------------------------------------

def has_emission(obj):
    """Checks if an object is a light or a mesh with an emission shader."""
    if obj.type == 'LIGHT':
        return True # All lights are considered to have emission for this addon's purpose
    if obj.type == 'MESH' and obj.data.materials:
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'EMISSION':
                        return True
    return False

def get_mesh_emission_control(obj):
    """Gets the color socket from a mesh's emission material."""
    if obj.type == 'MESH' and obj.data.materials:
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'EMISSION':
                        color_socket = node.inputs.get("Color")
                        return color_socket
    return None

def get_mesh_emission_strength_control(obj):
    """Gets the strength socket from a mesh's emission material, handling MATH nodes."""
    if obj.type == 'MESH' and obj.data.materials:
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'EMISSION':
                        strength_socket = node.inputs.get("Strength")
                        if strength_socket:
                            if strength_socket.is_linked:
                                for link in strength_socket.links:
                                    if link.from_node.type == 'MATH':
                                        math_node = link.from_node
                                        # Prefer the unconnected socket for control
                                        if not math_node.inputs[1].is_linked:
                                            return math_node.inputs[1]
                                        if not math_node.inputs[0].is_linked:
                                            return math_node.inputs[0]
                                        return None # Both are linked, no simple control
                            else:
                                return strength_socket
    return None

def is_collection_active(coll):
    """Checks if any object in a collection is selected."""
    for obj in coll.all_objects:
        if obj.select_get():
            return True
    return False

def is_managed_light(obj):
    """
    Checks if an object should be displayed in the Manage Lights panel,
    replicating the original addon's more restrictive filtering logic.
    """
    # The object must have a light source (be a LIGHT or have an emission shader)
    if not has_emission(obj):
        return False

    # All standard LIGHT objects are included
    if obj.type == 'LIGHT':
        return True

    # For MESH objects, only include them if they follow specific naming conventions
    if obj.type == 'MESH':
        if "Light_Plane" in obj.name or obj.name.startswith("L."):
            return True
            
    return False

# ---------------------------------------------------
# Handlers and Update Functions
# ---------------------------------------------------

def update_spot_power(self, context):
    """Update function for the God Rays operator's power property."""
    obj = context.active_object
    if obj and obj.type == 'LIGHT':
        obj.data.energy = self.spot_power

def update_emission_color(scene, depsgraph=None):
    """Handler to sync a spotlight's emission node color with its data.color."""
    if not depsgraph:
        return
        
    for update in depsgraph.updates:
        id_data = update.id
        light = None
        if isinstance(id_data, bpy.types.Light):
            light = id_data
        elif isinstance(id_data, bpy.types.Object) and id_data.type == 'LIGHT':
            light = id_data.data
            
        if light and light.type == 'SPOT' and light.use_nodes:
            nt = light.node_tree
            if nt:
                for node in nt.nodes:
                    if node.type == 'EMISSION':
                        # Sync color
                        node.inputs["Color"].default_value = (*light.color, 1)
                        break

_last_active_obj_name = None

def run_auto_solo_timer():
    try:
        context = bpy.context
        if not context or not hasattr(context, "scene") or not context.scene:
            return None
        scene = context.scene
        
        # Check if we should bypass auto solo
        if scene.get("bypass_auto_solo", False):
            scene["bypass_auto_solo"] = False
            return None
            
        active_obj = context.active_object
        
        # Check if the active object is a managed light
        if active_obj and is_managed_light(active_obj):
            if scene.custom_light_solo_active and scene.custom_light_solo_light != active_obj.name:
                toggle_solo_light(scene, active_obj)
        else:
            if scene.custom_light_solo_active:
                restore_light_visibility(scene)
    except Exception as e:
        print(f"Error in auto solo timer: {e}")
    return None

def auto_solo_handler(scene, depsgraph=None):
    global _last_active_obj_name
    
    context = bpy.context
    if not context or not hasattr(context, "view_layer"):
        return
        
    active_obj = context.view_layer.objects.active
    active_name = active_obj.name if active_obj else None
    
    if active_name != _last_active_obj_name:
        _last_active_obj_name = active_name
        # Schedule the update outside the depsgraph evaluation context
        if not bpy.app.timers.is_registered(run_auto_solo_timer):
            bpy.app.timers.register(run_auto_solo_timer, first_interval=0.01)




def get_world_background_node(world):
    """Gets the Background node from the world's node tree."""
    if world and world.use_nodes and world.node_tree:
        for node in world.node_tree.nodes:
            if node.type == 'BACKGROUND':
                return node
    return None

# ---------------------------------------------------
# Collection Brightness Helpers
# ---------------------------------------------------

def get_light_energy(obj):
    """Get energy/strength value for a light or emission mesh."""
    if obj.type == 'LIGHT':
        return obj.data.energy
    elif obj.type == 'MESH':
        strength_socket = get_mesh_emission_strength_control(obj)
        if strength_socket:
            return strength_socket.default_value
    return None

def set_light_energy(obj, value):
    """Set energy/strength value for a light or emission mesh."""
    if obj.type == 'LIGHT':
        obj.data.energy = value
        return True
    elif obj.type == 'MESH':
        strength_socket = get_mesh_emission_strength_control(obj)
        if strength_socket:
            strength_socket.default_value = value
            return True
    return False

def store_base_energy(obj):
    """Store current energy as base value in custom property."""
    energy = get_light_energy(obj)
    if energy is not None:
        obj["_base_energy"] = energy
        return True
    return False

def get_base_energy(obj):
    """Retrieve stored base energy value, or current energy if not stored."""
    if "_base_energy" in obj:
        return obj["_base_energy"]
    # If not stored, return current energy
    return get_light_energy(obj)

def apply_collection_brightness(coll, multiplier):
    """Apply brightness multiplier to all lights in a collection.
    Detects individual light changes and updates their base before applying.
    """
    # Get the last multiplier for this collection
    last_mult = coll.get("_last_multiplier", 1.0)
    
    for obj in coll.objects:
        if not is_managed_light(obj):
            continue
        
        current = get_light_energy(obj)
        if current is None:
            continue
        
        # Initialize base if not exists
        if "_base_energy" not in obj:
            base = current / last_mult if last_mult > 0 else current
            obj["_base_energy"] = base
        else:
            base = obj["_base_energy"]
        
        # Check if user manually changed this light
        expected = base * last_mult
        if abs(current - expected) > 0.001:
            # User changed this light individually, calculate new relative base
            base = current / last_mult if last_mult > 0 else current
            obj["_base_energy"] = base
        
        # Apply multiplier from base
        new_value = base * multiplier
        set_light_energy(obj, new_value)
    
    # Store current multiplier for next comparison
    coll["_last_multiplier"] = multiplier


# ---------------------------------------------------
# View Layer and Collection State Helpers
# ---------------------------------------------------

def find_layer_collection(layer_collection, collection):
    """Recursively find the layer collection corresponding to a collection."""
    if layer_collection.collection == collection:
        return layer_collection
    for child in layer_collection.children:
        found = find_layer_collection(child, collection)
        if found:
            return found
    return None

def is_collection_excluded(context, collection):
    """Checks if a collection is excluded in the active view layer."""
    lc = find_layer_collection(context.view_layer.layer_collection, collection)
    if lc:
        return lc.exclude
    return False


# ---------------------------------------------------
# Solo / Isolate Light Helpers
# ---------------------------------------------------

def get_all_managed_lights(scene):
    """Gets all managed light objects in the scene."""
    all_lights = []
    for obj in scene.objects:
        if is_managed_light(obj):
            all_lights.append(obj)
    return all_lights

def toggle_solo_light(scene, target_obj):
    """Toggles solo mode for a specific light object."""
    if scene.custom_light_solo_active and scene.custom_light_solo_light == target_obj.name:
        restore_light_visibility(scene)
    else:
        if scene.custom_light_solo_active:
            restore_light_visibility(scene)
            
        all_lights = get_all_managed_lights(scene)
        for obj in all_lights:
            if obj == target_obj:
                continue
            obj["_prev_hide_viewport"] = obj.hide_viewport
            obj["_prev_hide_render"] = obj.hide_render
            obj["_prev_hide_get"] = obj.hide_get()
            
            obj.hide_viewport = True
            obj.hide_render = True
            obj.hide_set(True)
            
        target_obj.hide_viewport = False
        target_obj.hide_render = False
        target_obj.hide_set(False)
        
        scene.custom_light_solo_active = True
        scene.custom_light_solo_light = target_obj.name
        
        # Force dependency graph / viewport update
        bpy.context.view_layer.update()

def restore_light_visibility(scene):
    """Restores the previous visibility states of all lights."""
    all_lights = get_all_managed_lights(scene)
    for obj in all_lights:
        if "_prev_hide_viewport" in obj:
            obj.hide_viewport = obj["_prev_hide_viewport"]
            del obj["_prev_hide_viewport"]
        if "_prev_hide_render" in obj:
            obj.hide_render = obj["_prev_hide_render"]
            del obj["_prev_hide_render"]
        if "_prev_hide_get" in obj:
            obj.hide_set(obj["_prev_hide_get"])
            del obj["_prev_hide_get"]
            
    scene.custom_light_solo_active = False
    scene.custom_light_solo_light = ""
    
    # Force dependency graph / viewport update
    bpy.context.view_layer.update()


# ---------------------------------------------------
# Gobo Node Parameter Helpers
# ---------------------------------------------------

def find_node_by_type(node_tree, node_type):
    """Finds a node of a specific type in a node tree, recursively checking groups."""
    if not node_tree:
        return None
    for node in node_tree.nodes:
        # Check by type, bl_idname, or custom check for color ramp
        if node_type in ('VAL_TO_RGB', 'VALTORGB'):
            if node.type in ('VAL_TO_RGB', 'VALTORGB') or node.bl_idname == 'ShaderNodeValToRGB' or isinstance(getattr(node, 'color_ramp', None), bpy.types.ColorRamp):
                return node
        else:
            if node.type == node_type or node.bl_idname == node_type:
                return node
                
        # Recursively check groups
        if hasattr(node, "node_tree") and node.node_tree:
            found = find_node_by_type(node.node_tree, node_type)
            if found:
                return found
    return None

def get_gobo_nodes(obj):
    """
    Returns a dictionary of key nodes in a gobo light or mesh object,
    or in its children if the object itself is not a gobo.
    Only returns the dictionary if a ColorRamp (VAL_TO_RGB) node is present.
    """
    def extract_gobo_nodes(node_tree):
        if not node_tree:
            return None
        
        color_ramp = find_node_by_type(node_tree, 'VAL_TO_RGB')
        if not color_ramp:
            return None
            
        return {
            'noise': find_node_by_type(node_tree, 'TEX_NOISE'),
            'voronoi': find_node_by_type(node_tree, 'TEX_VORONOI'),
            'wave': find_node_by_type(node_tree, 'TEX_WAVE'),
            'image': find_node_by_type(node_tree, 'TEX_IMAGE'),
            'color_ramp': color_ramp,
            'mapping': find_node_by_type(node_tree, 'MAPPING'),
            'emission': find_node_by_type(node_tree, 'EMISSION'),
            'node_tree': node_tree
        }

    # 1. Check the object itself
    if obj.type == 'LIGHT' and obj.data.use_nodes:
        res = extract_gobo_nodes(obj.data.node_tree)
        if res:
            return res
    elif obj.type == 'MESH':
        mat = obj.active_material
        if not mat and hasattr(obj.data, "materials") and obj.data.materials:
            mat = obj.data.materials[0]
        if mat and mat.use_nodes:
            res = extract_gobo_nodes(mat.node_tree)
            if res:
                return res

    # 2. Check the children of the object (e.g. parented plane gobo)
    for child in obj.children:
        if child.type == 'LIGHT' and child.data.use_nodes:
            res = extract_gobo_nodes(child.data.node_tree)
            if res:
                return res
        elif child.type == 'MESH':
            mat = child.active_material
            if not mat and hasattr(child.data, "materials") and child.data.materials:
                mat = child.data.materials[0]
            if mat and mat.use_nodes:
                res = extract_gobo_nodes(mat.node_tree)
                if res:
                    return res

    return None


def get_or_create_world_mapping_node(world):
    """Gets or creates the Mapping and Texture Coordinate nodes for the world's Environment Texture."""
    if not world or not world.use_nodes or not world.node_tree:
        return None
        
    nt = world.node_tree
    
    # 1. Find the Mapping node if it exists
    for node in nt.nodes:
        if node.type == 'MAPPING':
            return node
            
    # 2. If not, find the Environment Texture node
    env_tex = None
    for node in nt.nodes:
        if node.type == 'TEX_ENVIRONMENT':
            env_tex = node
            break
            
    if env_tex:
        # Create Mapping node
        mapping = nt.nodes.new(type='ShaderNodeMapping')
        mapping.location = (env_tex.location[0] - 200, env_tex.location[1])
        
        # Link Mapping to Env Tex
        nt.links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
        
        # Create Texture Coordinate node
        tex_coord = next((n for n in nt.nodes if n.type == 'TEX_COORD'), None)
        if not tex_coord:
            tex_coord = nt.nodes.new(type='ShaderNodeTexCoord')
            tex_coord.location = (mapping.location[0] - 200, mapping.location[1])
            
        # Link Generated to Vector
        nt.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
        return mapping
        
    return None