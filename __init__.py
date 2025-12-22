bl_info = {
    "name": "Custom Light",
    "description": "An addon to manage custom lights",
    "author": "Manh Huynh",
    "version": (2, 0, 0),  # Version bump for refactor
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Custom Lights",
    "warning": "",
    "category": "Lighting",
    "doc_url": "",  # Add documentation link if available
    "license": "GPL-2.0-or-later",
}

# Make sure to handle addon reloads correctly
if "bpy" in locals():
    import importlib
    if "operators" in locals():
        importlib.reload(operators)
    if "panels" in locals():
        importlib.reload(panels)
    if "utils" in locals():
        importlib.reload(utils)

import bpy
from . import operators, panels, utils

# Combine all classes from submodules
classes = (
    *operators.classes,
    *panels.classes,
)

# Handlers
handlers = [
    utils.update_emission_color,
]

# Keymap storage
addon_keymaps = []

def register():
    # Add a scene property to control collection creation
    bpy.types.Scene.custom_light_auto_collection = bpy.props.BoolProperty(
        name="Auto-create Collections",
        description="Automatically create and place new lights into dedicated collections",
        default=True
    )
    
    # Add brightness multiplier property to Collection with update callback
    def update_brightness(self, context):
        # Skip if triggered by Apply button
        if self.get("_skip_update"):
            return
        multiplier = self.light_brightness_multiplier
        if multiplier != 1.0:  # Only apply if not default
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
    
    # Register keymap for quick adjust
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('lighting.quick_adjust_menu', 'L', 'PRESS')
        addon_keymaps.append((km, kmi))

def unregister():
    # Unregister keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    if utils.update_emission_color in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(utils.update_emission_color)

    # Clean up the scene property when the addon is disabled
    try:
        del bpy.types.Scene.custom_light_auto_collection
    except AttributeError:
        pass # Property was not registered, do nothing
    
    try:
        del bpy.types.Collection.light_brightness_multiplier
    except AttributeError:
        pass

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)