# panel_main.py
import bpy
from . import operator_cube

class MainPanel(bpy.types.Panel):
    bl_label = "IRKE BIM Tools"
    bl_idname = "OBJECT_PT_irke_bim"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IRKE BIM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # 큐브 생성 섹션
        box = layout.box()
        box.label(text="Cube Generator")
        box.prop(scene, "cube_custom_size", text="Cube Size")
        box.operator(operator_cube.CubeOperator.bl_idname, text="Generate Cube")
        

# 등록할 클래스 리스트 (CubePanel은 이제 사용하지 않음)
classes = (MainPanel,)

def register():
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    for cls in classes:
        bpy.utils.register_class(cls)


    bpy.types.Scene.cube_custom_size = bpy.props.FloatProperty(
        name="Cube Size",
        description="Size of the new cube",
        default=2.0,
        min=0.01,
        soft_max=100.0
    )

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass