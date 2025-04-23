# 필요한 내장 모듈 임포트
import bpy

# bl_info 정의 - config.py와 버전 일치
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

# 모듈 관리자 가져오기
from .utils.module_manager import ModuleManager

# 패키지 목록
packages = ["operators", "panels", "preferences", "utils"]

# 모듈 관리자 초기화
manager = ModuleManager(__package__, packages)

# 등록/해제 함수
def register():
    manager.register_all()

def unregister():
    manager.unregister_all()

# 직접 실행 시 테스트
if __name__ == "__main__":
    register()