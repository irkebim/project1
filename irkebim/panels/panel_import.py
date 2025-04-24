import bpy

class ImportPlanPanel(bpy.types.Panel):
    bl_label = "Import Plan Image"
    bl_idname = "OBJECT_PT_import_plan"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IRKE BIM'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Import Floor Plan")
        layout.operator("irkebim.import_image", text="Import Plan Image")
