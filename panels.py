import bpy
from . import utils

class LIGHTING_PT_BaseLights(bpy.types.Panel):
    """Panel for adding basic Blender lights"""
    bl_label = "Add Base Lights"
    bl_idname = "LIGHTING_PT_base_lights"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Custom Lights"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("lighting.add_point_light", text="Point", icon='LIGHT_POINT')
        row.operator("lighting.add_sun_light", text="Sun", icon='LIGHT_SUN')
        row.operator("lighting.add_spot_light", text="Spot", icon='LIGHT_SPOT')
        
        row = layout.row(align=True)
        row.operator("lighting.add_area_rectangle_light", text="Rectangle", icon='LIGHT_AREA')
        row.operator("lighting.add_area_ellipse_light", text="Ellipse", icon='LIGHT_AREA')

        layout.separator()
        # Add the checkbox to control auto-collection behavior
        layout.prop(context.scene, "custom_light_auto_collection")

class LIGHTING_PT_AddCustomLight(bpy.types.Panel):
    """Panel for adding custom light setups"""
    bl_label = "Custom Light Tools"
    bl_idname = "LIGHTING_PT_add_custom_light"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Custom Lights"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        layout.operator("lighting.add_tracker_lights", text="Tracker Light", icon='LIGHT')
        row = layout.row(align=True)
        row.operator("lighting.add_linear_gradient_plane", text="Linear Gradient", icon='MESH_PLANE')
        row.operator("lighting.add_sphere_gradient_plane", text="Sphere Gradient", icon='MESH_CIRCLE')
        layout.operator("lighting.add_translucent_light", text="Translucent Light Plane", icon='LIGHT_AREA')
        layout.operator("lighting.add_simple_god_rays", text="Simple God Rays", icon='LIGHT_SPOT')
        layout.operator("lighting.import_dome_light", text="Dome Light", icon='WORLD')
        row = layout.row(align=True)
        row.operator("lighting.import_noise_gobo", text="Noise Gobo", icon='TEXTURE')
        row.operator("lighting.import_image_gobo", text="Image Gobo", icon='IMAGE_DATA')
        row = layout.row(align=True)
        row.operator("lighting.import_plane_gobo_noise", text="P.Noise", icon='OUTLINER_DATA_VOLUME')
        row.operator("lighting.import_plane_gobo_voronoise", text="P.Voronoise", icon='OUTLINER_OB_POINTCLOUD')
        row.operator("lighting.import_plane_gobo_wave", text="P.Wave", icon='OUTLINER_OB_FORCE_FIELD')
        layout.operator("lighting.track_to_selected", text="Track to Selected", icon='TRACKING')
        layout.operator("lighting.make_emission_mesh", text="Make Emission Mesh", icon='SOLO_ON')
        layout.operator("light.convert_bb", text="Set Blackbody Color", icon='COLOR')

class LIGHTING_PT_ManageLights(bpy.types.Panel):
    """Panel to manage all light-like objects in the scene"""
    bl_label = "Manage Lights"
    bl_idname = "LIGHTING_PT_manage_lights"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Custom Lights"
    bl_order = 2

    def draw_light_controls(self, layout, light):
        """Draws controls for a standard Blender light object."""
        col = layout.column(align=True)
        row = col.row(align=True)
        row.alignment = 'LEFT'
        
        row.prop(light.data, "color", text="")
        row.prop(light.data, "energy", text="Brightness")
        
        if light.data.type == 'AREA':
            row.prop(light.data, "size", text="Width")
            row.prop(light.data, "size_y", text="Height")
        elif light.data.type == 'POINT':
            row.prop(light.data, "shadow_soft_size", text="Size")
        elif light.data.type == 'SPOT':
            row.prop(light.data, "spot_size", text="Size")
        elif light.data.type == 'SUN':
            row.prop(light.data, "angle", text="Angle")

    def draw_mesh_light_controls(self, layout, obj):
        """Draws controls for a mesh light object."""
        mesh_color = utils.get_mesh_emission_control(obj)
        mesh_strength = utils.get_mesh_emission_strength_control(obj)
        if mesh_color:
            row_mesh = layout.row(align=True)
            row_mesh.alignment = 'LEFT'
            row_mesh.prop(mesh_color, "default_value", text="")
            if mesh_strength:
                row_mesh.prop(mesh_strength, "default_value", text="Strength")

    def draw_collection(self, layout, coll, name, is_master=False):
        """Draws the UI for a single collection, mimicking the original addon's layout."""
        # Use the more restrictive filter from the original addon
        objs = [obj for obj in coll.objects if utils.is_managed_light(obj)]
        
        if not objs:
            return

        box = layout.box()
        row = box.row(align=True)

        if is_master:
            expanded = coll.get("lights_expanded_master", True)
        else:
            expanded = coll.get("lights_expanded", True)
        
        icon_state = "TRIA_DOWN" if expanded else "TRIA_RIGHT"
        is_active = utils.is_collection_active(coll)
        collection_icon = 'COLLECTION_COLOR_03' if is_active else 'OUTLINER_COLLECTION'
        
        # Left side: expand toggle and collection name
        op_toggle = row.operator("lighting.toggle_collection_collapse", text="", icon=icon_state, emboss=False)
        op_toggle.collection_name = "MASTER" if is_master else coll.name
        
        op_select = row.operator("lighting.select_collection_all", text=name, emboss=False, icon=collection_icon)
        op_select.collection_name = "MASTER" if is_master else coll.name
        
        # Right side: brightness slider + viewport/render toggles
        row_right = row.row(align=True)
        row_right.alignment = 'RIGHT'
        
        # Brightness multiplier slider (inline) - only for non-master collections
        if not is_master:
            sub = row_right.row(align=True)
            sub.scale_x = 0.8
            sub.prop(coll, "light_brightness_multiplier", text="", slider=True)
            # Apply button - bakes current values as new base
            op_apply = sub.operator("lighting.apply_collection_brightness", text="", icon='CHECKMARK')
            op_apply.collection_name = coll.name
        
        # Viewport and render toggles
        any_viewport_hidden = any(obj.hide_viewport for obj in objs)
        any_render_hidden = any(obj.hide_render for obj in objs)
        
        op_vp = row_right.operator("lighting.toggle_collection_viewport", text="", emboss=False, 
                            icon='HIDE_OFF' if not any_viewport_hidden else 'HIDE_ON')
        op_vp.collection_name = "MASTER" if is_master else coll.name
        
        op_rend = row_right.operator("lighting.toggle_collection_render", text="", emboss=False,
                              icon='RESTRICT_RENDER_OFF' if not any_render_hidden else 'RESTRICT_RENDER_ON')
        op_rend.collection_name = "MASTER" if is_master else coll.name

        if expanded:
            for obj in sorted(objs, key=lambda o: o.name):
                # --- Object Row ---
                row_obj = box.row(align=True)
                
                # Left side: select button and name (left-aligned)
                row_left = row_obj.row(align=True)
                row_left.alignment = 'LEFT'
                op_obj = row_left.operator("lighting.select_light", text=obj.name, emboss=False, 
                                         icon="KEYTYPE_MOVING_HOLD_VEC" if obj.select_get() else "RADIOBUT_OFF")
                op_obj.light_name = obj.name
                
                # Middle: light type controls
                if obj.type == 'LIGHT':
                    row_obj.prop(obj.data, "type", text="")
                    if obj.data.type == 'AREA':
                        row_obj.prop(obj.data, "shape", text="")
                
                # Right side: visibility toggles (right-aligned to edge)
                row_right = row_obj.row(align=True)
                row_right.alignment = 'RIGHT'
                
                if obj.type == 'MESH' and hasattr(obj, "visible_camera"):
                    op_ray = row_right.operator("lighting.toggle_ray_camera", text="", emboss=False, icon='RESTRICT_VIEW_OFF' if obj.visible_camera else 'RESTRICT_VIEW_ON')
                    op_ray.light_name = obj.name
                
                op_vp = row_right.operator("lighting.toggle_viewport", text="", emboss=False, icon='HIDE_OFF' if not obj.hide_viewport else 'HIDE_ON')
                op_vp.light_name = obj.name
                
                op_rend = row_right.operator("lighting.toggle_render", text="", emboss=False, icon='RESTRICT_RENDER_OFF' if not obj.hide_render else 'RESTRICT_RENDER_ON')
                op_rend.light_name = obj.name

                # Highlight row if selected
                if obj.select_get():
                    row_obj.alert = True

                # --- Controls on separate rows below the name (always visible) ---
                if obj.type == 'LIGHT':
                    self.draw_light_controls(box, obj)
                elif obj.type == 'MESH':
                    self.draw_mesh_light_controls(box, obj)
                
                # Separator after each object entry
                box.separator()

    def draw_world_controls(self, layout, context):
        world = context.scene.world
        if not world:
            return

        box = layout.box()
        row = box.row(align=True)
        row.label(text="", icon='WORLD')
        
        bg_node = utils.get_world_background_node(world)
        if bg_node:
            row.prop(bg_node.inputs["Strength"], "default_value", text="World Brightness")
        elif not world.use_nodes:
            row.prop(world, "color", text="World Color")
        else:
            row.label(text="No Background Node")

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # World Controls
        self.draw_world_controls(layout, context)

        # Master Collection (Scene Collection)
        self.draw_collection(layout, scene.collection, "SCENE COLLECTION", is_master=True)

        # Draw all other collections in the scene that contain managed lights
        all_collections = utils.get_all_collections(scene.collection)
        for coll in sorted(all_collections, key=lambda c: c.name):
            # The draw_collection function will check for objects and do nothing if empty.
            self.draw_collection(layout, coll, coll.name.upper())

classes = (
    LIGHTING_PT_BaseLights,
    LIGHTING_PT_AddCustomLight,
    LIGHTING_PT_ManageLights,
)