import bpy
from ..operators.cube import CubeOperator

class OpenSettingsModal(bpy.types.Operator):
    bl_idname = "irke.open_settings_modal"
    bl_label = "Settings"
    bl_description = "Open settings for IRKE BIM Tools"
    
    def execute(self, context):
        # 설정값 저장 로직
        self.report({'INFO'}, "Settings saved")
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Default Values Settings")
        
        # default_values.py의 설정값 입력 필드들
        box = layout.box()
        box.label(text="General Settings")
        box.prop(context.scene, "cube_custom_size", text="Default Cube Size")
        
        # 추가 설정들이 있다면 여기에 계속 추가
        # box.prop(context.scene, "다른_설정_속성", text="다른 설정 레이블")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

class MainPanel(bpy.types.Panel):
    bl_label = "IRKE BIM Tools"
    bl_idname = "OBJECT_PT_irke_bim"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IRKE BIM'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # 헤더 부분 (패널 제목과 설정 버튼)
        row = layout.row()
        row.label(text="IRKE BIM Tools")  # 왼쪽에 패널 제목
        row.operator(OpenSettingsModal.bl_idname, text="", icon='PREFERENCES')  # 오른쪽에 설정 버튼
        
        # 구분선 추가
        layout.separator()
        
        # 큐브 생성 섹션
        box = layout.box()
        box.label(text="Cube Generator")
        box.prop(scene, "cube_custom_size", text="Cube Size")
        box.operator(CubeOperator.bl_idname, text="Generate Cube")