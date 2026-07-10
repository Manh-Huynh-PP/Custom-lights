import bpy
import math
from .. import utils

class LIGHTING_OT_AddPointLight(bpy.types.Operator):
    """Add a Point Light to the scene"""
    bl_idname = "lighting.add_point_light"
    bl_label = "Add Point Light"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        light_data = bpy.data.lights.new(name="CustomPointLight", type='POINT')
        light_obj = bpy.data.objects.new(name="CustomPointLight", object_data=light_data)
        light_obj.location = context.scene.cursor.location
        utils.setup_light_properties(light_data, type='POINT', energy=1000)
        utils.add_object_to_collection(context, light_obj, "Base Lights")
        self.report({'INFO'}, "Point Light Added!")
        return {'FINISHED'}

class LIGHTING_OT_AddSunLight(bpy.types.Operator):
    """Add a Sun Light to the scene"""
    bl_idname = "lighting.add_sun_light"
    bl_label = "Add Sun Light"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        light_data = bpy.data.lights.new(name="CustomSunLight", type='SUN')
        light_obj = bpy.data.objects.new(name="CustomSunLight", object_data=light_data)
        light_obj.location = context.scene.cursor.location
        utils.setup_light_properties(light_data, type='SUN', energy=1)
        utils.add_object_to_collection(context, light_obj, "Base Lights")
        self.report({'INFO'}, "Sun Light Added!")
        return {'FINISHED'}

class LIGHTING_OT_AddSpotLight(bpy.types.Operator):
    """Add a Spot Light to the scene"""
    bl_idname = "lighting.add_spot_light"
    bl_label = "Add Spot Light"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        light_data = bpy.data.lights.new(name="CustomSpotLight", type='SPOT')
        light_obj = bpy.data.objects.new(name="CustomSpotLight", object_data=light_data)
        light_obj.location = context.scene.cursor.location
        utils.setup_light_properties(light_data, type='SPOT', energy=1000)
        light_data.spot_size = math.radians(45)
        light_data.spot_blend = 0.15
        utils.add_object_to_collection(context, light_obj, "Base Lights")
        self.report({'INFO'}, "Spot Light Added!")
        return {'FINISHED'}

class LIGHTING_OT_AddAreaRectangleLight(bpy.types.Operator):
    """Add an Area Light with Rectangle shape"""
    bl_idname = "lighting.add_area_rectangle_light"
    bl_label = "Add Area Light (Rectangle)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        light_data = bpy.data.lights.new(name="CustomAreaRectLight", type='AREA')
        light_obj = bpy.data.objects.new(name="CustomAreaRectLight", object_data=light_data)
        light_obj.location = context.scene.cursor.location
        utils.setup_light_properties(light_data, type='AREA', energy=100)
        light_data.shape = 'RECTANGLE'
        light_data.size = 1.0
        light_data.size_y = 1.0
        utils.add_object_to_collection(context, light_obj, "Base Lights")
        self.report({'INFO'}, "Area Light (Rectangle) Added!")
        return {'FINISHED'}

class LIGHTING_OT_AddAreaEllipseLight(bpy.types.Operator):
    """Add an Area Light with Ellipse shape"""
    bl_idname = "lighting.add_area_ellipse_light"
    bl_label = "Add Area Light (Ellipse)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        light_data = bpy.data.lights.new(name="CustomAreaEllipseLight", type='AREA')
        light_obj = bpy.data.objects.new(name="CustomAreaEllipseLight", object_data=light_data)
        light_obj.location = context.scene.cursor.location
        utils.setup_light_properties(light_data, type='AREA', energy=100)
        light_data.shape = 'ELLIPSE'
        light_data.size = 1.0
        utils.add_object_to_collection(context, light_obj, "Base Lights")
        self.report({'INFO'}, "Area Light (Ellipse) Added!")
        return {'FINISHED'}

classes = (
    LIGHTING_OT_AddPointLight,
    LIGHTING_OT_AddSunLight,
    LIGHTING_OT_AddSpotLight,
    LIGHTING_OT_AddAreaRectangleLight,
    LIGHTING_OT_AddAreaEllipseLight,
)