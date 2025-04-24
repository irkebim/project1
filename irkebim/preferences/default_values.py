# irkebim/preferences/default_values.py
import bpy
from bpy.types import AddonPreferences
from bpy.props import FloatProperty
from .. import config

# 기본값 정의
DEFAULT_CUBE_SIZE = 2.0
DEFAULT_WALL_HEIGHT = 2.4
DEFAULT_WALL_THICKNESS = 0.2
DEFAULT_IMAGE_OPACITY = 0.5

# 환경설정 속성과 씬 속성 간 매핑
PREFERENCES_TO_SCENE_MAPPING = {
    'default_cube_size': ('cube_custom_size', DEFAULT_CUBE_SIZE),
    'default_wall_height': ('wall_default_height', DEFAULT_WALL_HEIGHT),
    'default_wall_thickness': ('wall_thickness', DEFAULT_WALL_THICKNESS),
}

# 씬 속성 동기화 함수
def update_scenes_property(property_name, value):
    try:
        if property_name in PREFERENCES_TO_SCENE_MAPPING:
            scene_prop = PREFERENCES_TO_SCENE_MAPPING[property_name][0]
            for scene in bpy.data.scenes:
                if hasattr(scene, scene_prop):
                    setattr(scene, scene_prop, value)
    except Exception as e:
        print(f"[IRKE] Failed to update scenes: {property_name} - {e}")

def create_update_callback(property_name):
    def update_callback(self, context):
        value = getattr(self, property_name)
        update_scenes_property(property_name, value)
    return update_callback

class DefaultAddonPreferences(AddonPreferences):
    bl_idname = config.ADDON_ID

    default_cube_size: FloatProperty(
        name="Default Cube Size",
        description="Default cube size for modeling",
        default=DEFAULT_CUBE_SIZE,
        min=0.1,
        update=create_update_callback('default_cube_size')
    )

    default_wall_height: FloatProperty(
        name="Wall Height",
        description="Default wall height for modeling",
        default=DEFAULT_WALL_HEIGHT,
        min=0.1,
        max=10.0,
        unit='LENGTH',
        update=create_update_callback('default_wall_height')
    )

    default_wall_thickness: FloatProperty(
        name="Wall Thickness",
        description="Default wall thickness",
        default=DEFAULT_WALL_THICKNESS,
        min=0.01,
        max=1.0,
        unit='LENGTH',
        update=create_update_callback('default_wall_thickness')
    )

    image_opacity: FloatProperty(
        name="Image Opacity",
        description="Opacity of the imported plan image",
        default=DEFAULT_IMAGE_OPACITY,
        min=0.0,
        max=1.0
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Modeling Defaults")
        box.prop(self, "default_cube_size")

        box = layout.box()
        box.label(text="Wall Defaults")
        box.prop(self, "default_wall_height")
        box.prop(self, "default_wall_thickness")

        box = layout.box()
        box.label(text="Import Settings")
        box.prop(self, "image_opacity")

        layout.label(text="Settings apply to new or synced scenes.")
