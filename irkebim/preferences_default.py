# preferences_default.py
import bpy
from bpy.types import AddonPreferences
from bpy.props import FloatProperty
from . import config

class DefaultAddonPreferences(AddonPreferences):
    bl_idname = config.ADDON_ID

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
