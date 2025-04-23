# irkebim/preferences/default_values.py
import bpy
from bpy.types import AddonPreferences
from bpy.props import FloatProperty, BoolProperty
from .. import config

# 오퍼레이터 기본값 정의 - 실제 기능 작동 관련 설정
DEFAULT_CUBE_SIZE = 2.0  # 기본 큐브 크기
DEFAULT_GRID_SIZE = 1.0  # 기본 그리드 크기
DEFAULT_PRECISION = 4    # 기본 소수점 정밀도

# 씬 업데이트 함수 - 함수를 먼저 정의해야 아래에서 참조 가능
def update_scenes_cube_size(value):
    """모든 씬의 큐브 크기 업데이트"""
    try:
        for scene in bpy.data.scenes:
            if hasattr(scene, "cube_custom_size"):
                scene.cube_custom_size = value
    except Exception as e:
        print(f"Error updating scenes: {e}")

# 환경 설정에서 값이 변경될 때 호출되는 함수
def on_cube_size_update(self, context):
    update_scenes_cube_size(self.default_cube_size)

class DefaultAddonPreferences(AddonPreferences):
    bl_idname = config.ADDON_ID

    # 오퍼레이터 기본값 설정 (UI에서 조정 가능)
    default_cube_size: FloatProperty(
        name="Default Cube Size",
        description="Set the default size of the cube for new scenes",
        default=DEFAULT_CUBE_SIZE,  # 이 파일에서 정의된 오퍼레이터 기본값 사용
        min=0.1,
        update=on_cube_size_update  # lambda 대신 명시적 함수 사용
    )
    
    # 추가 오퍼레이터 설정 - 실제 기능 동작에 관련된 설정
    use_snapping: BoolProperty(
        name="Use Snapping",
        description="Enable automatic snapping for precise modeling",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        
        # 오퍼레이터 기본값 섹션
        box = layout.box()
        box.label(text="Operator Default Values")
        box.prop(self, "default_cube_size")
        box.prop(self, "use_snapping")
        
        # 설명 추가
        layout.label(text="Changes will affect new scenes and existing scenes when restarting Blender")