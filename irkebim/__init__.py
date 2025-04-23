bl_info = {
    "name": "IRKE BIM",
    "author": "js_lim",
    "description": "BIM TOOLS",
    "blender": (4, 0, 0),
    "version": (0, 0, 1),
    "location": "",
    "doc_url": "",
    "warning": "",
    "category": "3D VIEW, object"
}

import bpy
from . import operator_cube
from . import panel_main
from . import preferences_default

def register():
    operator_cube.register()
    panel_main.register()
    preferences_default.register()

def unregister():
    operator_cube.unregister()
    panel_main.unregister()
    preferences_default.unregister()
