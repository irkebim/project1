# panel_main.py
import bpy
from . import operator_cube

class CubePanel(bpy.types.Panel):
    bl_label = "Cube Generator"
    bl_idname = "OBJECT_PT_cube_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IRKE BIM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "cube_custom_size", text="Cube Size")
        layout.operator(operator_cube.CubeOperator.bl_idname, text="Generate Cube")

classes = (CubePanel,)

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
