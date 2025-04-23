import importlib
import os
import time
import threading
import glob
from typing import List, Set

def get_modules_to_watch() -> List[str]:
    """감시할 모듈 목록을 자동으로 생성"""
    current_dir = os.path.dirname(os.path.dirname(__file__))  # irkebim 루트 폴더
    modules_to_watch = []
    
    # 하위 폴더 검색
    for folder in ["operators", "panels", "preferences"]:
        folder_path = os.path.join(current_dir, folder)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_name = f".{folder}.{filename[:-3]}"
                    modules_to_watch.append(module_name)
    
    return modules_to_watch

# 감시할 모듈 목록
WATCHED_MODULES = get_modules_to_watch()

def reload_modules():
    """모듈을 다시 로드"""
    print("♻️ [AutoReload] Reloading modules...")
    for modname in WATCHED_MODULES:
        try:
            full_name = __package__.rsplit(".", 1)[0] + modname  # irkebim.utils -> irkebim
            module = importlib.import_module(full_name)
            importlib.reload(module)
            print(f"✅ [AutoReload] Reloaded: {modname}")
        except ImportError as e:
            print(f"❌ [AutoReload] Failed to reload {modname}: {e}")

_running = False
_thread = None

def _get_monitored_paths() -> Set[str]:
    """감시할 모든 파일 경로 세트 가져오기"""
    current_dir = os.path.dirname(os.path.dirname(__file__))  # irkebim 루트 폴더
    paths = set()
    
    # 하위 폴더 추가
    for folder in ["operators", "panels", "preferences"]:
        folder_path = os.path.join(current_dir, folder)
        if os.path.isdir(folder_path):
            paths.add(folder_path)
    
    return paths

def _watch():
    """파일 변경 감시 쓰레드"""
    monitored_paths = _get_monitored_paths()
    print(f"👀 [AutoReload] Watching folders: {monitored_paths}")
    
    last_mtime = {}
    global _running
    
    while _running:
        time.sleep(0.5)
        
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

def start_watchdog():
    """파일 변경 감시 시작"""
    global _thread, _running
    if _thread and _thread.is_alive():
        return
    
    _running = True
    _thread = threading.Thread(target=_watch, daemon=True)
    _thread.start()

def stop_watchdog():
    """파일 변경 감시 중지"""
    global _running
    _running = False
    print("🛑 [AutoReload] Watcher stopped.")