# preferences_default.py
import bpy
from bpy.types import AddonPreferences
from bpy.props import FloatProperty
from . import config  # 수정: 상대 임포트 사용

class DefaultAddonPreferences(AddonPreferences):
    bl_idname = config.ADDON_ID  # config.py에 ADDON_ID 추가됨

    default_cube_size: FloatProperty(
        name="Default Cube Size",
        description="Set the default size of the cube",
        default=2.0,
        min=0.1,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "default_cube_size")

classes = (DefaultAddonPreferences,)

def register():
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass