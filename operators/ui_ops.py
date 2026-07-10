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
            is_excluded = False
            for coll in obj.users_collection:
                if utils.is_collection_excluded(context, coll):
                    is_excluded = True
                    break
            
            if is_excluded:
                self.report({'WARNING'}, f"Cannot select '{obj.name}' because its collection is excluded!")
                return {'CANCELLED'}

            bpy.ops.object.select_all(action='DESELECT')
            try:
                obj.select_set(True)
                context.view_layer.objects.active = obj
            except RuntimeError as e:
                self.report({'ERROR'}, f"Failed to select light: {e}")
                return {'CANCELLED'}
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
            
        if self.collection_name != "MASTER" and utils.is_collection_excluded(context, coll):
            self.report({'WARNING'}, f"Collection '{coll.name}' is excluded from View Layer!")
            return {'CANCELLED'}
            
        bpy.ops.object.select_all(action='DESELECT')
        
        selection_made = False
        for obj in coll.all_objects:
            if utils.is_managed_light(obj):
                try:
                    obj.select_set(True)
                    if not selection_made:
                        context.view_layer.objects.active = obj
                        selection_made = True
                except RuntimeError:
                    pass
                    
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
            vl = context.view_layer
            try:
                is_hidden = obj.hide_viewport or obj.hide_get(view_layer=vl)
            except RuntimeError:
                is_hidden = obj.hide_viewport
            new_state = not is_hidden
            # Set eye FIRST (before hide_viewport changes evaluation)
            try:
                obj.hide_set(new_state, view_layer=vl)
            except RuntimeError:
                pass
            obj.hide_viewport = new_state
        # Force outliner redraw
        for area in context.screen.areas:
            if area.type == 'OUTLINER':
                area.tag_redraw()
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
        
        # Check current state - if any light is hidden (either property), show all; otherwise hide all
        vl = context.view_layer
        any_hidden = False
        for obj in managed_lights:
            try:
                if obj.hide_viewport or obj.hide_get(view_layer=vl):
                    any_hidden = True
                    break
            except RuntimeError:
                if obj.hide_viewport:
                    any_hidden = True
                    break
        new_state = not any_hidden
        
        for obj in managed_lights:
            try:
                obj.hide_set(new_state, view_layer=vl)
            except RuntimeError:
                pass
            obj.hide_viewport = new_state
        
        # Force outliner redraw
        for area in context.screen.areas:
            if area.type == 'OUTLINER':
                area.tag_redraw()
        
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

class LIGHTING_OT_ToggleCollectionExclude(bpy.types.Operator):
    """Toggle include/exclude collection in view layer"""
    bl_idname = "lighting.toggle_collection_exclude"
    bl_label = "Toggle Collection Exclude"
    bl_options = {'REGISTER', 'UNDO'}
    
    collection_name: bpy.props.StringProperty()

    def execute(self, context):
        if self.collection_name == "MASTER":
            coll = context.scene.collection
        else:
            coll = bpy.data.collections.get(self.collection_name)
            
        if coll:
            lc = utils.find_layer_collection(context.view_layer.layer_collection, coll)
            if lc:
                lc.exclude = not lc.exclude
                self.report({'INFO'}, f"Collection '{coll.name}' {'Excluded' if lc.exclude else 'Included'}")
        return {'FINISHED'}

class LIGHTING_OT_SoloLight(bpy.types.Operator):
    """Toggle solo mode for the light (isolating it)"""
    bl_idname = "lighting.solo_light"
    bl_label = "Solo Light"
    bl_options = {'REGISTER', 'UNDO'}
    
    light_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.light_name)
        if obj:
            # Select the light and set active to trigger auto-solo state properly
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            
            utils.toggle_solo_light(context.scene, obj)
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
        return {'FINISHED'}

class LIGHTING_OT_DeleteLight(bpy.types.Operator):
    """Delete the light object from the scene"""
    bl_idname = "lighting.delete_light"
    bl_label = "Delete Light"
    bl_options = {'REGISTER', 'UNDO'}
    
    light_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.light_name)
        if obj:
            if context.scene.custom_light_solo_active and context.scene.custom_light_solo_light == obj.name:
                utils.restore_light_visibility(context.scene)
            name = obj.name
            bpy.data.objects.remove(obj, do_unlink=True)
            self.report({'INFO'}, f"Deleted light '{name}'")
        return {'FINISHED'}

class LIGHTING_OT_CleanupEmptyCollections(bpy.types.Operator):
    """Delete all empty collections in the scene"""
    bl_idname = "lighting.cleanup_empty_collections"
    bl_label = "Clean Empty Collections"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        deleted_count = 0
        while True:
            deleted_any = False
            all_colls = utils.get_all_collections(context.scene.collection)
            for coll in all_colls:
                if len(coll.objects) == 0 and len(coll.children) == 0:
                    bpy.data.collections.remove(coll)
                    deleted_count += 1
                    deleted_any = True
                    break
            if not deleted_any:
                break
        self.report({'INFO'}, f"Deleted {deleted_count} empty collections.")
        return {'FINISHED'}

class MismatchedLightItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    
    def update_viewport(self, context):
        if self.get("initializing", False):
            return
        obj = bpy.data.objects.get(self.name)
        if obj:
            obj.hide_viewport = self.hide_viewport
            vl = context.view_layer
            try:
                obj.hide_set(self.hide_viewport, view_layer=vl)
            except RuntimeError:
                pass
            # Force redraw of Viewport and Outliner to see changes instantly
            for area in context.screen.areas:
                if area.type in {'VIEW_3D', 'OUTLINER'}:
                    area.tag_redraw()

    def update_render(self, context):
        if self.get("initializing", False):
            return
        obj = bpy.data.objects.get(self.name)
        if obj:
            obj.hide_render = self.hide_render
            # Force redraw of Viewport and Outliner to see changes instantly
            for area in context.screen.areas:
                if area.type in {'VIEW_3D', 'OUTLINER'}:
                    area.tag_redraw()

    hide_viewport: bpy.props.BoolProperty(
        name="Viewport",
        description="Toggle viewport visibility (syncs eye and monitor)",
        update=update_viewport
    )
    
    hide_render: bpy.props.BoolProperty(
        name="Render",
        description="Toggle render visibility",
        update=update_render
    )

class LIGHTING_OT_CheckVisibilityMismatch(bpy.types.Operator):
    """Check for lights with mismatched viewport and render visibility"""
    bl_idname = "lighting.check_visibility_mismatch"
    bl_label = "Mismatched Lights"

    lights: bpy.props.CollectionProperty(type=MismatchedLightItem)

    def invoke(self, context, event):
        vl = context.view_layer
        mismatched = []
        all_lights = utils.get_all_managed_lights(context.scene)
        for obj in all_lights:
            try:
                eye_hidden = obj.hide_get(view_layer=vl)
            except RuntimeError:
                eye_hidden = False
            if (obj.hide_viewport or eye_hidden) != obj.hide_render:
                mismatched.append(obj.name)
        
        if not mismatched:
            self.report({'INFO'}, "All lights have matching viewport and render visibility.")
            return {'FINISHED'}
        
        # Populate the collection property
        self.lights.clear()
        for name in mismatched:
            obj = bpy.data.objects.get(name)
            if obj:
                item = self.lights.add()
                item["initializing"] = True
                item.name = obj.name
                try:
                    eye_h = obj.hide_get(view_layer=vl)
                except RuntimeError:
                    eye_h = False
                item.hide_viewport = obj.hide_viewport or eye_h
                item.hide_render = obj.hide_render
                item["initializing"] = False
                
        return context.window_manager.invoke_props_dialog(self, width=320)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text=f"{len(self.lights)} light(s) with mismatched visibility:", icon='ERROR')
        layout.separator()
        
        # Header row
        header = layout.row(align=True)
        sub = header.row()
        sub.scale_x = 2.0
        sub.label(text="Light Name")
        header.label(text="VP (Eye/Mon)")
        header.label(text="Render (Cam)")
        
        layout.separator()
        
        for item in self.lights:
            row = layout.row(align=True)
            
            # Light name
            sub = row.row()
            sub.scale_x = 2.0
            sub.label(text=item.name, icon='LIGHT')
            
            # Viewport toggle (dynamic eye icon)
            vp_icon = 'HIDE_ON' if item.hide_viewport else 'HIDE_OFF'
            row.prop(item, "hide_viewport", text="", icon=vp_icon, toggle=True)
            
            # Render toggle (dynamic camera icon)
            rd_icon = 'RESTRICT_RENDER_ON' if item.hide_render else 'RESTRICT_RENDER_OFF'
            row.prop(item, "hide_render", text="", icon=rd_icon, toggle=True)
    
    def execute(self, context):
        self.report({'INFO'}, "Visibility check complete.")
        return {'FINISHED'}

classes = (
    MismatchedLightItem,
    LIGHTING_OT_ToggleCollectionCollapse,
    LIGHTING_OT_SelectLight,
    LIGHTING_OT_SelectCollectionAll,
    LIGHTING_OT_ToggleRayCamera,
    LIGHTING_OT_ToggleViewport,
    LIGHTING_OT_ToggleRender,
    LIGHTING_OT_ToggleCollectionViewport,
    LIGHTING_OT_ToggleCollectionRender,
    LIGHTING_OT_ApplyCollectionBrightness,
    LIGHTING_OT_ToggleCollectionExclude,
    LIGHTING_OT_SoloLight,
    LIGHTING_OT_DeleteLight,
    LIGHTING_OT_CleanupEmptyCollections,
    LIGHTING_OT_CheckVisibilityMismatch,
)