# irkebim/operators/cube.py
import bpy
from .. import config

class CubeOperator(bpy.types.Operator):
    bl_idname = "mesh.add_custom_cube"
    bl_label = "Add Cube"
    bl_description = "Add a cube with the specified size"

    def execute(self, context):
        scene = context.scene
        size = scene.cube_custom_size
        bpy.ops.mesh.primitive_cube_add(size=size)
        return {'FINISHED'}

# 프로퍼티 정의 - 자동 수집을 위한 이름 규칙 사용
Property_Scene_cube_custom_size = bpy.props.FloatProperty(
    name="Cube Size",
    description="Size of the new cube",
    default=config.DEFAULT_CUBE_SIZE,  # 설정에서 기본값 가져오기
    min=0.01,
    soft_max=100.0
)