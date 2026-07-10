bl_info = {
    "name": "Custom Light",
    "description": "An addon to manage custom lights",
    "author": "Manh Huynh",
    "version": (2, 1, 5),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Custom Lights",
    "warning": "",
    "category": "Lighting",
    "doc_url": "https://github.com/Manh-Huynh-PP/Custom-lights",
    "license": "GPL-2.0-or-later",
}

import bpy
import math

# Import submodules FIRST to ensure they are available in the package namespace
# before any reloads are attempted. This prevents circular import errors
# where a submodule tries to import from the parent package during reload.
if "bpy" in locals():
    import importlib
    from . import utils
    from .operators import add_basic_lights, add_custom_lights, utility_ops, ui_ops, quick_adjust, pie_menu
    importlib.reload(add_basic_lights)
    importlib.reload(add_custom_lights)
    importlib.reload(utility_ops)
    importlib.reload(ui_ops)
    importlib.reload(quick_adjust)
    importlib.reload(pie_menu)
    from . import operators
    from . import panels
    
    importlib.reload(utils)
    importlib.reload(operators)
    importlib.reload(panels)
else:
    from . import utils, operators, panels

import rna_keymap_ui

class LIGHTING_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        layout.label(text="Configure Shortcut Keys:", icon='PREFERENCES')
        
        wm = context.window_manager
        kc = wm.keyconfigs.user
        
        if kc:
            km = kc.keymaps.get('3D View')
            if km:
                # Find keymap item for our shortcut dispatcher
                kmi_found = False
                for kmi in km.keymap_items:
                    if kmi.idname == 'lighting.shortcut_dispatcher':
                        box = layout.box()
                        # Force keymap item to not be expanded
                        kmi.show_expanded = False
                        
                        row = box.row(align=True)
                        row.prop(kmi, "active", text="")
                        row.label(text="Shortcut Key:")
                        
                        # Event type editor
                        row.prop(kmi, "map_type", text="")
                        
                        # Event key editor
                        if kmi.map_type == 'KEYBOARD':
                            row.prop(kmi, "type", text="", full_event=True)
                        elif kmi.map_type == 'MOUSE':
                            row.prop(kmi, "type", text="", full_event=True)
                        elif kmi.map_type == 'NDOF':
                            row.prop(kmi, "type", text="", full_event=True)
                        elif kmi.map_type == 'TWEAK':
                            subrow = row.row(align=True)
                            subrow.prop(kmi, "type", text="")
                            subrow.prop(kmi, "value", text="")
                        elif kmi.map_type == 'TIMER':
                            row.prop(kmi, "type", text="")
                        
                        # Modifiers
                        import sys
                        oskey_label = "Cmd" if sys.platform == 'darwin' else ("Win" if sys.platform == 'win32' else "OS")
                        row.prop(kmi, "shift_ui", text="Shift", toggle=True)
                        row.prop(kmi, "ctrl_ui", text="Ctrl", toggle=True)
                        row.prop(kmi, "alt_ui", text="Alt", toggle=True)
                        row.prop(kmi, "oskey_ui", text=oskey_label, toggle=True)
                        
                        # Restore button
                        if (not kmi.is_user_defined) and kmi.is_user_modified:
                            row.operator("preferences.keyitem_restore", text="", icon='BACK').item_id = kmi.id
                        kmi_found = True
                if not kmi_found:
                    layout.label(text="Shortcut dispatcher keymap item not found.", icon='ERROR')
        
        layout.separator()
        layout.operator("lighting.reset_keymaps", icon='FILE_REFRESH')


class LIGHTING_OT_ResetKeymaps(bpy.types.Operator):
    """Reset the Custom Lights shortcut keys to their defaults"""
    bl_idname = "lighting.reset_keymaps"
    bl_label = "Reset Shortcuts to Default"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.window_manager
        kc = wm.keyconfigs.user
        if kc:
            km = kc.keymaps.get('3D View')
            if km:
                for kmi in km.keymap_items:
                    if kmi.idname == 'lighting.shortcut_dispatcher':
                        kmi.type = 'L'
                        kmi.value = 'PRESS'
                        kmi.any = False
                        kmi.shift = False
                        kmi.ctrl = False
                        kmi.alt = False
                        kmi.oskey = False
                        kmi.active = True
        self.report({'INFO'}, "Shortcuts reset to default (L key)!")
        return {'FINISHED'}

# Combine all classes from submodules
classes = (
    LIGHTING_Preferences,
    LIGHTING_OT_ResetKeymaps,
    *operators.classes,
    *panels.classes,
)

# Handlers
handlers = [
    utils.update_emission_color,
]

# Keymap storage
addon_keymaps = []

def update_hdri_rotation(self, context):
    mapping = utils.get_or_create_world_mapping_node(self)
    if mapping:
        mapping.inputs['Rotation'].default_value[2] = math.radians(self.hdri_rotation_z)

def register():
    # Add a scene property to control collection creation
    bpy.types.Scene.custom_light_auto_collection = bpy.props.BoolProperty(
        name="Auto-create Collections",
        description="Automatically create and place new lights into dedicated collections",
        default=True
    )
    
    bpy.types.Scene.custom_light_target_coll_type = bpy.props.EnumProperty(
        name="Collection Mode",
        items=[
            ('NEW', "New", "Create a new parent collection"),
            ('EXISTING', "Existing", "Choose an existing collection")
        ],
        default='NEW'
    )
    
    bpy.types.Scene.custom_light_target_coll_name = bpy.props.StringProperty(
        name="Collection Name",
        default="Custom Lights"
    )
    
    bpy.types.Scene.custom_light_target_coll_ptr = bpy.props.PointerProperty(
        type=bpy.types.Collection,
        name="Target Collection"
    )
    
    bpy.types.Scene.custom_light_solo_active = bpy.props.BoolProperty(
        name="Solo Active",
        default=False
    )
    
    bpy.types.Scene.custom_light_solo_light = bpy.props.StringProperty(
        name="Solo Light Name",
        default=""
    )
    
    bpy.types.Scene.custom_light_filter_type = bpy.props.EnumProperty(
        name="Filter",
        items=[
            ('ALL', "All", "Show all managed light objects", 'LIGHT', 0),
            ('LIGHT', "Base Lights", "Show only standard light sources", 'LIGHT_DATA', 1),
            ('MESH', "Mesh Lights", "Show only emission meshes", 'MESH_DATA', 2),
            ('GOBO', "Gobos", "Show only lights with gobo setup", 'TEXTURE_DATA', 3),
        ],
        default='ALL'
    )
    
    bpy.types.World.hdri_rotation_z = bpy.props.FloatProperty(
        name="HDRI Rotation Z",
        description="Rotate the environment map around the Z axis",
        default=0.0,
        min=0.0,
        max=360.0,
        soft_min=0.0,
        soft_max=360.0,
        step=100,
        precision=1,
        update=update_hdri_rotation
    )
    
    # Add brightness multiplier property to Collection with update callback
    def update_brightness(self, context):
        # Skip if triggered by Apply button
        if self.get("_skip_update"):
            return
        multiplier = self.light_brightness_multiplier
        utils.apply_collection_brightness(self, multiplier)
    
    bpy.types.Collection.light_brightness_multiplier = bpy.props.FloatProperty(
        name="Multiply",
        description="Multiply brightness of all lights in this collection",
        default=1.0,
        min=0.0,
        soft_max=10.0,
        step=10,
        precision=2,
        update=update_brightness
    )

    for cls in classes:
        bpy.utils.register_class(cls)

    if utils.update_emission_color not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(utils.update_emission_color)
    if utils.auto_solo_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(utils.auto_solo_handler)
    
    # Register keymap for shortcut dispatcher
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        # L key: Shortcut Dispatcher (calls Quick Adjust if light is active, else opens Pie Menu)
        kmi = km.keymap_items.new('lighting.shortcut_dispatcher', 'L', 'PRESS')
        addon_keymaps.append((km, kmi))

def unregister():
    # Unregister keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    if utils.update_emission_color in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(utils.update_emission_color)
    if utils.auto_solo_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(utils.auto_solo_handler)

    # Clean up the scene property when the addon is disabled
    try:
        del bpy.types.Scene.custom_light_auto_collection
    except AttributeError:
        pass # Property was not registered, do nothing
        
    try:
        del bpy.types.Scene.custom_light_target_coll_type
    except AttributeError:
        pass
        
    try:
        del bpy.types.Scene.custom_light_target_coll_name
    except AttributeError:
        pass
        
    try:
        del bpy.types.Scene.custom_light_target_coll_ptr
    except AttributeError:
        pass
    
    try:
        del bpy.types.Scene.custom_light_solo_active
    except AttributeError:
        pass
        
    try:
        del bpy.types.Scene.custom_light_solo_light
    except AttributeError:
        pass
        
    try:
        del bpy.types.Scene.custom_light_filter_type
    except AttributeError:
        pass
        
    try:
        del bpy.types.World.hdri_rotation_z
    except AttributeError:
        pass
    
    try:
        del bpy.types.Collection.light_brightness_multiplier
    except AttributeError:
        pass

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)