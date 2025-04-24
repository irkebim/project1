"""
irkebim/panels/panel_offset.py
개선된 오프셋 패널 - 메시 및 커브 지원
"""
import bpy

class EdgeOffsetPanel(bpy.types.Panel):
    bl_label = "Edge Offset"
    bl_idname = "OBJECT_PT_edge_offset"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IRKE BIM'
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type in {'MESH', 'CURVE'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.active_object
        
        # 객체 타입에 따라 UI 조정
        is_curve = obj and obj.type == 'CURVE'
        
        # 오프셋 설정
        col = layout.column(align=True)
        col.prop(scene, "edge_offset_distance", text="Distance (mm)")
        
        # 방향 설정
        row = col.row(align=True)
        row.prop(scene, "edge_offset_direction", text="Direction")
        
        # 반복 횟수
        if not is_curve:  # 커브에선 반복 횟수가 무의미
            col.prop(scene, "edge_offset_count", text="Count")
        
        # 면 생성 (메시에만 해당)
        if not is_curve:
            col.prop(scene, "edge_offset_create_faces", text="Create Faces")
        
        # 실행 버튼
        row = layout.row()
        if is_curve:
            op = row.operator("mesh.edge_offset", text="Create Offset Curve")
            op.as_new_object = True  # 커브는 항상 새 객체로 생성
        else:
            # 메시일 때 선택 사항
            box = layout.box()
            box.label(text="Output Options")
            col = box.column(align=True)
            col.label(text="Apply as:")
            row = col.row(align=True)
            
            # 기존 오브젝트 수정 버튼
            op1 = row.operator("mesh.edge_offset", text="Modify Existing")
            op1.as_new_object = False
            
            # 새 오브젝트 생성 버튼
            op2 = row.operator("mesh.edge_offset", text="New Object")
            op2.as_new_object = True