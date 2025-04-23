import os
import sys
import importlib
from typing import Dict, List, Any, Optional
import bpy

class ModuleManager:
    """애드온 모듈을 동적으로 관리하는 클래스"""
    
    def __init__(self, root_package: str, package_paths: List[str] = None):
        self.root_package = root_package
        self.package_paths = package_paths or []
        self.modules = {}  # 이름: 모듈 객체
        self.special_modules = ["config", "auto_reload"]
        
        # 유틸리티 모듈 먼저 로드
        self._load_utils()
        
        # 특별 모듈 로드
        for name in self.special_modules:
            self._import_module(name, self.root_package)
        
        # 모든 모듈 로드
        self.load_all_modules()
        
        # 등록 관리자 가져오기
        self.registration = self.get_module("utils.registration")
        if not self.registration:
            from . import registration
            self.registration = registration
            
        # auto_reload 모듈 가져오기
        self.auto_reload = self.get_module("utils.auto_reload")
        if not self.auto_reload:
            self.auto_reload = self.get_module("auto_reload")
        
        # config 모듈 가져오기
        self.config = self.get_module("config")
    
    def _get_base_dir(self) -> str:
        """루트 패키지 디렉토리 가져오기"""
        # 패키지 내 __init__.py 파일 경로를 기준으로 루트 디렉토리 찾기
        root_module = sys.modules.get(self.root_package)
        if root_module and hasattr(root_module, "__file__"):
            return os.path.dirname(os.path.abspath(root_module.__file__))
        else:
            # 대체 방법: 현재 파일 기준으로 부모 디렉토리 찾기
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def _load_utils(self):
        """유틸리티 모듈 로드"""
        base_dir = self._get_base_dir()
        utils_path = os.path.join(base_dir, "utils")
        
        if os.path.exists(utils_path):
            for filename in os.listdir(utils_path):
                if filename.endswith(".py") and not filename.startswith("__"):
                    name = filename[:-3]
                    self._import_module(name, f"{self.root_package}.utils")
    
    def _import_module(self, name: str, package: str) -> Optional[Any]:
        """모듈 가져오기 (새로고침 또는 처음 임포트)"""
        full_name = f"{package}.{name}"
        try:
            if full_name in sys.modules:
                module = importlib.reload(sys.modules[full_name])
            else:
                module = importlib.import_module(f".{name}", package=package)
                
            # 모듈 맵에 추가 (패키지 접두사 제거)
            module_key = full_name.replace(f"{self.root_package}.", "", 1)
            self.modules[module_key] = module
            return module
        except ImportError as e:
            print(f"Failed to import {full_name}: {e}")
            return None
    
    def load_all_modules(self):
        """모든 모듈 로드"""
        base_dir = self._get_base_dir()
        
        # 패키지 경로 처리
        for package_path in self.package_paths:
            full_path = os.path.join(base_dir, package_path)
            if not os.path.exists(full_path) or package_path == "utils":  # utils는 이미 처리함
                continue
            
            package = f"{self.root_package}.{package_path}"
            
            # 디렉토리의 모든 Python 파일 처리
            for filename in os.listdir(full_path):
                if filename.endswith(".py") and not filename.startswith("__"):
                    name = filename[:-3]
                    self._import_module(name, package)
    
    def get_module(self, name: str) -> Optional[Any]:
        """이름으로 모듈 가져오기"""
        return self.modules.get(name)
    
    def reload_modules(self, module_names: List[str] = None):
        """지정된 모듈(들) 다시 로드"""
        if not module_names:
            module_names = list(self.modules.keys())
        
        for name in module_names:
            if name in self.modules:
                full_name = f"{self.root_package}.{name}"
                if full_name in sys.modules:
                    try:
                        self.modules[name] = importlib.reload(sys.modules[full_name])
                        print(f"Reloaded module: {name}")
                    except Exception as e:
                        print(f"Error reloading {name}: {e}")
    
    def register_all(self):
        """모든 모듈의 클래스 및 속성 등록"""
        if not self.registration:
            print("Registration module not found, cannot register classes.")
            return
            
        # 등록 초기화 및 실행
        self.registration.initialize(self.modules)
        self.registration.register_all()
        
        # 환경 설정에서 Scene 속성 초기화
        self._sync_preferences_to_scenes()
        
        # 개발 모드에서 자동 리로드 활성화
        if self.config and hasattr(self.config, "DEV_MODE") and self.config.DEV_MODE:
            if self.auto_reload and hasattr(self.auto_reload, "start_watchdog"):
                self.auto_reload.start_watchdog()
    
    def _sync_preferences_to_scenes(self):
        """환경 설정의 값을 Scene 속성에 동기화"""
        if not self.config or not hasattr(self.config, "ADDON_ID"):
            return
            
        try:
            # 애드온 설정에 접근
            preferences = bpy.context.preferences.addons.get(self.config.ADDON_ID)
            if not preferences or not preferences.preferences:
                return
                
            # 모든 Scene에 적용
            for scene in bpy.data.scenes:
                # 큐브 크기 설정
                if hasattr(preferences.preferences, "default_cube_size") and hasattr(scene, "cube_custom_size"):
                    scene.cube_custom_size = preferences.preferences.default_cube_size
                    
                # 추가 속성도 비슷하게 처리할 수 있음
                
        except Exception as e:
            print(f"Error syncing preferences to scenes: {e}")
    
    def unregister_all(self):
        """모든 모듈의 클래스 및 속성 등록 해제"""
        # 자동 리로드 중지
        if self.config and hasattr(self.config, "DEV_MODE") and self.config.DEV_MODE:
            if self.auto_reload and hasattr(self.auto_reload, "stop_watchdog"):
                self.auto_reload.stop_watchdog()
        
        # 등록 해제
        if not self.registration:
            print("Registration module not found, cannot unregister classes.")
            return
            
        self.registration.unregister_all()