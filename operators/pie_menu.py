import bpy
from .. import utils

class LIGHTING_MT_ViewportPieMenu(bpy.types.Menu):
    """Pie menu for quick access to light creation and management tools"""
    bl_label = "Custom Lights"
    bl_idname = "LIGHTING_MT_viewport_pie_menu"

    def draw(self, context):
        layout = self.layout
        if not hasattr(layout, "menu_pie"):
            return
        pie = layout.menu_pie()
        
        active_obj = context.active_object
        selected_objs = context.selected_objects
        
        # 1. Left (West)
        pie.operator("lighting.add_point_light", text="Point Light", icon='LIGHT_POINT')
        
        # 2. Right (East)
        pie.operator("lighting.add_area_rectangle_light", text="Area Light", icon='LIGHT_AREA')
        
        # 3. Bottom (South)
        if active_obj and active_obj.type == 'MESH' and len(selected_objs) >= 2:
            pie.operator("lighting.track_to_selected", text="Track to Selected", icon='TRACKING')
        else:
            pie.column()
        
        # 4. Top (North)
        pie.operator("lighting.add_tracker_lights", text="Tracker Light", icon='LIGHT')
        
        # 5. Top-Left (Northwest)
        pie.operator("lighting.add_spot_light", text="Spot Light", icon='LIGHT_SPOT')
        
        # 6. Top-Right (Northeast)
        pie.operator("lighting.add_sun_light", text="Sun Light", icon='LIGHT_SUN')
        
        # 7. Bottom-Left (Southwest)
        pie.operator("lighting.add_linear_gradient_plane", text="Linear Gradient", icon='MESH_PLANE')
        
        # 8. Bottom-Right (Southeast)
        pie.operator("lighting.add_sphere_gradient_plane", text="Sphere Gradient", icon='MESH_CIRCLE')

class LIGHTING_OT_ShortcutDispatcher(bpy.types.Operator):
    """Dispatches L key shortcut based on active object selection"""
    bl_idname = "lighting.shortcut_dispatcher"
    bl_label = "Shortcut Dispatcher"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        active_obj = context.active_object
        selected_objs = context.selected_objects
        
        if active_obj and active_obj.type == 'MESH' and len(selected_objs) >= 2:
            return bpy.ops.wm.call_menu_pie('INVOKE_DEFAULT', name='LIGHTING_MT_viewport_pie_menu')
            
        selected_lights = [obj for obj in context.selected_objects if utils.is_managed_light(obj)]
        if selected_lights:
            return bpy.ops.lighting.quick_adjust_menu('INVOKE_DEFAULT')
        else:
            return bpy.ops.wm.call_menu_pie('INVOKE_DEFAULT', name='LIGHTING_MT_viewport_pie_menu')

classes = (
    LIGHTING_MT_ViewportPieMenu,
    LIGHTING_OT_ShortcutDispatcher,
)
