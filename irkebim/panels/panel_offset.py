import bpy

class EdgeOffsetPanel(bpy.types.Panel):
    bl_label = "Edge Offset"
    bl_idname = "OBJECT_PT_edge_offset"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IRKE BIM'

# 방법 1: poll 제거 (항상 패널 표시됨)
# 그냥 제거해도 됩니다

# 방법 2: 완화된 조건 (3D 뷰에 오브젝트만 있으면 표시)
    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}


    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Exact Offset Tool")

        layout.prop(scene, "offset_distance", text="Offset Distance (mm)")
        layout.prop(scene, "offset_direction", text="Direction")

        layout.operator("irkebim.offset_curve", text="Create Exact Offset")
