import os
import sys
import importlib
from typing import Dict, List, Any, Optional
import bpy

class ModuleManager:
    """애드온 모듈을 동적으로 관리하는 클래스"""
    
    def __init__(self, root_package: str, package_paths: List[str] = None):
        print(f"Initializing ModuleManager for {root_package}")
        self.root_package = root_package
        self.package_paths = package_paths or []
        self.modules = {}  # 이름: 모듈 객체
        self.special_modules = ["config", "auto_reload"]
        
        # 중요: 속성 미리 초기화
        self.config = None
        self.auto_reload = None
        self.registration = None
        
        # 유틸리티 모듈 먼저 로드
        self._load_utils()
        
        # 특별 모듈 로드 (순서 조정: config를 먼저 로드)
        print("Loading config module")
        config_module = self._safe_import_module("config", self.root_package)
        if config_module:
            self.config = config_module
            self.modules['config'] = config_module
            print("Config module loaded successfully")
        else:
            print("Failed to load config module")
        
        # 나머지 특별 모듈 로드
        for name in self.special_modules:
            if name != "config":  # config는 이미 로드했으므로 제외
                print(f"Loading special module: {name}")
                self._safe_import_module(name, self.root_package)
        
        # 모든 모듈 로드
        print("Loading all modules")
        self.load_all_modules()
        
        # 등록 관리자 가져오기
        print("Setting up registration manager")
        self.registration = self.get_module("utils.registration")
        if not self.registration:
            try:
                from . import registration
                self.registration = registration
                print("Loaded registration from local import")
            except ImportError:
                print("Registration module not found")
                self.registration = None
                
        # auto_reload 모듈 가져오기
        print("Setting up auto_reload module")
        self.auto_reload = self.get_module("utils.auto_reload")
        if not self.auto_reload:
            print("auto_reload not found in modules, trying direct imports")
            try:
                # 모듈이 루트에 있을 수도 있음
                if "auto_reload" in self.modules:
                    self.auto_reload = self.modules["auto_reload"]
                    print("Found auto_reload in modules")
                else:
                    # 직접 임포트 시도
                    try:
                        module_name = f"{self.root_package}.utils.auto_reload"
                        print(f"Trying to import auto_reload from {module_name}")
                        self.auto_reload = importlib.import_module(module_name)
                        print("Imported auto_reload from utils")
                    except ImportError as e:
                        print(f"Failed to import from utils: {e}")
                        try:
                            module_name = f"{self.root_package}.auto_reload"
                            print(f"Trying to import auto_reload from {module_name}")
                            self.auto_reload = importlib.import_module(module_name)
                            print("Imported auto_reload from root package")
                        except ImportError as e:
                            print(f"Failed to import from root: {e}")
                            print("Auto-reload module not found, hot-reload will be disabled")
                            self.auto_reload = None
            except Exception as e:
                print(f"Error setting up auto_reload: {e}")
                self.auto_reload = None
                
        print("ModuleManager initialization completed")
    
    def _get_base_dir(self) -> str:
        """루트 패키지 디렉토리 가져오기"""
        # 패키지 내 __init__.py 파일 경로를 기준으로 루트 디렉토리 찾기
        root_module = sys.modules.get(self.root_package)
        if root_module and hasattr(root_module, "__file__"):
            return os.path.dirname(os.path.abspath(root_module.__file__))
        else:
            # 대체 방법: 현재 파일 기준으로 부모 디렉토리 찾기
            current_dir = os.path.dirname(__file__)  # utils 폴더
            return os.path.dirname(current_dir)  # 상위 폴더 (루트)
    
    def _load_utils(self):
        """유틸리티 모듈 로드"""
        try:
            base_dir = self._get_base_dir()
            utils_path = os.path.join(base_dir, "utils")
            print(f"Loading utilities from {utils_path}")
            
            if os.path.exists(utils_path):
                for filename in os.listdir(utils_path):
                    if filename.endswith(".py") and not filename.startswith("__"):
                        name = filename[:-3]
                        print(f"Loading utility module: {name}")
                        self._safe_import_module(name, f"{self.root_package}.utils")
        except Exception as e:
            print(f"Error in _load_utils: {e}")
            import traceback
            traceback.print_exc()
    
    def _safe_import_module(self, name: str, package: str) -> Optional[Any]:
        """안전하게 모듈 가져오기 (config 참조 없이)"""
        full_name = f"{package}.{name}"
        try:
            print(f"Attempting to import: {full_name}")
            if full_name in sys.modules:
                print(f"Reloading existing module: {full_name}")
                module = importlib.reload(sys.modules[full_name])
            else:
                print(f"Importing new module: {full_name}")
                module = importlib.import_module(f".{name}", package=package)
                
            # 모듈 맵에 추가 (패키지 접두사 제거)
            module_key = full_name.replace(f"{self.root_package}.", "", 1)
            self.modules[module_key] = module
            print(f"Successfully imported: {full_name} -> {module_key}")
            return module
        except ImportError as e:
            print(f"Failed to import {full_name}: {e}")
            return None
        except Exception as e:
            print(f"Error importing {full_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _import_module(self, name: str, package: str) -> Optional[Any]:
        """모듈 가져오기 (새로고침 또는 처음 임포트)"""
        return self._safe_import_module(name, package)  # 안전한 임포트 메서드 재사용
    
    def load_all_modules(self):
        """모든 모듈 로드"""
        try:
            base_dir = self._get_base_dir()
            
            # 패키지 경로 처리
            for package_path in self.package_paths:
                full_path = os.path.join(base_dir, package_path)
                if not os.path.exists(full_path):
                    print(f"Path does not exist: {full_path}")
                    continue
                    
                if package_path == "utils":  # utils는 이미 처리함
                    print("Skipping utils folder (already processed)")
                    continue
                
                print(f"Loading modules from {package_path}")
                package = f"{self.root_package}.{package_path}"
                
                # 디렉토리의 모든 Python 파일 처리
                for filename in os.listdir(full_path):
                    if filename.endswith(".py") and not filename.startswith("__"):
                        name = filename[:-3]
                        print(f"Loading module: {package}.{name}")
                        self._import_module(name, package)
        except Exception as e:
            print(f"Error in load_all_modules: {e}")
            import traceback
            traceback.print_exc()
    
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
        print("Initializing registration")
        self.registration.initialize(self.modules)
        print("Registering all classes and properties")
        self.registration.register_all()
        
        # 환경 설정에서 Scene 속성 초기화
        print("Syncing preferences to scenes")
        self._sync_preferences_to_scenes()
        
        # 개발 모드에서 자동 리로드 활성화
        if self.config and hasattr(self.config, "DEV_MODE") and self.config.DEV_MODE:
            print("Activating auto-reload (DEV_MODE is enabled)")
            if self.auto_reload and hasattr(self.auto_reload, "start_watchdog"):
                self.auto_reload.start_watchdog()
            else:
                print("Auto-reload module not available or missing start_watchdog function")
    
def _sync_preferences_to_scenes(self):
    """환경 설정의 값을 Scene 속성에 동기화 (자동화된 방식)"""
    if not self.config or not hasattr(self.config, "ADDON_ID"):
        print("Config module missing or ADDON_ID not defined")
        return
    
    try:
        # 오퍼레이터 설정 모듈 가져오기
        default_values_module = self.get_module("preferences.default_values")
        if not default_values_module:
            print("default_values module not found, cannot sync preferences")
            return
            
        # 매핑 정보 가져오기
        if not hasattr(default_values_module, "PREFERENCES_TO_SCENE_MAPPING"):
            print("PREFERENCES_TO_SCENE_MAPPING not found in default_values")
            return
            
        mapping = default_values_module.PREFERENCES_TO_SCENE_MAPPING
        print(f"Found {len(mapping)} properties to sync")
            
        # 애드온 설정에 접근
        addon_id = self.config.ADDON_ID
        print(f"Looking for preferences for addon: {addon_id}")
        preferences = bpy.context.preferences.addons.get(addon_id)
        
        # bpy.data.scenes 접근 가능 여부 확인
        if not hasattr(bpy.data, "scenes"):
            print("bpy.data.scenes not available, skipping sync")
            return
            
        # 각 매핑된 속성에 대해 동기화 수행
        for pref_property, (scene_property, default_value) in mapping.items():
            # 환경설정에서 값 가져오기 또는 기본값 사용
            if preferences and preferences.preferences:
                if hasattr(preferences.preferences, pref_property):
                    value = getattr(preferences.preferences, pref_property)
                    print(f"Using preference value for {pref_property}: {value}")
                else:
                    value = default_value
                    print(f"Preference {pref_property} not found, using default: {value}")
            else:
                value = default_value
                print(f"No preferences found, using default for {pref_property}: {value}")
            
            # 모든 씬에 적용
            for scene in bpy.data.scenes:
                if hasattr(scene, scene_property):
                    setattr(scene, scene_property, value)
                    print(f"Updated scene {scene.name}.{scene_property} = {value}")
                else:
                    print(f"Property {scene_property} not found in scene {scene.name}")
                
    except Exception as e:
        print(f"Error syncing preferences to scenes: {e}")
        import traceback
        traceback.print_exc()
    
    def unregister_all(self):
        """모든 모듈의 클래스 및 속성 등록 해제"""
        # 자동 리로드 중지
        print("Stopping auto-reload if active")
        if self.config and hasattr(self.config, "DEV_MODE") and self.config.DEV_MODE:
            if self.auto_reload and hasattr(self.auto_reload, "stop_watchdog"):
                self.auto_reload.stop_watchdog()
        
        # 등록 해제
        if not self.registration:
            print("Registration module not found, cannot unregister classes.")
            return
            
        print("Unregistering all classes and properties")
        self.registration.unregister_all()