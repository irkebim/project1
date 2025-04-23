# irkebim/panels/panel_main.py
import bpy
from ..operators.cube import CubeOperator

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
        box.operator(CubeOperator.bl_idname, text="Generate Cube")