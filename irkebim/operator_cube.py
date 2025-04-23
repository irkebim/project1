# operator_cube.py
import bpy
from . import config

class CubeOperator(bpy.types.Operator):
    bl_idname = "mesh.add_custom_cube"
    bl_label = "Add Cube"
    bl_description = "Add a cube with the specified size"

    def execute(self, context):
        scene = context.scene

        size = scene.cube_custom_size
        
        bpy.ops.mesh.primitive_cube_add(size=size)
        return {'FINISHED'}

classes = (CubeOperator,)

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
