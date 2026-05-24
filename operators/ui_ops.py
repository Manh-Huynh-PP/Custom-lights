import bpy
from .. import utils

class LIGHTING_OT_ToggleCollectionCollapse(bpy.types.Operator):
    """Toggle collapse/expand collection in the panel"""
    bl_idname = "lighting.toggle_collection_collapse"
    bl_label = "Toggle Collection Collapse"
    
    collection_name: bpy.props.StringProperty()

    def execute(self, context):
        if self.collection_name == "MASTER":
            scene = context.scene
            expanded = scene.collection.get("lights_expanded_master", True)
            scene.collection["lights_expanded_master"] = not expanded
        else:
            coll = bpy.data.collections.get(self.collection_name)
            if coll:
                expanded = coll.get("lights_expanded", True)
                coll["lights_expanded"] = not expanded
        return {'FINISHED'}

class LIGHTING_OT_SelectLight(bpy.types.Operator):
    """Select the light object"""
    bl_idname = "lighting.select_light"
    bl_label = "Select Light"
    
    light_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.light_name)
        if obj:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
        return {'FINISHED'}

class LIGHTING_OT_SelectCollectionAll(bpy.types.Operator):
    """Select all light-like objects in the collection"""
    bl_idname = "lighting.select_collection_all"
    bl_label = "Select Collection (All)"
    
    collection_name: bpy.props.StringProperty()

    def execute(self, context):
        if self.collection_name == "MASTER":
            coll = context.scene.collection
        else:
            coll = bpy.data.collections.get(self.collection_name)
        
        if not coll:
            self.report({'WARNING'}, "Collection not found")
            return {'CANCELLED'}
            
        bpy.ops.object.select_all(action='DESELECT')
        
        selection_made = False
        for obj in coll.all_objects:
            if utils.is_managed_light(obj):
                obj.select_set(True)
                if not selection_made:
                    context.view_layer.objects.active = obj
                    selection_made = True
                    
        return {'FINISHED'}

class LIGHTING_OT_ToggleRayCamera(bpy.types.Operator):
    """Toggle ray visibility for camera"""
    bl_idname = "lighting.toggle_ray_camera"
    bl_label = "Toggle Ray Camera"
    
    light_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.light_name)
        if obj:
            obj.visible_camera = not obj.visible_camera
        return {'FINISHED'}

class LIGHTING_OT_ToggleViewport(bpy.types.Operator):
    """Toggle viewport visibility"""
    bl_idname = "lighting.toggle_viewport"
    bl_label = "Toggle Viewport"
    
    light_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.light_name)
        if obj:
            obj.hide_viewport = not obj.hide_viewport
        return {'FINISHED'}

class LIGHTING_OT_ToggleRender(bpy.types.Operator):
    """Toggle render visibility"""
    bl_idname = "lighting.toggle_render"
    bl_label = "Toggle Render"
    
    light_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.light_name)
        if obj:
            obj.hide_render = not obj.hide_render
        return {'FINISHED'}

class LIGHTING_OT_ToggleCollectionViewport(bpy.types.Operator):
    """Toggle viewport visibility for all lights in collection"""
    bl_idname = "lighting.toggle_collection_viewport"
    bl_label = "Toggle Collection Viewport"
    
    collection_name: bpy.props.StringProperty()

    def execute(self, context):
        if self.collection_name == "MASTER":
            coll = context.scene.collection
        else:
            coll = bpy.data.collections.get(self.collection_name)
        
        if not coll:
            return {'CANCELLED'}
        
        # Get all managed lights in collection
        managed_lights = [obj for obj in coll.objects if utils.is_managed_light(obj)]
        
        if not managed_lights:
            return {'CANCELLED'}
        
        # Check current state - if any light is hidden, show all; otherwise hide all
        any_hidden = any(obj.hide_viewport for obj in managed_lights)
        new_state = not any_hidden
        
        for obj in managed_lights:
            obj.hide_viewport = new_state
        
        return {'FINISHED'}

class LIGHTING_OT_ToggleCollectionRender(bpy.types.Operator):
    """Toggle render visibility for all lights in collection"""
    bl_idname = "lighting.toggle_collection_render"
    bl_label = "Toggle Collection Render"
    
    collection_name: bpy.props.StringProperty()

    def execute(self, context):
        if self.collection_name == "MASTER":
            coll = context.scene.collection
        else:
            coll = bpy.data.collections.get(self.collection_name)
        
        if not coll:
            return {'CANCELLED'}
        
        # Get all managed lights in collection
        managed_lights = [obj for obj in coll.objects if utils.is_managed_light(obj)]
        
        if not managed_lights:
            return {'CANCELLED'}
        
        # Check current state - if any light is hidden, show all; otherwise hide all
        any_hidden = any(obj.hide_render for obj in managed_lights)
        new_state = not any_hidden
        
        for obj in managed_lights:
            obj.hide_render = new_state
        
        return {'FINISHED'}



class LIGHTING_OT_ApplyCollectionBrightness(bpy.types.Operator):
    """Apply current brightness as new base values and reset slider to 1"""
    bl_idname = "lighting.apply_collection_brightness"
    bl_label = "Apply Brightness"
    bl_options = {'REGISTER', 'UNDO'}
    
    collection_name: bpy.props.StringProperty()

    def execute(self, context):
        coll = bpy.data.collections.get(self.collection_name)
        
        if not coll:
            return {'CANCELLED'}
        
        # Update base values to current energy
        for obj in coll.objects:
            if not utils.is_managed_light(obj):
                continue
            
            current = utils.get_light_energy(obj)
            if current is not None:
                obj["_base_energy"] = current
                
        # Reset the collection's last_multiplier history
        coll["_last_multiplier"] = 1.0
        
        # Reset slider to 1.0 without triggering update
        coll["_skip_update"] = True
        coll.light_brightness_multiplier = 1.0
        if "_skip_update" in coll:
            del coll["_skip_update"]
        
        return {'FINISHED'}


classes = (
    LIGHTING_OT_ToggleCollectionCollapse,
    LIGHTING_OT_SelectLight,
    LIGHTING_OT_SelectCollectionAll,
    LIGHTING_OT_ToggleRayCamera,
    LIGHTING_OT_ToggleViewport,
    LIGHTING_OT_ToggleRender,
    LIGHTING_OT_ToggleCollectionViewport,
    LIGHTING_OT_ToggleCollectionRender,
    LIGHTING_OT_ApplyCollectionBrightness,
)