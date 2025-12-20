import bpy
import math
import bmesh
import os
from mathutils import Vector
from .. import utils

class LIGHTING_OT_AddTrackerLights(bpy.types.Operator):
    """Add a customizable tracker lighting setup."""
    bl_idname = "lighting.add_tracker_lights"
    bl_label = "Tracker Lights"
    bl_options = {'REGISTER', 'UNDO'}

    num_lights: bpy.props.IntProperty(name="Number of Lights", default=1, min=1, max=10)
    light_intensity: bpy.props.FloatProperty(name="Light Intensity (W)", default=30)
    light_distance: bpy.props.FloatProperty(name="Light Distance", default=5)
    light_width: bpy.props.FloatProperty(name="Light Width", default=1)
    light_height: bpy.props.FloatProperty(name="Light Height", default=1)
    light_color: bpy.props.FloatVectorProperty(name="Light Color", subtype='COLOR', size=3, default=(1.0, 1.0, 1.0), min=0, max=1)

    def execute(self, context):
        target = context.active_object
        if not target:
            self.report({'WARNING'}, "No target object selected!")
            return {'CANCELLED'}
        center = target.location
        collection_name = "Tracker Lights"

        empty = bpy.data.objects.new("Light_Target", None)
        empty.empty_display_type = 'PLAIN_AXES'
        empty.empty_display_size = max(target.dimensions) * 1.5 if max(target.dimensions) > 0 else 1.0
        empty.location = center
        empty.rotation_euler = target.rotation_euler
        utils.add_object_to_collection(context, empty, collection_name)

        empty.parent = target

        for i in range(self.num_lights):
            angle = (i / self.num_lights) * math.pi * 2
            x = center.x + self.light_distance * math.cos(angle)
            y = center.y + self.light_distance * math.sin(angle)
            z = center.z + (self.light_distance / 2 if self.num_lights > 1 else self.light_distance)

            light_data = bpy.data.lights.new(name=f"Light_{i+1}", type='AREA')
            utils.setup_light_properties(light_data, type='AREA', energy=self.light_intensity, color=self.light_color)
            light_data.shape = 'RECTANGLE'
            light_data.size = self.light_width
            light_data.size_y = self.light_height

            light_object = bpy.data.objects.new(name=f"Light_{i+1}", object_data=light_data)
            light_object.location = (x, y, z)
            light_object.rotation_euler = (math.radians(-45), 0, angle + math.pi)
            utils.add_object_to_collection(context, light_object, collection_name)

            constraint = light_object.constraints.new(type='TRACK_TO')
            constraint.target = empty
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'

        context.view_layer.objects.active = empty
        empty.select_set(True)
        self.report({'INFO'}, f"Added {self.num_lights} Tracker Lights!")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "num_lights")
        layout.prop(self, "light_intensity")
        layout.prop(self, "light_distance")
        layout.prop(self, "light_width")
        layout.prop(self, "light_height")
        layout.prop(self, "light_color")

class LIGHTING_OT_AddLinearGradientPlane(bpy.types.Operator):
    """Create a linear gradient light plane."""
    bl_idname = "lighting.add_linear_gradient_plane"
    bl_label = "Linear Gradient Plane"
    bl_options = {'REGISTER', 'UNDO'}

    emission_color: bpy.props.FloatVectorProperty(name="Emission Color", subtype='COLOR', size=4, default=(1.0, 1.0, 1.0, 1.0))
    plane_width: bpy.props.FloatProperty(name="Plane Width", default=2.0, min=0.1)
    plane_length: bpy.props.FloatProperty(name="Plane Length", default=2.0, min=0.1)
    strength: bpy.props.FloatProperty(name="Strength", default=1.0, min=0.0)
    flip: bpy.props.BoolProperty(name="Flip ColorRamp", default=False)
    rotate: bpy.props.BoolProperty(name="Rotate", default=False)
    camera_visibility: bpy.props.BoolProperty(name="Ray Camera Visibility", default=True)
    transparent_black: bpy.props.BoolProperty(name="Transparent Black Gradient", default=False,
        description="Make black parts of gradient transparent")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "emission_color")
        layout.prop(self, "flip")
        layout.prop(self, "rotate")
        layout.prop(self, "plane_width")
        layout.prop(self, "plane_length")
        layout.prop(self, "strength")
        layout.prop(self, "camera_visibility")
        layout.prop(self, "transparent_black")

    def execute(self, context):
        bpy.ops.mesh.primitive_plane_add(align='WORLD', location=context.scene.cursor.location)
        plane_obj = context.active_object
        plane_obj.name = "Linear_Gradient_Plane"
        plane_obj.scale.x = self.plane_width
        plane_obj.scale.y = self.plane_length

        mat = bpy.data.materials.new(name="LinearGradient_Mat")
        mat.use_nodes = True
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links
        for node in list(nodes): nodes.remove(node)

        tex_coord = nodes.new(type="ShaderNodeTexCoord")
        mapping = nodes.new(type="ShaderNodeMapping")
        separate_xyz = nodes.new(type="ShaderNodeSeparateXYZ")
        gradient = nodes.new(type="ShaderNodeTexGradient")
        color_ramp = nodes.new(type="ShaderNodeValToRGB")
        
        try:
            luminance_node = nodes.new(type="ShaderNodeRGBToBW")
            luminance_output_name = "Val"
        except Exception:
            luminance_node = nodes.new(type="ShaderNodeSeparateRGB")
            luminance_output_name = "R"

        math_node = nodes.new(type="ShaderNodeMath")
        emission = nodes.new(type="ShaderNodeEmission")
        mat_output = nodes.new(type="ShaderNodeOutputMaterial")

        color_ramp.color_ramp.interpolation = 'EASE'
        math_node.operation = 'MULTIPLY'
        math_node.inputs[1].default_value = self.strength
        emission.inputs["Color"].default_value = self.emission_color
        gradient.gradient_type = 'EASING'

        links.new(tex_coord.outputs["UV"], mapping.inputs[0])
        links.new(mapping.outputs[0], separate_xyz.inputs[0])
        
        if self.rotate:
            links.new(separate_xyz.outputs["Y"], gradient.inputs[0])
        else:
            links.new(separate_xyz.outputs["X"], gradient.inputs[0])
        
        links.new(gradient.outputs["Fac"], color_ramp.inputs["Fac"])
        
        if not self.flip:
            color_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
            color_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
        else:
            color_ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
            color_ramp.color_ramp.elements[1].color = (0, 0, 0, 1)

        links.new(color_ramp.outputs["Color"], luminance_node.inputs[0])
        links.new(luminance_node.outputs[luminance_output_name], math_node.inputs[0])
        links.new(math_node.outputs["Value"], emission.inputs["Strength"])

        if self.transparent_black:
            # Add Transparent BSDF and Mix Shader
            transparent = nodes.new(type="ShaderNodeBsdfTransparent")
            mix_shader = nodes.new(type="ShaderNodeMixShader")
            # Color from ColorRamp drives mix factor (black=0=transparent, white=1=emission)
            links.new(color_ramp.outputs["Color"], mix_shader.inputs["Fac"])
            links.new(transparent.outputs["BSDF"], mix_shader.inputs[1])
            links.new(emission.outputs["Emission"], mix_shader.inputs[2])
            links.new(mix_shader.outputs["Shader"], mat_output.inputs["Surface"])
        else:
            links.new(emission.outputs["Emission"], mat_output.inputs["Surface"])
        
        plane_obj.data.materials.append(mat)
        plane_obj.visible_camera = self.camera_visibility
        utils.add_object_to_collection(context, plane_obj, "Gradient Light Planes")
        self.report({'INFO'}, "Linear Gradient Plane Added!")
        return {'FINISHED'}


class LIGHTING_OT_AddSphereGradientPlane(bpy.types.Operator):
    """Create a spherical gradient light plane."""
    bl_idname = "lighting.add_sphere_gradient_plane"
    bl_label = "Sphere Gradient Plane"
    bl_options = {'REGISTER', 'UNDO'}

    emission_color: bpy.props.FloatVectorProperty(name="Emission Color", subtype='COLOR', size=4, default=(1.0, 1.0, 1.0, 1.0))
    plane_width: bpy.props.FloatProperty(name="Plane Width", default=2.0, min=0.1)
    plane_length: bpy.props.FloatProperty(name="Plane Length", default=2.0, min=0.1)
    strength: bpy.props.FloatProperty(name="Strength", default=1.0, min=0.0)
    camera_visibility: bpy.props.BoolProperty(name="Ray Camera Visibility", default=True)
    transparent_black: bpy.props.BoolProperty(name="Transparent Black Gradient", default=False,
        description="Make black parts of gradient transparent")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "emission_color")
        layout.prop(self, "plane_width")
        layout.prop(self, "plane_length")
        layout.prop(self, "strength")
        layout.prop(self, "camera_visibility")
        layout.prop(self, "transparent_black")

    def execute(self, context):
        bpy.ops.mesh.primitive_plane_add(align='WORLD', location=context.scene.cursor.location)
        plane_obj = context.active_object
        plane_obj.name = "Sphere_Gradient_Plane"
        plane_obj.scale.x = self.plane_width
        plane_obj.scale.y = self.plane_length

        mat = bpy.data.materials.new(name="SphereGradient_Mat")
        mat.use_nodes = True
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links
        for node in list(nodes): nodes.remove(node)

        tex_coord = nodes.new(type="ShaderNodeTexCoord")
        mapping = nodes.new(type="ShaderNodeMapping")
        gradient = nodes.new(type="ShaderNodeTexGradient")
        color_ramp = nodes.new(type="ShaderNodeValToRGB")
        
        try:
            luminance_node = nodes.new(type="ShaderNodeRGBToBW")
            luminance_output_name = "Val"
        except Exception:
            luminance_node = nodes.new(type="ShaderNodeSeparateRGB")
            luminance_output_name = "R"

        math_node = nodes.new(type="ShaderNodeMath")
        emission = nodes.new(type="ShaderNodeEmission")
        mat_output = nodes.new(type="ShaderNodeOutputMaterial")

        color_ramp.color_ramp.interpolation = 'EASE'
        math_node.operation = 'MULTIPLY'
        math_node.inputs[1].default_value = self.strength
        emission.inputs["Color"].default_value = self.emission_color
        
        # Spherical gradient setup
        mapping.inputs["Location"].default_value = (-0.5, -0.5, 0)
        gradient.gradient_type = 'SPHERICAL'

        links.new(tex_coord.outputs["UV"], mapping.inputs[0])
        links.new(mapping.outputs[0], gradient.inputs[0])
        links.new(gradient.outputs["Fac"], color_ramp.inputs["Fac"])
        
        color_ramp.color_ramp.elements[0].position = 0.5
        color_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
        color_ramp.color_ramp.elements[1].position = 1.0
        color_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)

        links.new(color_ramp.outputs["Color"], luminance_node.inputs[0])
        links.new(luminance_node.outputs[luminance_output_name], math_node.inputs[0])
        links.new(math_node.outputs["Value"], emission.inputs["Strength"])

        if self.transparent_black:
            # Add Transparent BSDF and Mix Shader
            transparent = nodes.new(type="ShaderNodeBsdfTransparent")
            mix_shader = nodes.new(type="ShaderNodeMixShader")
            # Color from ColorRamp drives mix factor (black=0=transparent, white=1=emission)
            links.new(color_ramp.outputs["Color"], mix_shader.inputs["Fac"])
            links.new(transparent.outputs["BSDF"], mix_shader.inputs[1])
            links.new(emission.outputs["Emission"], mix_shader.inputs[2])
            links.new(mix_shader.outputs["Shader"], mat_output.inputs["Surface"])
        else:
            links.new(emission.outputs["Emission"], mat_output.inputs["Surface"])
        
        plane_obj.data.materials.append(mat)
        plane_obj.visible_camera = self.camera_visibility
        utils.add_object_to_collection(context, plane_obj, "Gradient Light Planes")
        self.report({'INFO'}, "Sphere Gradient Plane Added!")
        return {'FINISHED'}

class LIGHTING_OT_AddTranslucentLight(bpy.types.Operator):
    """Add a translucent light plane based on the active light."""
    bl_idname = "lighting.add_translucent_light"
    bl_label = "Translucent Light Plane"
    bl_options = {'REGISTER', 'UNDO'}

    plane_color: bpy.props.FloatVectorProperty(name="Plane Color", subtype='COLOR', size=3, default=(1.0, 1.0, 1.0), min=0.0, max=1.0)
    distance: bpy.props.FloatProperty(name="Distance Offset", default=0.2, min=0.0)
    camera_visibility: bpy.props.BoolProperty(name="Visible to Camera", default=False)

    def invoke(self, context, event):
        active = context.active_object
        if not active or active.type != 'LIGHT':
            self.report({'WARNING'}, "Please select an active light!")
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        active = context.active_object
        depsgraph = context.evaluated_depsgraph_get()
        active_eval = active.evaluated_get(depsgraph)
        light_loc = active_eval.matrix_world.translation.copy()
        light_rot = active_eval.matrix_world.to_euler()

        bpy.ops.mesh.primitive_plane_add(location=light_loc, rotation=light_rot)
        plane = context.active_object

        if active.data.type == 'AREA':
            scale_x = active.data.size * 1.5
            scale_y = active.data.size_y * 1.5
        else:
            scale_x = scale_y = 1.5
        plane.scale = (scale_x, scale_y, 1)

        local_z = plane.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        plane.location = light_loc + (local_z * self.distance)

        mat = bpy.data.materials.new(name="Translucent_Light_Mat")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        output_node = nodes.new(type="ShaderNodeOutputMaterial")
        translucent_node = nodes.new(type="ShaderNodeBsdfTranslucent")
        translucent_node.inputs["Color"].default_value = (*self.plane_color, 1)
        links.new(translucent_node.outputs["BSDF"], output_node.inputs["Surface"])
        
        if plane.data.materials: plane.data.materials[0] = mat
        else: plane.data.materials.append(mat)

        plane.visible_camera = self.camera_visibility
        
        plane.parent = active
        plane.matrix_parent_inverse = active.matrix_world.inverted()
        utils.add_object_to_collection(context, plane, "Translucent Planes")
        return {'FINISHED'}

class LIGHTING_OT_AddSimpleGodRays(bpy.types.Operator):
    """Add simple god rays to the selected light."""
    bl_idname = "lighting.add_simple_god_rays"
    bl_label = "Add Simple God Rays"
    bl_options = {'REGISTER', 'UNDO'}

    spot_power: bpy.props.FloatProperty(name="Spotlight Power", default=1000, min=0.0, update=utils.update_spot_power)
    noise_scale: bpy.props.FloatProperty(name="Noise Scale", default=5.0, min=0.1)
    light_color: bpy.props.FloatVectorProperty(name="Light Color", subtype='COLOR', size=3, default=(1.0, 1.0, 1.0), min=0.0, max=1.0)
    cone_height: bpy.props.FloatProperty(name="Cone Height", default=5.0, min=0.1)
    volume_color: bpy.props.FloatVectorProperty(name="Volume Color", subtype='COLOR', size=3, default=(1.0, 1.0, 1.0), min=0.0, max=1.0)
    volume_density: bpy.props.FloatProperty(name="Volume Density", default=0.1, min=0.0)

    def invoke(self, context, event):
        active = context.active_object
        if not active:
            self.report({'WARNING'}, "Please select a light object.")
            return {'CANCELLED'}
        if active.type != 'LIGHT':
            self.report({'WARNING'}, "Selected object is not a light.")
            return {'CANCELLED'}
        active.data.type = 'SPOT'
        return self.execute(context)

    def execute(self, context):
        spotlight = context.active_object
        if spotlight.data.type != 'SPOT':
            spotlight.data.type = 'SPOT'
        
        spotlight.data.energy = self.spot_power
        spotlight.data.color = self.light_color
        spot_angle = spotlight.data.spot_size

        depsgraph = context.evaluated_depsgraph_get()
        spotlight_eval = spotlight.evaluated_get(depsgraph)
        light_loc = spotlight_eval.matrix_world.translation.copy()
        light_rot = spotlight_eval.matrix_world.to_euler()

        spotlight.data.use_nodes = True
        nt = spotlight.data.node_tree
        nodes = nt.nodes
        links = nt.links
        for node in list(nodes): nodes.remove(node)
        
        # Create and configure nodes
        tex_coord = nodes.new(type="ShaderNodeTexCoord")
        mapping = nodes.new(type="ShaderNodeMapping")
        noise = nodes.new(type="ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = self.noise_scale
        color_ramp = nodes.new(type="ShaderNodeValToRGB")
        color_ramp.color_ramp.elements[0].position = 0.5
        color_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
        color_ramp.color_ramp.elements[1].position = 1.0
        color_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
        # Use RGBToBW to obtain a single luminance value from color output
        # Fall back to SeparateRGB if RGBToBW is not present on this build.
        try:
            luminance_node = nodes.new(type="ShaderNodeRGBToBW")
            luminance_output_name = "Val"
        except Exception:
            luminance_node = nodes.new(type="ShaderNodeSeparateRGB")
            luminance_output_name = "R"

        math_node = nodes.new(type="ShaderNodeMath")
        math_node.operation = 'MULTIPLY'
        math_node.inputs[1].default_value = 1.0
        emission = nodes.new(type="ShaderNodeEmission")
        emission.inputs["Color"].default_value = (*self.light_color, 1)
        output = nodes.new(type="ShaderNodeOutputLight")

        # Link nodes
        links.new(tex_coord.outputs["Normal"], mapping.inputs[0])
        links.new(mapping.outputs[0], noise.inputs[0])
        links.new(noise.outputs["Fac"], color_ramp.inputs[0])
        links.new(color_ramp.outputs["Color"], luminance_node.inputs[0])
        links.new(luminance_node.outputs[luminance_output_name], math_node.inputs[0])
        links.new(math_node.outputs["Value"], emission.inputs["Strength"])
        links.new(emission.outputs["Emission"], output.inputs["Surface"])
        
        # Create and setup cone
        bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=1, depth=2, location=light_loc, rotation=light_rot)
        cone_obj = context.active_object
        cone_obj.name = f"{spotlight.name}_GodRaysCone"
        
        bm = bmesh.new()
        bm.from_mesh(cone_obj.data)
        top_vert = max(bm.verts, key=lambda v: v.co.z)
        bmesh.ops.translate(bm, verts=bm.verts, vec=-top_vert.co.copy())
        bm.to_mesh(cone_obj.data)
        bm.free()
        cone_obj.location = light_loc.copy()
        cone_obj.rotation_euler = light_rot.copy()
        
        width = 2 * (self.cone_height * math.tan(spot_angle / 2.0))
        cone_obj.scale = (width, width, self.cone_height)
        
        # Setup volume material
        vol_mat = bpy.data.materials.get("Volume_Scatter_Mat")
        if not vol_mat:
            vol_mat = bpy.data.materials.new(name="Volume_Scatter_Mat")
            vol_mat.use_nodes = True
            vol_nodes = vol_mat.node_tree.nodes
            vol_links = vol_mat.node_tree.links
            for node in list(vol_nodes): vol_nodes.remove(node)
            vol_output = vol_nodes.new(type="ShaderNodeOutputMaterial")
            vol_scatter = vol_nodes.new(type="ShaderNodeVolumeScatter")
            vol_scatter.inputs["Color"].default_value = (*self.volume_color, 1)
            vol_scatter.inputs["Density"].default_value = self.volume_density
            vol_links.new(vol_scatter.outputs["Volume"], vol_output.inputs["Volume"])
        
        if cone_obj.data.materials: cone_obj.data.materials[0] = vol_mat
        else: cone_obj.data.materials.append(vol_mat)
        
        cone_obj.parent = spotlight
        cone_obj.matrix_parent_inverse = spotlight.matrix_world.inverted()
        utils.add_object_to_collection(context, cone_obj, "God Rays")
        return {'FINISHED'}

class LIGHTING_OT_ImportDomeLight(bpy.types.Operator):
    """Import Dome Light from DOME_light.blend"""
    bl_idname = "lighting.import_dome_light"
    bl_label = "Import Dome Light"
    bl_options = {'REGISTER', 'UNDO'}

    dome_size: bpy.props.FloatProperty(name="Dome Size", default=10.0, min=0.1, description="Dome diameter")
    hdri_image: bpy.props.StringProperty(name="HDRI Image", subtype='FILE_PATH')
    env_location: bpy.props.FloatVectorProperty(name="Env Location", subtype='XYZ', size=3)
    strength: bpy.props.FloatProperty(name="Env Light Strength", default=1.0)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "dome_size")
        layout.prop(self, "hdri_image")
        layout.prop(self, "env_location")
        layout.prop(self, "strength")

    def execute(self, context):
        addon_dir = os.path.dirname(os.path.dirname(__file__))
        filepath = os.path.join(addon_dir, "DOME_light.blend")
        
        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"Library file not found: {filepath}")
            return {'CANCELLED'}

        # Import object
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            if "L.DOME_env" in data_from.objects:
                data_to.objects = ["L.DOME_env"]
            else:
                self.report({'ERROR'}, "Object 'L.DOME_env' not found in library.")
                return {'CANCELLED'}
        
        obj = data_to.objects[0]
        if obj:
            # Set uniform scale based on dome_size (diameter)
            scale_factor = self.dome_size / 2.0  # Convert diameter to radius-based scale
            obj.scale = (scale_factor, scale_factor, scale_factor)
            
            # Add to collection (respects auto-collection setting)
            utils.add_object_to_collection(context, obj, "Dome Lights")
            
            # Update Material
            if obj.data.materials:
                mat = obj.data.materials[0]
                if mat and mat.use_nodes:
                    nodes = mat.node_tree.nodes
                    
                    # HDRI Image
                    env_tex_node = next((n for n in nodes if n.type == 'TEX_ENVIRONMENT'), None)
                    if env_tex_node and self.hdri_image:
                        try:
                            img = bpy.data.images.load(self.hdri_image, check_existing=True)
                            env_tex_node.image = img
                        except Exception as e:
                            self.report({'WARNING'}, f"Could not load image: {e}")

                    # Mapping Location
                    mapping_node = next((n for n in nodes if n.type == 'MAPPING'), None)
                    if mapping_node:
                        loc_input = mapping_node.inputs.get("Location")
                        if loc_input:
                            loc_input.default_value = self.env_location
                    
                    # Emission Strength
                    emission_node = next((n for n in nodes if n.type == 'EMISSION'), None)
                    if emission_node:
                        strength_input = emission_node.inputs.get("Strength")
                        if strength_input:
                            strength_input.default_value = self.strength
            
            return {'FINISHED'}
        return {'CANCELLED'}

class LIGHTING_OT_ImportNoiseGobo(bpy.types.Operator):
    """Import Noise Gobo light from DOME_light.blend"""
    bl_idname = "lighting.import_noise_gobo"
    bl_label = "Import Noise Gobo"
    bl_options = {'REGISTER', 'UNDO'}

    noise_scale: bpy.props.FloatProperty(name="Noise Scale", default=5.0, min=0.1)
    color: bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', size=3, default=(1.0, 1.0, 1.0), min=0.0, max=1.0)
    spread: bpy.props.FloatProperty(name="Spread", default=0.5236, min=0.0, max=3.1416, subtype='ANGLE', unit='ROTATION')
    strength: bpy.props.FloatProperty(name="Strength", default=1.0, min=0.0)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "noise_scale")
        layout.prop(self, "color")
        layout.prop(self, "spread")
        layout.prop(self, "strength")

    def execute(self, context):
        addon_dir = os.path.dirname(os.path.dirname(__file__))
        filepath = os.path.join(addon_dir, "DOME_light.blend")
        
        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"Library file not found: {filepath}")
            return {'CANCELLED'}

        # Use bpy.ops.wm.append to import the object
        bpy.ops.wm.append(
            filepath=os.path.join(filepath, "Object", "Noise_gobo"),
            directory=os.path.join(filepath, "Object") + os.sep,
            filename="Noise_gobo"
        )
        
        # Find the imported object
        obj = bpy.data.objects.get("Noise_gobo")
        if obj:
            # Set location to cursor position
            obj.location = context.scene.cursor.location
            
            # Update light properties
            if obj.type == 'LIGHT' and obj.data:
                # Update Spread (Beam Shape for Area Light)
                # Note: self.spread is already in radians (ANGLE property stores internally as radians)
                if obj.data.type == 'AREA' and hasattr(obj.data, 'spread'):
                    obj.data.spread = self.spread
                
                # Update material nodes
                if obj.data.use_nodes and obj.data.node_tree:
                    nodes = obj.data.node_tree.nodes
                    
                    # Update Noise Scale
                    noise_node = next((n for n in nodes if n.type == 'TEX_NOISE'), None)
                    if noise_node:
                        scale_input = noise_node.inputs.get("Scale")
                        if scale_input:
                            scale_input.default_value = self.noise_scale
                    
                    # Update Emission Color
                    emission_node = next((n for n in nodes if n.type == 'EMISSION'), None)
                    if emission_node:
                        color_input = emission_node.inputs.get("Color")
                        if color_input:
                            color_input.default_value = (*self.color, 1.0)
                    
                    # Update Strength (Math node)
                    math_node = next((n for n in nodes if n.type == 'MATH'), None)
                    if math_node:
                        # Find the value input (usually input 1 for multiply)
                        if len(math_node.inputs) > 1:
                            math_node.inputs[1].default_value = self.strength
            
            # Add to collection (respects auto-collection setting)
            utils.add_object_to_collection(context, obj, "Noise Gobo Lights")
            
            self.report({'INFO'}, "Successfully imported Noise_gobo")
            return {'FINISHED'}
        
        self.report({'ERROR'}, "Failed to import Noise_gobo")
        return {'CANCELLED'}

class LIGHTING_OT_ImportImageGobo(bpy.types.Operator):
    """Import Image Gobo light from DOME_light.blend"""
    bl_idname = "lighting.import_image_gobo"
    bl_label = "Import Image Gobo"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    filter_image: bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    filter_folder: bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    
    spread: bpy.props.FloatProperty(name="Spread", default=0.5236, min=0.0, max=3.1416, subtype='ANGLE', unit='ROTATION')
    strength: bpy.props.FloatProperty(name="Strength", default=1.0, min=0.0)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No image selected")
            return {'CANCELLED'}
            
        addon_dir = os.path.dirname(os.path.dirname(__file__))
        filepath = os.path.join(addon_dir, "DOME_light.blend")
        
        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"Library file not found: {filepath}")
            return {'CANCELLED'}

        # Use bpy.ops.wm.append to import the object
        bpy.ops.wm.append(
            filepath=os.path.join(filepath, "Object", "Image_Gobo"),
            directory=os.path.join(filepath, "Object") + os.sep,
            filename="Image_Gobo"
        )
        
        # Find the imported object
        obj = bpy.data.objects.get("Image_Gobo")
        if obj:
            # Set location to cursor position
            obj.location = context.scene.cursor.location
            
            # Update light properties
            if obj.type == 'LIGHT' and obj.data:
                # Update Spread (Beam Shape for Area Light)
                # Note: self.spread is already in radians (ANGLE property stores internally as radians)
                if obj.data.type == 'AREA' and hasattr(obj.data, 'spread'):
                    obj.data.spread = self.spread
                
                # Update material nodes
                if obj.data.use_nodes and obj.data.node_tree:
                    nodes = obj.data.node_tree.nodes
                    
                    # Update Image Texture
                    image_node = next((n for n in nodes if n.type == 'TEX_IMAGE'), None)
                    if image_node and self.filepath:
                        try:
                            img = bpy.data.images.load(self.filepath, check_existing=True)
                            image_node.image = img
                        except Exception as e:
                            self.report({'WARNING'}, f"Could not load image: {e}")
                    
                    # Update Strength (Math node)
                    math_node = next((n for n in nodes if n.type == 'MATH'), None)
                    if math_node:
                        # Find the value input (usually input 1 for multiply)
                        if len(math_node.inputs) > 1:
                            math_node.inputs[1].default_value = self.strength
            
            # Add to collection (respects auto-collection setting)
            utils.add_object_to_collection(context, obj, "Image Gobo Lights")
            
            self.report({'INFO'}, "Successfully imported Image_Gobo")
            return {'FINISHED'}
        
        self.report({'ERROR'}, "Failed to import Image_Gobo")
        return {'CANCELLED'}


class LIGHTING_OT_ImportPlaneGoboNoise(bpy.types.Operator):
    """Import Plane Gobo Noise from DOME_light.blend and parent to active light."""
    bl_idname = "lighting.import_plane_gobo_noise"
    bl_label = "Import Plane Gobo Noise"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance Offset", default=0.2, min=0.0)
    camera_visibility: bpy.props.BoolProperty(name="Visible to Camera", default=False)

    def invoke(self, context, event):
        active = context.active_object
        if not active or active.type != 'LIGHT':
            self.report({'WARNING'}, "Please select an active light!")
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        active = context.active_object
        if not active or active.type != 'LIGHT':
            self.report({'WARNING'}, "Please select an active light!")
            return {'CANCELLED'}

        addon_dir = os.path.dirname(os.path.dirname(__file__))
        filepath = os.path.join(addon_dir, "DOME_light.blend")

        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"Library file not found: {filepath}")
            return {'CANCELLED'}

        # Import object
        bpy.ops.wm.append(
            filepath=os.path.join(filepath, "Object", "Plane_Gobo_noise"),
            directory=os.path.join(filepath, "Object") + os.sep,
            filename="Plane_Gobo_noise"
        )

        obj = bpy.data.objects.get("Plane_Gobo_noise")
        if obj:
            # Get light world transform
            depsgraph = context.evaluated_depsgraph_get()
            active_eval = active.evaluated_get(depsgraph)
            light_loc = active_eval.matrix_world.translation.copy()
            light_rot = active_eval.matrix_world.to_euler()

            # Set rotation to match light
            obj.rotation_euler = light_rot

            # Offset position in local -Z direction
            local_z = obj.matrix_world.to_quaternion() @ Vector((0, 0, -1))
            obj.location = light_loc + (local_z * self.distance)

            # Set camera visibility
            obj.visible_camera = self.camera_visibility

            # Parent to light
            obj.parent = active
            obj.matrix_parent_inverse = active.matrix_world.inverted()

            # Add to collection
            utils.add_object_to_collection(context, obj, "Plane Gobo Lights")

            self.report({'INFO'}, "Plane Gobo Noise added!")
            return {'FINISHED'}

        self.report({'ERROR'}, "Failed to import Plane_Gobo_noise")
        return {'CANCELLED'}


class LIGHTING_OT_ImportPlaneGoboVoronoise(bpy.types.Operator):
    """Import Plane Gobo Voronoise from DOME_light.blend and parent to active light."""
    bl_idname = "lighting.import_plane_gobo_voronoise"
    bl_label = "Import Plane Gobo Voronoise"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance Offset", default=0.2, min=0.0)
    camera_visibility: bpy.props.BoolProperty(name="Visible to Camera", default=False)

    def invoke(self, context, event):
        active = context.active_object
        if not active or active.type != 'LIGHT':
            self.report({'WARNING'}, "Please select an active light!")
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        active = context.active_object
        if not active or active.type != 'LIGHT':
            self.report({'WARNING'}, "Please select an active light!")
            return {'CANCELLED'}

        addon_dir = os.path.dirname(os.path.dirname(__file__))
        filepath = os.path.join(addon_dir, "DOME_light.blend")

        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"Library file not found: {filepath}")
            return {'CANCELLED'}

        # Import object
        bpy.ops.wm.append(
            filepath=os.path.join(filepath, "Object", "Plane_Gobo_voronoise"),
            directory=os.path.join(filepath, "Object") + os.sep,
            filename="Plane_Gobo_voronoise"
        )

        obj = bpy.data.objects.get("Plane_Gobo_voronoise")
        if obj:
            # Get light world transform
            depsgraph = context.evaluated_depsgraph_get()
            active_eval = active.evaluated_get(depsgraph)
            light_loc = active_eval.matrix_world.translation.copy()
            light_rot = active_eval.matrix_world.to_euler()

            # Set rotation to match light
            obj.rotation_euler = light_rot

            # Offset position in local -Z direction
            local_z = obj.matrix_world.to_quaternion() @ Vector((0, 0, -1))
            obj.location = light_loc + (local_z * self.distance)

            # Set camera visibility
            obj.visible_camera = self.camera_visibility

            # Parent to light
            obj.parent = active
            obj.matrix_parent_inverse = active.matrix_world.inverted()

            # Add to collection
            utils.add_object_to_collection(context, obj, "Plane Gobo Lights")

            self.report({'INFO'}, "Plane Gobo Voronoise added!")
            return {'FINISHED'}

        self.report({'ERROR'}, "Failed to import Plane_Gobo_voronoise")
        return {'CANCELLED'}


class LIGHTING_OT_ImportPlaneGoboWave(bpy.types.Operator):
    """Import Plane Gobo Wave from DOME_light.blend and parent to active light."""
    bl_idname = "lighting.import_plane_gobo_wave"
    bl_label = "Import Plane Gobo Wave"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance Offset", default=0.2, min=0.0)
    camera_visibility: bpy.props.BoolProperty(name="Visible to Camera", default=False)

    def invoke(self, context, event):
        active = context.active_object
        if not active or active.type != 'LIGHT':
            self.report({'WARNING'}, "Please select an active light!")
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        active = context.active_object
        if not active or active.type != 'LIGHT':
            self.report({'WARNING'}, "Please select an active light!")
            return {'CANCELLED'}

        addon_dir = os.path.dirname(os.path.dirname(__file__))
        filepath = os.path.join(addon_dir, "DOME_light.blend")

        if not os.path.exists(filepath):
            self.report({'ERROR'}, f"Library file not found: {filepath}")
            return {'CANCELLED'}

        # Import object
        bpy.ops.wm.append(
            filepath=os.path.join(filepath, "Object", "Plane_Gobo_wave"),
            directory=os.path.join(filepath, "Object") + os.sep,
            filename="Plane_Gobo_wave"
        )

        obj = bpy.data.objects.get("Plane_Gobo_wave")
        if obj:
            # Get light world transform
            depsgraph = context.evaluated_depsgraph_get()
            active_eval = active.evaluated_get(depsgraph)
            light_loc = active_eval.matrix_world.translation.copy()
            light_rot = active_eval.matrix_world.to_euler()

            # Set rotation to match light
            obj.rotation_euler = light_rot

            # Offset position in local -Z direction
            local_z = obj.matrix_world.to_quaternion() @ Vector((0, 0, -1))
            obj.location = light_loc + (local_z * self.distance)

            # Set camera visibility
            obj.visible_camera = self.camera_visibility

            # Parent to light
            obj.parent = active
            obj.matrix_parent_inverse = active.matrix_world.inverted()

            # Add to collection
            utils.add_object_to_collection(context, obj, "Plane Gobo Lights")

            self.report({'INFO'}, "Plane Gobo Wave added!")
            return {'FINISHED'}

        self.report({'ERROR'}, "Failed to import Plane_Gobo_wave")
        return {'CANCELLED'}


classes = (
    LIGHTING_OT_AddTrackerLights,
    LIGHTING_OT_AddLinearGradientPlane,
    LIGHTING_OT_AddSphereGradientPlane,
    LIGHTING_OT_AddTranslucentLight,
    LIGHTING_OT_AddSimpleGodRays,
    LIGHTING_OT_ImportDomeLight,
    LIGHTING_OT_ImportNoiseGobo,
    LIGHTING_OT_ImportImageGobo,
    LIGHTING_OT_ImportPlaneGoboNoise,
    LIGHTING_OT_ImportPlaneGoboVoronoise,
    LIGHTING_OT_ImportPlaneGoboWave,

)