# irkebim/preferences/default_values.py
import bpy
from bpy.types import AddonPreferences
from bpy.props import FloatProperty, BoolProperty
from .. import config

# 오퍼레이터 기본값 정의 - 실제 기능 작동 관련 설정
DEFAULT_CUBE_SIZE = 2.0  # 기본 큐브 크기
DEFAULT_GRID_SIZE = 1.0  # 기본 그리드 크기
DEFAULT_PRECISION = 4    # 기본 소수점 정밀도
DEFAULT_WALL_HEIGHT = 2.4  # 기본 벽체 높이
DEFAULT_WALL_THICKNESS = 0.2  # 기본 벽체 두께

# 환경설정 속성과 씬 속성 간의 매핑 정보
# 형식: {'환경설정 속성 이름': ('씬 속성 이름', 기본값)}
# 이 매핑이 있는 속성은 자동으로 동기화됩니다
PREFERENCES_TO_SCENE_MAPPING = {
    'default_cube_size': ('cube_custom_size', DEFAULT_CUBE_SIZE),
    'default_wall_height': ('wall_default_height', DEFAULT_WALL_HEIGHT),
    'default_wall_thickness': ('wall_thickness', DEFAULT_WALL_THICKNESS)  # 아직 씬에 추가하지 않은 예시 속성
}

# 씬 업데이트 함수 - 속성별 특수 로직이 필요한 경우 사용
def update_scenes_property(property_name, value):
    """특정 속성 값으로 모든 씬 업데이트"""
    try:
        # 매핑에서 씬 속성 이름 찾기
        if property_name in PREFERENCES_TO_SCENE_MAPPING:
            scene_property_name = PREFERENCES_TO_SCENE_MAPPING[property_name][0]
            print(f"Updating scenes property: {scene_property_name} = {value}")
            
            # 모든 씬에 적용
            for scene in bpy.data.scenes:
                if hasattr(scene, scene_property_name):
                    setattr(scene, scene_property_name, value)
                    print(f"Updated scene {scene.name}.{scene_property_name}")
    except Exception as e:
        print(f"Error updating scenes property {property_name}: {e}")
        import traceback
        traceback.print_exc()

# 업데이트 콜백 생성 함수
def create_update_callback(property_name):
    """특정 속성에 대한 업데이트 콜백 생성"""
    def update_callback(self, context):
        value = getattr(self, property_name)
        update_scenes_property(property_name, value)
    return update_callback

class DefaultAddonPreferences(AddonPreferences):
    bl_idname = config.ADDON_ID

    # 오퍼레이터 기본값 설정 (UI에서 조정 가능)
    default_cube_size: FloatProperty(
        name="Default Cube Size",
        description="Set the default size of the cube for new scenes",
        default=DEFAULT_CUBE_SIZE,
        min=0.1,
        update=create_update_callback('default_cube_size')
    )
    
    # 벽체 설정
    default_wall_height: FloatProperty(
        name="Default Wall Height",
        description="Set the default height of walls for new scenes",
        default=DEFAULT_WALL_HEIGHT,
        min=0.1,
        max=10.0,
        unit='LENGTH',
        update=create_update_callback('default_wall_height')
    )
    
    default_wall_thickness: FloatProperty(
        name="Default Wall Thickness",
        description="Set the default thickness of walls for new scenes",
        default=DEFAULT_WALL_THICKNESS,
        min=0.01,
        max=1.0,
        unit='LENGTH',
        update=create_update_callback('default_wall_thickness')
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
        
        # 벽체 설정 섹션
        box = layout.box()
        box.label(text="Wall Settings")
        box.prop(self, "default_wall_height")
        box.prop(self, "default_wall_thickness")
        
        # 기타 설정
        box = layout.box()
        box.label(text="Other Settings")
        box.prop(self, "use_snapping")
        
        # 설명 추가
        layout.label(text="Changes will affect new scenes and existing scenes when restarting Blender")