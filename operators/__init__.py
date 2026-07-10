from . import add_basic_lights, add_custom_lights, utility_ops, ui_ops, quick_adjust, pie_menu

# Combine all operator classes from the different modules
classes = (
    *add_basic_lights.classes,
    *add_custom_lights.classes,
    *utility_ops.classes,
    *ui_ops.classes,
    *quick_adjust.classes,
    *pie_menu.classes,
)