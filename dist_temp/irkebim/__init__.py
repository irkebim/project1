# 필요한 내장 모듈 임포트
import bpy
import importlib

# bl_info 정의
bl_info = {
    "name": "IRKE BIM",
    "author": "js_lim",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > IRKE BIM",
    "description": "A powerful BIM tool for architectural modeling in Blender",
    "warning": "",
    "doc_url": "https://github.com/irkebim/myextension",
    "category": "3D View",
}

# 내부 모듈 임포트 - 반드시 bl_info 다음에 와야 함
if "auto_reload" in locals():
    importlib.reload(auto_reload)
    auto_reload.reload_modules()
else:
    from . import auto_reload

if "config" in locals():
    importlib.reload(config)
else:
    from . import config

if "operator_cube" in locals():
    importlib.reload(operator_cube)
else:
    from . import operator_cube

if "panel_main" in locals():
    importlib.reload(panel_main)
else:
    from . import panel_main

if "preferences_default" in locals():
    importlib.reload(preferences_default)
else:
    from . import preferences_default


# 등록/해제 함수
def register():
    # 모듈별 등록
    operator_cube.register()
    panel_main.register()
    preferences_default.register()
    
    # 개발 모드에서 자동 리로드 활성화
    if config.DEV_MODE:
        auto_reload.start_watchdog()
    
def unregister():
    # 자동 리로드 중지
    if config.DEV_MODE:
        auto_reload.stop_watchdog()
    
    # 모듈별 등록 해제
    preferences_default.unregister()
    panel_main.unregister()
    operator_cube.unregister()

# 직접 실행 시 테스트를 위한 코드
if __name__ == "__main__":
    register()