import bpy
from .. import utils

class LIGHTING_OT_QuickAdjustMenu(bpy.types.Operator):
    """Quick adjust menu for selected light (Press L key)"""
    bl_idname = "lighting.quick_adjust_menu"
    bl_label = "Quick Adjust Light"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Properties for light adjustment
    relative_mode: bpy.props.BoolProperty(
        name="Relative Mode",
        description="Adjust values relatively (offsets) instead of setting all lights to the same absolute value",
        default=True
    )
    
    solo_active_toggle: bpy.props.BoolProperty(
        name="Solo Light",
        description="Toggle solo mode for the active light",
        default=False
    )

    mesh_display_type: bpy.props.EnumProperty(
        name="Display As",
        description="Viewport display style for the selected mesh lights",
        items=[
            ('TEXTURED', "Texture", "Display as textured", 'SHADING_TEXTURE', 0),
            ('WIRE', "Wire", "Display as wireframe", 'SHADING_WIRE', 1),
        ],
        default='TEXTURED'
    )

    mesh_visible_camera: bpy.props.BoolProperty(
        name="Camera",
        description="Toggle ray visibility for Camera",
        default=True
    )
    mesh_visible_diffuse: bpy.props.BoolProperty(
        name="Diffuse",
        description="Toggle ray visibility for Diffuse",
        default=True
    )
    mesh_visible_glossy: bpy.props.BoolProperty(
        name="Glossy",
        description="Toggle ray visibility for Glossy",
        default=True
    )
    mesh_visible_transmission: bpy.props.BoolProperty(
        name="Transmission",
        description="Toggle ray visibility for Transmission",
        default=True
    )
    mesh_visible_volume: bpy.props.BoolProperty(
        name="Volume Scatter",
        description="Toggle ray visibility for Volume Scatter",
        default=True
    )
    mesh_visible_shadow: bpy.props.BoolProperty(
        name="Shadow",
        description="Toggle ray visibility for Shadow",
        default=True
    )

    light_visible_camera: bpy.props.BoolProperty(
        name="Camera",
        description="Toggle Cycles ray visibility for Camera on standard lights",
        default=True
    )
    light_visible_diffuse: bpy.props.BoolProperty(
        name="Diffuse",
        description="Toggle Cycles ray visibility for Diffuse on standard lights",
        default=True
    )
    light_visible_glossy: bpy.props.BoolProperty(
        name="Glossy",
        description="Toggle Cycles ray visibility for Glossy on standard lights",
        default=True
    )
    light_visible_transmission: bpy.props.BoolProperty(
        name="Transmission",
        description="Toggle Cycles ray visibility for Transmission on standard lights",
        default=True
    )
    light_visible_volume: bpy.props.BoolProperty(
        name="Volume Scatter",
        description="Toggle Cycles ray visibility for Volume Scatter on standard lights",
        default=True
    )
    light_visible_shadow: bpy.props.BoolProperty(
        name="Shadow",
        description="Toggle Cycles ray visibility for Shadow on standard lights",
        default=True
    )

    light_energy: bpy.props.FloatProperty(
        name="Energy/Strength", 
        default=1.0, 
        min=0.0
    )
    light_color: bpy.props.FloatVectorProperty(
        name="Color", 
        subtype='COLOR', 
        size=4, 
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, 
        max=1.0
    )
    
    # For area lights
    light_size: bpy.props.FloatProperty(
        name="Size", 
        default=1.0, 
        min=0.0
    )
    light_size_y: bpy.props.FloatProperty(
        name="Size Y", 
        default=1.0, 
        min=0.0
    )
    
    # For spot lights
    spot_size: bpy.props.FloatProperty(
        name="Spot Size", 
        default=0.785398, 
        min=0.0, 
        max=3.14159, 
        subtype='ANGLE'
    )
    spot_blend: bpy.props.FloatProperty(
        name="Spot Blend", 
        default=0.15, 
        min=0.0, 
        max=1.0
    )
    
    # For point lights
    shadow_soft_size: bpy.props.FloatProperty(
        name="Shadow Soft Size", 
        default=0.25, 
        min=0.0
    )
    
    @classmethod
    def poll(cls, context):
        if context.active_object and utils.is_managed_light(context.active_object):
            return True
        for obj in context.selected_objects:
            if utils.is_managed_light(obj):
                return True
        return False

    def get_selected_lights(self, context):
        """Helper to get all selected managed lights, with fallback to active object"""
        selected = [obj for obj in context.selected_objects if utils.is_managed_light(obj)]
        if not selected:
            active = context.active_object
            if active and utils.is_managed_light(active):
                selected = [active]
        return selected

    def apply_changes_realtime(self, context):
        """Apply changes to the light in realtime as properties are adjusted"""
        selected_lights = LIGHTING_OT_QuickAdjustMenu.get_selected_lights(self, context)
        if not selected_lights:
            return
        
        # Check if we should adjust relatively and have stored initial values
        use_relative = self.relative_mode and hasattr(self, "init_values")
        
        if use_relative:
            # Compute deltas from the primary/operator values
            delta_energy = self.light_energy - getattr(self, "init_energy_val", self.light_energy)
            delta_size = self.light_size - getattr(self, "init_size_val", self.light_size)
            delta_size_y = self.light_size_y - getattr(self, "init_size_y_val", self.light_size_y)
            delta_spot_size = self.spot_size - getattr(self, "init_spot_size_val", self.spot_size)
            delta_spot_blend = self.spot_blend - getattr(self, "init_spot_blend_val", self.spot_blend)
            delta_shadow_soft_size = self.shadow_soft_size - getattr(self, "init_shadow_soft_size_val", self.shadow_soft_size)
        
        for obj in selected_lights:
            # Check if we have relative initial values for this object
            obj_relative = use_relative and obj.name in self.init_values
            
            if obj.type == 'LIGHT':
                # Apply energy
                if obj_relative:
                    obj.data.energy = max(0.0, self.init_values[obj.name]['energy'] + delta_energy)
                else:
                    obj.data.energy = self.light_energy
                
                # Color is set absolutely (standard behavior)
                obj.data.color = self.light_color[:3]
                
                if obj.data.type == 'AREA':
                    if obj_relative:
                        obj.data.size = max(0.0, self.init_values[obj.name]['size'] + delta_size)
                        obj.data.size_y = max(0.0, self.init_values[obj.name]['size_y'] + delta_size_y)
                    else:
                        obj.data.size = self.light_size
                        obj.data.size_y = self.light_size_y
                elif obj.data.type == 'SPOT':
                    if obj_relative:
                        obj.data.spot_size = max(0.0, min(3.14159, self.init_values[obj.name]['spot_size'] + delta_spot_size))
                        obj.data.spot_blend = max(0.0, min(1.0, self.init_values[obj.name]['spot_blend'] + delta_spot_blend))
                    else:
                        obj.data.spot_size = self.spot_size
                        obj.data.spot_blend = self.spot_blend
                elif obj.data.type == 'POINT':
                    if obj_relative:
                        obj.data.shadow_soft_size = max(0.0, self.init_values[obj.name]['shadow_soft_size'] + delta_shadow_soft_size)
                    else:
                        obj.data.shadow_soft_size = self.shadow_soft_size
                
                # Apply Cycles ray visibility
                if hasattr(obj.data, "cycles"):
                    cycles_data = obj.data.cycles
                    if hasattr(cycles_data, "use_camera"):
                        cycles_data.use_camera = self.light_visible_camera
                    if hasattr(cycles_data, "use_diffuse"):
                        cycles_data.use_diffuse = self.light_visible_diffuse
                    if hasattr(cycles_data, "use_glossy"):
                        cycles_data.use_glossy = self.light_visible_glossy
                    if hasattr(cycles_data, "use_transmission"):
                        cycles_data.use_transmission = self.light_visible_transmission
                    if hasattr(cycles_data, "use_volume"):
                        cycles_data.use_volume = self.light_visible_volume
                    if hasattr(cycles_data, "cast_shadow"):
                        cycles_data.cast_shadow = self.light_visible_shadow
                    
            elif obj.type == 'MESH':
                # Set emission strength
                strength_socket = utils.get_mesh_emission_strength_control(obj)
                if strength_socket:
                    if obj_relative:
                        strength_socket.default_value = max(0.0, self.init_values[obj.name]['energy'] + delta_energy)
                    else:
                        strength_socket.default_value = self.light_energy
                
                # Set emission color
                color_socket = utils.get_mesh_emission_control(obj)
                if color_socket:
                    color_socket.default_value = self.light_color
                
                # Set display type
                obj.display_type = self.mesh_display_type
                
                # Set visible rays
                obj.visible_camera = self.mesh_visible_camera
                obj.visible_diffuse = self.mesh_visible_diffuse
                obj.visible_glossy = self.mesh_visible_glossy
                obj.visible_transmission = self.mesh_visible_transmission
                obj.visible_volume_scatter = self.mesh_visible_volume
                obj.visible_shadow = self.mesh_visible_shadow
        
        # Force viewport update for all areas
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()

    def invoke(self, context, event):
        selected_lights = self.get_selected_lights(context)
        if not selected_lights:
            return {'CANCELLED'}
        
        # Try to use active_object if it is in selected_lights, otherwise first selected light
        primary_obj = context.active_object
        if not primary_obj or primary_obj not in selected_lights:
            primary_obj = selected_lights[0]
        
        # Load current values
        if primary_obj.type == 'LIGHT':
            self.light_energy = primary_obj.data.energy
            self.light_color = (*primary_obj.data.color, 1.0)
            
            if primary_obj.data.type == 'AREA':
                self.light_size = primary_obj.data.size
                self.light_size_y = primary_obj.data.size_y
            elif primary_obj.data.type == 'SPOT':
                self.spot_size = primary_obj.data.spot_size
                self.spot_blend = primary_obj.data.spot_blend
            elif primary_obj.data.type == 'POINT':
                self.shadow_soft_size = primary_obj.data.shadow_soft_size
                
        elif primary_obj.type == 'MESH':
            # Get emission strength
            strength_socket = utils.get_mesh_emission_strength_control(primary_obj)
            if strength_socket:
                self.light_energy = strength_socket.default_value
            
            # Get emission color
            color_socket = utils.get_mesh_emission_control(primary_obj)
            if color_socket:
                self.light_color = color_socket.default_value
                
        # Store primary light's values on the operator instance for relative delta calculations
        self.init_energy_val = self.light_energy
        self.init_size_val = self.light_size
        self.init_size_y_val = self.light_size_y
        self.init_spot_size_val = self.spot_size
        self.init_spot_blend_val = self.spot_blend
        self.init_shadow_soft_size_val = self.shadow_soft_size
        
        # Store initial values for ALL selected lights to allow relative offset adjustments
        self.init_values = {}
        for obj in selected_lights:
            self.init_values[obj.name] = {
                'type': obj.type,
                'light_type': obj.data.type if obj.type == 'LIGHT' else None,
                'visible_camera': True,
                'visible_diffuse': True,
                'visible_glossy': True,
                'visible_transmission': True,
                'visible_volume': True,
                'visible_shadow': True,
            }
            if obj.type == 'LIGHT':
                cycles_vals = {}
                if hasattr(obj.data, "cycles"):
                    cycles_data = obj.data.cycles
                    cycles_vals = {
                        'visible_camera': getattr(cycles_data, "use_camera", True),
                        'visible_diffuse': getattr(cycles_data, "use_diffuse", True),
                        'visible_glossy': getattr(cycles_data, "use_glossy", True),
                        'visible_transmission': getattr(cycles_data, "use_transmission", True),
                        'visible_volume': getattr(cycles_data, "use_volume", True),
                        'visible_shadow': getattr(cycles_data, "cast_shadow", True),
                    }
                else:
                    cycles_vals = {
                        'visible_camera': True,
                        'visible_diffuse': True,
                        'visible_glossy': True,
                        'visible_transmission': True,
                        'visible_volume': True,
                        'visible_shadow': True,
                    }
                self.init_values[obj.name].update({
                    'energy': obj.data.energy,
                    'color': tuple(obj.data.color),
                    'size': obj.data.size if obj.data.type == 'AREA' else 1.0,
                    'size_y': obj.data.size_y if obj.data.type == 'AREA' else 1.0,
                    'spot_size': obj.data.spot_size if obj.data.type == 'SPOT' else 0.0,
                    'spot_blend': obj.data.spot_blend if obj.data.type == 'SPOT' else 0.0,
                    'shadow_soft_size': obj.data.shadow_soft_size if obj.data.type == 'POINT' else 0.0,
                    **cycles_vals
                })
            elif obj.type == 'MESH':
                strength_val = 1.0
                strength_socket = utils.get_mesh_emission_strength_control(obj)
                if strength_socket:
                    strength_val = strength_socket.default_value
                    
                color_val = (1.0, 1.0, 1.0, 1.0)
                color_socket = utils.get_mesh_emission_control(obj)
                if color_socket:
                    color_val = tuple(color_socket.default_value)
                    
                self.init_values[obj.name].update({
                    'energy': strength_val,
                    'color': color_val,
                    'display_type': obj.display_type,
                    'visible_camera': obj.visible_camera,
                    'visible_diffuse': obj.visible_diffuse,
                    'visible_glossy': obj.visible_glossy,
                    'visible_transmission': obj.visible_transmission,
                    'visible_volume': obj.visible_volume_scatter,
                    'visible_shadow': obj.visible_shadow,
                })
        
        # Initialize mesh properties
        first_mesh = next((obj for obj in selected_lights if obj.type == 'MESH'), None)
        if first_mesh:
            if first_mesh.display_type in {'TEXTURED', 'WIRE'}:
                self.mesh_display_type = first_mesh.display_type
            else:
                self.mesh_display_type = 'TEXTURED'
            self.mesh_visible_camera = first_mesh.visible_camera
            self.mesh_visible_diffuse = first_mesh.visible_diffuse
            self.mesh_visible_glossy = first_mesh.visible_glossy
            self.mesh_visible_transmission = first_mesh.visible_transmission
            self.mesh_visible_volume = first_mesh.visible_volume_scatter
            self.mesh_visible_shadow = first_mesh.visible_shadow
        else:
            self.mesh_display_type = 'TEXTURED'
            self.mesh_visible_camera = True
            self.mesh_visible_diffuse = True
            self.mesh_visible_glossy = True
            self.mesh_visible_transmission = True
            self.mesh_visible_volume = True
            self.mesh_visible_shadow = True
        
        # Initialize light properties
        first_light = next((obj for obj in selected_lights if obj.type == 'LIGHT'), None)
        if first_light and hasattr(first_light.data, "cycles"):
            cycles_data = first_light.data.cycles
            self.light_visible_camera = getattr(cycles_data, "use_camera", True)
            self.light_visible_diffuse = getattr(cycles_data, "use_diffuse", True)
            self.light_visible_glossy = getattr(cycles_data, "use_glossy", True)
            self.light_visible_transmission = getattr(cycles_data, "use_transmission", True)
            self.light_visible_volume = getattr(cycles_data, "use_volume", True)
            self.light_visible_shadow = getattr(cycles_data, "cast_shadow", True)
        else:
            self.light_visible_camera = True
            self.light_visible_diffuse = True
            self.light_visible_glossy = True
            self.light_visible_transmission = True
            self.light_visible_volume = True
            self.light_visible_shadow = True
        
        # Initialize solo_active_toggle property based on current scene state
        is_this_solo = context.scene.custom_light_solo_active and context.scene.custom_light_solo_light == primary_obj.name
        self.solo_active_toggle = is_this_solo
        
        return context.window_manager.invoke_props_popup(self, event)

    def check(self, context):
        # Handle solo active toggle
        selected_lights = self.get_selected_lights(context)
        if selected_lights:
            primary_obj = context.active_object
            if not primary_obj or primary_obj not in selected_lights:
                primary_obj = selected_lights[0]
            
            # Sync active object solo state
            scene_solo_active = context.scene.custom_light_solo_active and context.scene.custom_light_solo_light == primary_obj.name
            if self.solo_active_toggle != scene_solo_active:
                utils.toggle_solo_light(context.scene, primary_obj)
        
        # Apply changes in realtime
        self.apply_changes_realtime(context)
        return True

    def draw(self, context):
        layout = self.layout
        selected_lights = self.get_selected_lights(context)
        if not selected_lights:
            return
        
        if len(selected_lights) == 1:
            obj = selected_lights[0]
            layout.label(text=f"Adjust: {obj.name}", icon='LIGHT')
            layout.separator()
            
            if obj.type == 'LIGHT':
                layout.prop(self, "light_energy", text="Energy")
                layout.prop(self, "light_color", text="Color")
                
                layout.separator()
                
                if obj.data.type == 'AREA':
                    layout.prop(self, "light_size", text="Width")
                    layout.prop(self, "light_size_y", text="Height")
                elif obj.data.type == 'SPOT':
                    layout.prop(self, "spot_size", text="Spot Size")
                    layout.prop(self, "spot_blend", text="Blend")
                elif obj.data.type == 'POINT':
                    layout.prop(self, "shadow_soft_size", text="Radius")
                    
            elif obj.type == 'MESH':
                layout.prop(self, "light_energy", text="Strength")
                layout.prop(self, "light_color", text="Color")
                
                layout.separator()
                row = layout.row(align=True)
                row.label(text="Display As:")
                row.prop(self, "mesh_display_type", expand=True)

            # Solo active button in Quick Adjust Menu (for single light)
            layout.separator()
            solo_text = "Disable Solo" if self.solo_active_toggle else "Solo Light"
            solo_icon = 'SOLO_ON' if self.solo_active_toggle else 'SOLO_OFF'
            layout.prop(self, "solo_active_toggle", text=solo_text, toggle=True, icon=solo_icon)
            
            # Draw Flip and Rotate buttons for gradient lights in L menu only if feasible
            nodes_dict = utils.get_gobo_nodes(obj)
            has_flip = False
            has_rotate = False
            if nodes_dict:
                color_ramp = nodes_dict.get('color_ramp')
                if color_ramp and hasattr(color_ramp, "color_ramp") and color_ramp.color_ramp:
                    if len(color_ramp.color_ramp.elements) >= 2:
                        has_flip = True
                node_tree = nodes_dict.get('node_tree')
                if node_tree:
                    has_sep = any(node.type == 'SEPARATE_XYZ' or node.bl_idname == 'ShaderNodeSeparateXYZ' for node in node_tree.nodes)
                    has_grad = any(node.type == 'TEX_GRADIENT' or node.bl_idname == 'ShaderNodeTexGradient' for node in node_tree.nodes)
                    if has_sep and has_grad:
                        has_rotate = True
            
            if has_flip or has_rotate:
                layout.separator()
                row_grad = layout.row(align=True)
                if has_flip:
                    row_grad.operator("lighting.flip_gradient", text="Flip Gradient", icon='FILE_REFRESH')
                if has_rotate:
                    row_grad.operator("lighting.rotate_gradient", text="Rotate Gradient", icon='FILE_REFRESH')
            
            # Draw Ray Visibility at the bottom of single light popup
            if obj.type == 'LIGHT' and hasattr(obj.data, "cycles"):
                layout.separator()
                box = layout.box()
                box.label(text="Ray Visibility", icon='GRID')
                
                col = box.column(align=True)
                
                row1 = col.row(align=True)
                row1.prop(self, "light_visible_camera", text="Camera")
                row1.prop(self, "light_visible_shadow", text="Shadow")
                
                row2 = col.row(align=True)
                row2.prop(self, "light_visible_diffuse", text="Diffuse")
                row2.prop(self, "light_visible_glossy", text="Glossy")
                
                row3 = col.row(align=True)
                row3.prop(self, "light_visible_transmission", text="Transmission")
                row3.prop(self, "light_visible_volume", text="Volume")
            elif obj.type == 'MESH':
                layout.separator()
                box = layout.box()
                box.label(text="Ray Visibility", icon='GRID')
                
                col = box.column(align=True)
                
                row1 = col.row(align=True)
                row1.prop(self, "mesh_visible_camera", text="Camera")
                row1.prop(self, "mesh_visible_shadow", text="Shadow")
                
                row2 = col.row(align=True)
                row2.prop(self, "mesh_visible_diffuse", text="Diffuse")
                row2.prop(self, "mesh_visible_glossy", text="Glossy")
                
                row3 = col.row(align=True)
                row3.prop(self, "mesh_visible_transmission", text="Transmission")
                row3.prop(self, "mesh_visible_volume", text="Volume")
        else:
            layout.label(text=f"Adjust {len(selected_lights)} Selected Lights", icon='LIGHT')
            layout.separator()
            
            # Show the relative mode checkbox at the top of controls
            layout.prop(self, "relative_mode", text="Relative Offset Mode")
            layout.separator()
            
            layout.prop(self, "light_energy", text="Energy/Strength")
            layout.prop(self, "light_color", text="Color")
            
            has_area = any(obj.type == 'LIGHT' and obj.data.type == 'AREA' for obj in selected_lights)
            has_spot = any(obj.type == 'LIGHT' and obj.data.type == 'SPOT' for obj in selected_lights)
            has_point = any(obj.type == 'LIGHT' and obj.data.type == 'POINT' for obj in selected_lights)
            
            if has_area or has_spot or has_point:
                layout.separator()
                
            if has_area:
                layout.prop(self, "light_size", text="Area Width")
                layout.prop(self, "light_size_y", text="Area Height")
            if has_spot:
                layout.prop(self, "spot_size", text="Spot Size")
                layout.prop(self, "spot_blend", text="Spot Blend")
            if has_point:
                layout.prop(self, "shadow_soft_size", text="Point Radius")

            has_light = any(obj.type == 'LIGHT' for obj in selected_lights)
            if has_light:
                layout.separator()
                box = layout.box()
                box.label(text="Light Ray Visibility", icon='GRID')
                
                col = box.column(align=True)
                
                row1 = col.row(align=True)
                row1.prop(self, "light_visible_camera", text="Camera")
                row1.prop(self, "light_visible_shadow", text="Shadow")
                
                row2 = col.row(align=True)
                row2.prop(self, "light_visible_diffuse", text="Diffuse")
                row2.prop(self, "light_visible_glossy", text="Glossy")
                
                row3 = col.row(align=True)
                row3.prop(self, "light_visible_transmission", text="Transmission")
                row3.prop(self, "light_visible_volume", text="Volume")

            has_mesh = any(obj.type == 'MESH' for obj in selected_lights)
            if has_mesh:
                layout.separator()
                row = layout.row(align=True)
                row.label(text="Mesh Display:")
                row.prop(self, "mesh_display_type", expand=True)
                
                layout.separator()
                box = layout.box()
                box.label(text="Ray Visibility", icon='GRID')
                
                col = box.column(align=True)
                
                row1 = col.row(align=True)
                row1.prop(self, "mesh_visible_camera", text="Camera")
                row1.prop(self, "mesh_visible_shadow", text="Shadow")
                
                row2 = col.row(align=True)
                row2.prop(self, "mesh_visible_diffuse", text="Diffuse")
                row2.prop(self, "mesh_visible_glossy", text="Glossy")
                
                row3 = col.row(align=True)
                row3.prop(self, "mesh_visible_transmission", text="Transmission")
                row3.prop(self, "mesh_visible_volume", text="Volume")

    def execute(self, context):
        selected_lights = self.get_selected_lights(context)
        if not selected_lights:
            return {'CANCELLED'}
        self.apply_changes_realtime(context)
        return {'FINISHED'}

    def cancel(self, context):
        """Revert changes when the user cancels the popup"""
        # Rely on Blender's native Undo system ('UNDO' option in bl_options)
        # to revert changes if the user presses Ctrl+Z. This prevents changes from 
        # being lost when the popup is dismissed by clicking other buttons (like Rotate/Flip).
        pass

class LIGHTING_OT_FlipGradient(bpy.types.Operator):
    """Flip the active light's gradient color stops"""
    bl_idname = "lighting.flip_gradient"
    bl_label = "Flip Gradient"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj:
            return False
        nodes_dict = utils.get_gobo_nodes(obj)
        if not nodes_dict:
            return False
        color_ramp = nodes_dict.get('color_ramp')
        if not color_ramp or not hasattr(color_ramp, "color_ramp") or not color_ramp.color_ramp:
            return False
        return len(color_ramp.color_ramp.elements) >= 2

    def execute(self, context):
        obj = context.active_object
        nodes_dict = utils.get_gobo_nodes(obj)
        if nodes_dict:
            color_ramp = nodes_dict.get('color_ramp')
            if color_ramp and len(color_ramp.color_ramp.elements) >= 2:
                # Swap first two elements' colors
                col0 = tuple(color_ramp.color_ramp.elements[0].color)
                col1 = tuple(color_ramp.color_ramp.elements[1].color)
                color_ramp.color_ramp.elements[0].color = col1
                color_ramp.color_ramp.elements[1].color = col0
                self.report({'INFO'}, "Gradient flipped!")
                context.area.tag_redraw()
                
                # Push manual undo state to support Undo without using REGISTER/UNDO options
                try:
                    bpy.ops.ed.undo_push(message="Flip Gradient")
                except Exception:
                    pass
                return {'FINISHED'}
        return {'CANCELLED'}


class LIGHTING_OT_RotateGradient(bpy.types.Operator):
    """Toggle rotation of the gradient between X and Y axes"""
    bl_idname = "lighting.rotate_gradient"
    bl_label = "Rotate Gradient"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj:
            return False
        nodes_dict = utils.get_gobo_nodes(obj)
        if not nodes_dict:
            return False
        node_tree = nodes_dict.get('node_tree')
        if not node_tree:
            return False
        has_sep = any(node.type == 'SEPARATE_XYZ' or node.bl_idname == 'ShaderNodeSeparateXYZ' for node in node_tree.nodes)
        has_grad = any(node.type == 'TEX_GRADIENT' or node.bl_idname == 'ShaderNodeTexGradient' for node in node_tree.nodes)
        return has_sep and has_grad

    def execute(self, context):
        obj = context.active_object
        nodes_dict = utils.get_gobo_nodes(obj)
        if nodes_dict:
            node_tree = nodes_dict.get('node_tree')
            if node_tree:
                # Find Separate XYZ and Gradient Texture nodes
                sep_xyz = None
                gradient = None
                for node in node_tree.nodes:
                    if node.type == 'SEPARATE_XYZ' or node.bl_idname == 'ShaderNodeSeparateXYZ':
                        sep_xyz = node
                    elif node.type == 'TEX_GRADIENT' or node.bl_idname == 'ShaderNodeTexGradient':
                        gradient = node
                
                if sep_xyz and gradient:
                    input_sock = gradient.inputs.get('Vector') or gradient.inputs[0]
                    current_link = None
                    for link in node_tree.links:
                        if link.to_socket == input_sock:
                            current_link = link
                            break
                    
                    if current_link:
                        from_socket_name = current_link.from_socket.name
                        node_tree.links.remove(current_link)
                        if from_socket_name == 'X':
                            node_tree.links.new(sep_xyz.outputs['Y'], input_sock)
                        else:
                            node_tree.links.new(sep_xyz.outputs['X'], input_sock)
                        self.report({'INFO'}, "Gradient rotated!")
                        context.area.tag_redraw()
                        
                        # Push manual undo state to support Undo without using REGISTER/UNDO options
                        try:
                            bpy.ops.ed.undo_push(message="Rotate Gradient")
                        except Exception:
                            pass
                        return {'FINISHED'}
        return {'CANCELLED'}


classes = (
    LIGHTING_OT_QuickAdjustMenu,
    LIGHTING_OT_FlipGradient,
    LIGHTING_OT_RotateGradient,
)
