import bpy
from .. import utils

class LIGHTING_OT_QuickAdjustMenu(bpy.types.Operator):
    """Quick adjust menu for selected light (Press L key)"""
    bl_idname = "lighting.quick_adjust_menu"
    bl_label = "Quick Adjust Light"
    bl_options = {'REGISTER', 'UNDO'}
    
    def update_light_energy(self, context):
        """Update callback for energy property"""
        self.apply_changes_realtime(context)
    
    def update_light_color(self, context):
        """Update callback for color property"""
        self.apply_changes_realtime(context)
    
    def update_light_size(self, context):
        """Update callback for size property"""
        self.apply_changes_realtime(context)
    
    def update_light_size_y(self, context):
        """Update callback for size_y property"""
        self.apply_changes_realtime(context)
    
    def update_spot_size(self, context):
        """Update callback for spot size property"""
        self.apply_changes_realtime(context)
    
    def update_spot_blend(self, context):
        """Update callback for spot blend property"""
        self.apply_changes_realtime(context)
    
    def update_shadow_soft_size(self, context):
        """Update callback for shadow soft size property"""
        self.apply_changes_realtime(context)
    
    # Properties for light adjustment with update callbacks
    light_energy: bpy.props.FloatProperty(
        name="Energy/Strength", 
        default=1.0, 
        min=0.0,
        update=update_light_energy
    )
    light_color: bpy.props.FloatVectorProperty(
        name="Color", 
        subtype='COLOR', 
        size=4, 
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0, 
        max=1.0,
        update=update_light_color
    )
    
    # For area lights
    light_size: bpy.props.FloatProperty(
        name="Size", 
        default=1.0, 
        min=0.0,
        update=update_light_size
    )
    light_size_y: bpy.props.FloatProperty(
        name="Size Y", 
        default=1.0, 
        min=0.0,
        update=update_light_size_y
    )
    
    # For spot lights
    spot_size: bpy.props.FloatProperty(
        name="Spot Size", 
        default=0.785398, 
        min=0.0, 
        max=3.14159, 
        subtype='ANGLE',
        update=update_spot_size
    )
    spot_blend: bpy.props.FloatProperty(
        name="Spot Blend", 
        default=0.15, 
        min=0.0, 
        max=1.0,
        update=update_spot_blend
    )
    
    # For point lights
    shadow_soft_size: bpy.props.FloatProperty(
        name="Shadow Soft Size", 
        default=0.25, 
        min=0.0,
        update=update_shadow_soft_size
    )
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and utils.is_managed_light(obj)
    
    def apply_changes_realtime(self, context):
        """Apply changes to the light in realtime as properties are adjusted"""
        obj = context.active_object
        
        if not obj or not utils.is_managed_light(obj):
            return
        
        # Apply changes based on object type
        if obj.type == 'LIGHT':
            obj.data.energy = self.light_energy
            obj.data.color = self.light_color[:3]
            
            if obj.data.type == 'AREA':
                obj.data.size = self.light_size
                obj.data.size_y = self.light_size_y
            elif obj.data.type == 'SPOT':
                obj.data.spot_size = self.spot_size
                obj.data.spot_blend = self.spot_blend
            elif obj.data.type == 'POINT':
                obj.data.shadow_soft_size = self.shadow_soft_size
                
        elif obj.type == 'MESH':
            # Set emission strength
            strength_socket = utils.get_mesh_emission_strength_control(obj)
            if strength_socket:
                strength_socket.default_value = self.light_energy
            
            # Set emission color
            color_socket = utils.get_mesh_emission_control(obj)
            if color_socket:
                color_socket.default_value = self.light_color
        
        # Force viewport update for all areas
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
    
    def invoke(self, context, event):
        obj = context.active_object
        
        if not obj or not utils.is_managed_light(obj):
            return {'CANCELLED'}
        
        # Load current values
        if obj.type == 'LIGHT':
            self.light_energy = obj.data.energy
            self.light_color = (*obj.data.color, 1.0)
            
            if obj.data.type == 'AREA':
                self.light_size = obj.data.size
                self.light_size_y = obj.data.size_y
            elif obj.data.type == 'SPOT':
                self.spot_size = obj.data.spot_size
                self.spot_blend = obj.data.spot_blend
            elif obj.data.type == 'POINT':
                self.shadow_soft_size = obj.data.shadow_soft_size
                
        elif obj.type == 'MESH':
            # Get emission strength
            strength_socket = utils.get_mesh_emission_strength_control(obj)
            if strength_socket:
                self.light_energy = strength_socket.default_value
            
            # Get emission color
            color_socket = utils.get_mesh_emission_control(obj)
            if color_socket:
                self.light_color = color_socket.default_value
        
        return context.window_manager.invoke_props_popup(self, event)
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        if not obj:
            return
        
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
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or not utils.is_managed_light(obj):
            return {'CANCELLED'}
        
        # Apply changes
        if obj.type == 'LIGHT':
            obj.data.energy = self.light_energy
            obj.data.color = self.light_color[:3]
            
            if obj.data.type == 'AREA':
                obj.data.size = self.light_size
                obj.data.size_y = self.light_size_y
            elif obj.data.type == 'SPOT':
                obj.data.spot_size = self.spot_size
                obj.data.spot_blend = self.spot_blend
            elif obj.data.type == 'POINT':
                obj.data.shadow_soft_size = self.shadow_soft_size
                
        elif obj.type == 'MESH':
            # Set emission strength
            strength_socket = utils.get_mesh_emission_strength_control(obj)
            if strength_socket:
                strength_socket.default_value = self.light_energy
            
            # Set emission color
            color_socket = utils.get_mesh_emission_control(obj)
            if color_socket:
                color_socket.default_value = self.light_color
        
        return {'FINISHED'}


classes = (
    LIGHTING_OT_QuickAdjustMenu,
)
