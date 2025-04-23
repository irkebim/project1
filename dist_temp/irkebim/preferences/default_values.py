# irkebim/preferences/default_values.py
import bpy
from bpy.types import AddonPreferences
from bpy.props import FloatProperty
from .. import config

class DefaultAddonPreferences(AddonPreferences):
    bl_idname = config.ADDON_ID

    default_cube_size: FloatProperty(
        name="Default Cube Size",
        description="Set the default size of the cube for new scenes",
        default=config.DEFAULT_CUBE_SIZE,  # 설정에서 기본값 가져오기
        min=0.1,
        update=lambda self, context: update_scenes_cube_size(self.default_cube_size)
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "default_cube_size")
        layout.label(text="Changes will affect new scenes and existing scenes when restarting Blender")

# 업데이트 함수 - 모든 씬의 큐브 크기 업데이트
def update_scenes_cube_size(value):
    try:
        for scene in bpy.data.scenes:
            if hasattr(scene, "cube_custom_size"):
                scene.cube_custom_size = value
    except Exception as e:
        print(f"Error updating scenes: {e}")