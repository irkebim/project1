import importlib
import os
import time
import threading
import sys
from typing import List, Set, Optional

# 전역 변수
_running = False
_thread = None

def get_modules_to_watch() -> List[str]:
    """감시할 모듈 목록을 자동으로 생성"""
    try:
        print("Auto-reload: Getting modules to watch")
        # 현재 모듈의 패키지 이름 추출
        package_name = __package__
        if not package_name:
            # __package__가 비어있으면 파일 경로에서 추론
            current_dir = os.path.dirname(os.path.dirname(__file__))
            package_name = os.path.basename(current_dir)
            print(f"Package name from path: {package_name}")
        elif "." in package_name:
            # utils.auto_reload 같은 형태면 루트 패키지만 사용
            package_name = package_name.split(".")[0]
            print(f"Root package name: {package_name}")
        
        # 패키지 루트 디렉토리 찾기
        if package_name in sys.modules:
            root_module = sys.modules[package_name]
            if hasattr(root_module, "__file__"):
                current_dir = os.path.dirname(os.path.abspath(root_module.__file__))
                print(f"Root dir from module: {current_dir}")
            else:
                current_dir = os.path.dirname(os.path.dirname(__file__))
                print(f"Root dir from current file: {current_dir}")
        else:
            current_dir = os.path.dirname(os.path.dirname(__file__))
            print(f"Root dir from current file (fallback): {current_dir}")
        
        modules_to_watch = []
        
        # 하위 폴더 검색
        for folder in ["operators", "panels", "preferences"]:
            folder_path = os.path.join(current_dir, folder)
            if os.path.isdir(folder_path):
                print(f"Checking folder: {folder_path}")
                for filename in os.listdir(folder_path):
                    if filename.endswith(".py") and not filename.startswith("__"):
                        module_name = f".{folder}.{filename[:-3]}"
                        modules_to_watch.append(module_name)
                        print(f"Added module to watch: {module_name}")
            else:
                print(f"Folder not found: {folder_path}")
        
        print(f"Total modules to watch: {len(modules_to_watch)}")
        return modules_to_watch
    except Exception as e:
        print(f"Error finding modules to watch: {e}")
        import traceback
        traceback.print_exc()
        # 오류 발생 시 기본 모듈 목록 반환
        basic_modules = [
            ".operators.cube",
            ".panels.panel_main",
            ".preferences.default_values"
        ]
        print(f"Using basic module list: {basic_modules}")
        return basic_modules

# 감시할 모듈 목록 (지연 초기화)
WATCHED_MODULES = None

def get_watched_modules() -> List[str]:
    """감시할 모듈 목록 반환 (지연 초기화)"""
    global WATCHED_MODULES
    if WATCHED_MODULES is None:
        WATCHED_MODULES = get_modules_to_watch()
    return WATCHED_MODULES

def reload_modules():
    """모듈을 다시 로드"""
    print("♻️ [AutoReload] Reloading modules...")
    
    # 모듈 목록 가져오기
    modules_to_reload = get_watched_modules()
    success_count = 0
    error_count = 0
    
    # 패키지 이름 찾기
    package_name = __package__ or "irkebim"
    if "." in package_name:
        # utils.auto_reload 같은 형태면 루트 패키지만 사용
        package_name = package_name.split(".")[0]
    
    print(f"Using package name for reloading: {package_name}")
    
    # 모듈 리로드
    for modname in modules_to_reload:
        try:
            full_name = package_name + modname  # irkebim.operators.cube
            print(f"Reloading module: {full_name}")
            module = importlib.import_module(full_name)
            importlib.reload(module)
            success_count += 1
        except ImportError as e:
            print(f"❌ [AutoReload] Failed to reload {modname}: {e}")
            error_count += 1
        except Exception as e:
            print(f"❌ [AutoReload] Error reloading {modname}: {e}")
            import traceback
            traceback.print_exc()
            error_count += 1
    
    print(f"✅ [AutoReload] Reloaded {success_count} modules, {error_count} failed")

def _get_monitored_paths() -> Set[str]:
    """감시할 모든 파일 경로 세트 가져오기"""
    try:
        # 패키지 이름 찾기
        package_name = __package__ or "irkebim"
        if "." in package_name:
            # utils.auto_reload 같은 형태면 루트 패키지만 사용
            package_name = package_name.split(".")[0]
        
        # 패키지 루트 디렉토리 찾기
        current_dir = None
        if package_name in sys.modules:
            root_module = sys.modules[package_name]
            if hasattr(root_module, "__file__"):
                current_dir = os.path.dirname(os.path.abspath(root_module.__file__))
        
        if current_dir is None:
            current_dir = os.path.dirname(os.path.dirname(__file__))
        
        paths = set()
        
        # 하위 폴더 추가
        for folder in ["operators", "panels", "preferences"]:
            folder_path = os.path.join(current_dir, folder)
            if os.path.isdir(folder_path):
                paths.add(folder_path)
        
        return paths
    except Exception as e:
        print(f"[AutoReload] Error finding folders to monitor: {e}")
        import traceback
        traceback.print_exc()
        
        # 오류 발생 시 현재 디렉토리 기준으로 경로 찾기 시도
        try:
            current_dir = os.path.dirname(os.path.dirname(__file__))
            paths = set()
            for folder in ["operators", "panels", "preferences"]:
                folder_path = os.path.join(current_dir, folder)
                if os.path.isdir(folder_path):
                    paths.add(folder_path)
            return paths
        except:
            # 모든 방법이 실패하면 빈 세트 반환
            return set()

def _watch():
    """파일 변경 감시 쓰레드"""
    last_mtime = {}
    global _running
    
    # 초기 경로 설정
    monitored_paths = _get_monitored_paths()
    print(f"👀 [AutoReload] Watching folders: {monitored_paths}")
    
    while _running:
        time.sleep(0.5)
        
        # 변경감지 코드 예외처리
        try:
            # 매 반복마다 경로 갱신 (폴더가 생성될 수 있음)
            if not monitored_paths:
                monitored_paths = _get_monitored_paths()
                if monitored_paths:
                    print(f"👀 [AutoReload] Found folders to watch: {monitored_paths}")
            
            for path in monitored_paths:
                if not os.path.exists(path):
                    continue
                    
                for filename in os.listdir(path):
                    if filename.endswith(".py") and not filename.startswith("__"):
                        filepath = os.path.join(path, filename)
                        try:
                            mtime = os.path.getmtime(filepath)
                            
                            if filepath not in last_mtime:
                                last_mtime[filepath] = mtime
                            elif last_mtime[filepath] != mtime:
                                last_mtime[filepath] = mtime
                                print(f"🔁 [AutoReload] Detected change in {filepath}")
                                reload_modules()
                                break
                        except FileNotFoundError:
                            continue
        except Exception as e:
            print(f"[AutoReload] Error in file watcher: {e}")
            import traceback
            traceback.print_exc()
            
            # 짧은 대기 후 계속
            time.sleep(1)

def start_watchdog():
    """파일 변경 감시 시작"""
    global _thread, _running
    
    # 이미 실행 중이면 중복 시작 방지
    if _thread and _thread.is_alive():
        print("[AutoReload] Watcher already running")
        return
    
    # 초기화가 필요하면 수행
    get_watched_modules()
    
    try:
        _running = True
        _thread = threading.Thread(target=_watch, daemon=True)
        _thread.start()
        print("🚀 [AutoReload] Watcher started.")
    except Exception as e:
        print(f"❌ [AutoReload] Failed to start watcher: {e}")
        import traceback
        traceback.print_exc()
        _running = False

def stop_watchdog():
    """파일 변경 감시 중지"""
    global _running
    
    if _running:
        _running = False
        print("🛑 [AutoReload] Watcher stopped.")
        
    # 스레드가 완전히 종료될 시간 부여
    time.sleep(0.1)