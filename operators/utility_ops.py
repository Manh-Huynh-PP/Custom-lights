import bpy
from .. import utils

class LIGHT_OT_ConvertBB(bpy.types.Operator):
    """Set blackbody color using Blender's native Blackbody node (for mesh) or Temperature property (for lights)"""
    bl_idname = "light.convert_bb"
    bl_label = "Set Blackbody Color"
    bl_options = {'REGISTER', 'UNDO'}

    temperature: bpy.props.FloatProperty(name="Temperature (K)", default=5500, min=1000, max=12000)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "temperature", slider=True)

    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No active object!")
            return {'CANCELLED'}
        
        if obj.type == 'LIGHT':
            # Case 2: Light object - use native temperature property
            obj.data.use_temperature = True
            obj.data.temperature = self.temperature
            
            self.report({'INFO'}, f"Light temperature set to {self.temperature:.0f}K")
            return {'FINISHED'}
            
        elif obj.type == 'MESH':
            # Case 1: Emission mesh - use Blackbody node
            mat = obj.active_material
            if not mat or not mat.use_nodes:
                self.report({'ERROR'}, "Mesh has no active material with nodes!")
                return {'CANCELLED'}
            
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            # Find emission node
            emission_node = next((node for node in nodes if node.type == 'EMISSION'), None)
            if not emission_node:
                self.report({'ERROR'}, "Material has no Emission node!")
                return {'CANCELLED'}
            
            # Find or create Blackbody node
            blackbody_node = next((node for node in nodes if node.type == 'BLACKBODY'), None)
            if not blackbody_node:
                blackbody_node = nodes.new(type='ShaderNodeBlackbody')
                blackbody_node.location = (emission_node.location[0] - 250, emission_node.location[1])
            
            # Set temperature
            blackbody_node.inputs['Temperature'].default_value = self.temperature
            
            # Connect Blackbody to Emission Color
            color_input = emission_node.inputs['Color']
            # Remove existing connections to Color input
            for link in color_input.links:
                links.remove(link)
            
            # Create new connection
            links.new(blackbody_node.outputs['Color'], color_input)
            
            self.report({'INFO'}, f"Blackbody node connected at {self.temperature:.0f}K")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Active object must be a Light or a Mesh!")
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

class LIGHTING_OT_TrackToSelected(bpy.types.Operator):
    """Create a Track To constraint for selected objects, using the active object as the target"""
    bl_idname = "lighting.track_to_selected"
    bl_label = "Track to Selected"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_obj = context.active_object
        selected_objs = context.selected_objects

        if not active_obj or len(selected_objs) < 2:
            self.report({'WARNING'}, "Select at least two objects (active object is the target).")
            return {'CANCELLED'}

        for obj in selected_objs:
            if obj == active_obj:
                continue
            
            constraint = next((c for c in obj.constraints if c.type == 'TRACK_TO' and c.target == active_obj), None)
            if not constraint:
                constraint = obj.constraints.new(type='TRACK_TO')
            
            constraint.target = active_obj
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'

        self.report({'INFO'}, "Track To constraint created for selected objects.")
        return {'FINISHED'}

class LIGHTING_OT_MakeEmissionMesh(bpy.types.Operator):
    """Rename active mesh to 'L.*' and add an Emission shader"""
    bl_idname = "lighting.make_emission_mesh"
    bl_label = "Make Emission Mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a mesh object.")
            return {'CANCELLED'}
        
        if not obj.name.startswith("L."):
            obj.name = "L." + obj.name
            
        mat = bpy.data.materials.new(name="Emission_Material")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        emission_node = nodes.new(type="ShaderNodeEmission")
        output_node = nodes.new(type="ShaderNodeOutputMaterial")
        links.new(emission_node.outputs["Emission"], output_node.inputs["Surface"])
        
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
            
        return {'FINISHED'}

classes = (
    LIGHT_OT_ConvertBB,
    LIGHTING_OT_TrackToSelected,
    LIGHTING_OT_MakeEmissionMesh,
)