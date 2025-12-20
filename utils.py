import bpy
import math
import bmesh
from mathutils import Vector

# ---------------------------------------------------
# Collection and Object Helpers
# ---------------------------------------------------

def create_or_get_collection(parent_collection, collection_name):
    """Creates a new collection or gets an existing one."""
    if collection_name in parent_collection.children:
        return parent_collection.children[collection_name]
    else:
        new_collection = bpy.data.collections.new(collection_name)
        parent_collection.children.link(new_collection)
        return new_collection

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
        # Auto-collection is ON: Create "Custom Lights" -> sub-collection structure
        root_coll = create_or_get_collection(scene.collection, "Custom Lights")
        target_collection = create_or_get_collection(root_coll, collection_name)
        if obj.name not in target_collection.objects:
            target_collection.objects.link(obj)
    else:
        # Auto-collection is OFF: Link directly to the scene collection
        if obj.name not in scene.collection.objects:
            scene.collection.objects.link(obj)

    # Make the new object active and selected
    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = obj
    obj.select_set(True)

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

def update_emission_color(scene):
    """Handler to sync a spotlight's emission node color with its data.color."""
    # Using bpy.context.scene is more reliable in handlers
    if not bpy.context.scene:
        return
        
    for obj in bpy.context.scene.objects:
        if obj.type == 'LIGHT' and obj.data.type == 'SPOT' and obj.data.use_nodes:
            nt = obj.data.node_tree
            if nt:
                for node in nt.nodes:
                    if node.type == 'EMISSION':
                        # Sync color
                        node.inputs["Color"].default_value = (*obj.data.color, 1)
                        break

# Storage for tracking previous multiplier values
_prev_brightness_multipliers = {}

def update_collection_brightness(scene):
    """Handler to apply brightness multiplier when it changes."""
    if not bpy.context.scene:
        return
    
    # Check scene collection
    scene_coll = bpy.context.scene.collection
    _check_and_apply_brightness(scene_coll, "MASTER")
    
    # Check all other collections
    for coll in get_all_collections(scene_coll):
        _check_and_apply_brightness(coll, coll.name)

def _check_and_apply_brightness(coll, coll_key):
    """Check if multiplier changed and apply if so."""
    global _prev_brightness_multipliers
    
    current = coll.get("brightness_multiplier", 1.0)
    prev = _prev_brightness_multipliers.get(coll_key, 1.0)
    
    if abs(current - prev) > 0.0001:  # Changed
        _prev_brightness_multipliers[coll_key] = current
        apply_collection_brightness(coll, current)

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
            obj["_base_energy"] = current
        
        base = obj.get("_base_energy", current)
        
        # Check if user manually changed this light
        expected = base * last_mult
        if abs(current - expected) > 0.001:
            # User changed this light individually, update its base
            obj["_base_energy"] = current
            base = current
        
        # Apply multiplier from base
        new_value = base * multiplier
        set_light_energy(obj, new_value)
    
    # Store current multiplier for next comparison
    coll["_last_multiplier"] = multiplier