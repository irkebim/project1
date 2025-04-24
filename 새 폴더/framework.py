import ast
import atexit
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
import hashlib
import glob

# 필요한 패키지 설치 함수
def install_if_missing(package):
    """Install a package if it's not already installed"""
    try:
        __import__(package)
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 필요한 패키지 설치
install_if_missing("watchdog")

# 상수 정의
ADDON_NAME = "irkebim"
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# 기본 설정 값
BLENDER_EXE_PATH = "C:/Program Files/Blender Foundation/Blender 4.4/blender.exe"
BLENDER_ADDON_PATH = "C:/Users/js11w/AppData/Roaming/Blender Foundation/Blender/4.4/scripts/addons/"
BLENDER_EXTENSION_PATH = "C:/Users/js11w/AppData/Roaming/Blender Foundation/Blender/4.4/extensions/user_default/"
RELEASE_DIR = os.path.join(PROJECT_ROOT, "releases")  # 기본 릴리즈 경로를 releases 폴더로 설정
TEST_RELEASE_DIR = os.path.join(PROJECT_ROOT, "dist_temp")
DEV_AS_ADDON = True
DIST_AS_EXTENSION = True

# config.ini에서 설정 읽기
CONFIG_FILEPATH = os.path.join(PROJECT_ROOT, 'config.ini')
if os.path.isfile(CONFIG_FILEPATH):
    try:
        from configparser import ConfigParser
        configParser = ConfigParser()
        configParser.read(CONFIG_FILEPATH, encoding='utf-8')

        if configParser.has_option('blender', 'exe_path'):
            BLENDER_EXE_PATH = configParser.get('blender', 'exe_path')

        if configParser.has_option('blender', 'addon_path'):
            BLENDER_ADDON_PATH = configParser.get('blender', 'addon_path')
            
        if configParser.has_option('blender', 'extension_path'):
            BLENDER_EXTENSION_PATH = configParser.get('blender', 'extension_path')

        if configParser.has_option('default', 'release_dir'):
            RELEASE_DIR = configParser.get('default', 'release_dir')
    except Exception as e:
        print(f"Error reading config.ini: {e}")
        print("Using default values.")

# 유틸리티 함수
def search_files(root_dir, extensions):
    """Search for files with specified extensions recursively"""
    result = []
    for ext in extensions:
        if not ext.startswith('.'):
            ext = '.' + ext
        for filename in glob.iglob(f"{root_dir}/**/*{ext}", recursive=True):
            result.append(filename)
    return result

def read_utf8(file_path):
    """Read a UTF-8 file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_utf8(file_path, content):
    """Write content to a UTF-8 file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_md5_folder(folder_path):
    """Get the MD5 hash of all files in a folder"""
    md5_hash = hashlib.md5()
    for file_path in sorted(search_files(folder_path, ['.py', '.toml', '.txt', '.json'])):
        with open(file_path, 'rb') as f:
            md5_hash.update(f.read())
    return md5_hash.hexdigest()

def is_subdirectory(path, potential_parent):
    """Check if path is a subdirectory of potential_parent"""
    path = os.path.abspath(path)
    potential_parent = os.path.abspath(potential_parent)
    return path.startswith(potential_parent)

def remove_folder_safely(folder_path):
    """안전하게 폴더 삭제를 시도하는 함수"""
    if not os.path.exists(folder_path):
        return True
        
    try:
        shutil.rmtree(folder_path)
        return True
    except PermissionError:
        print(f"Permission denied when trying to remove {folder_path}. Will retry...")
        time.sleep(1)  # 잠시 대기
        try:
            shutil.rmtree(folder_path)
            return True
        except Exception as e:
            print(f"Failed to remove {folder_path} after retry: {e}")
            return False
    except Exception as e:
        print(f"Failed to remove {folder_path}: {e}")
        return False

# 프레임워크 코드
_addon_md5__signature = "addon.txt"

# Code to be injected into Blender for hot reload functionality
start_up_command = """
import bpy
from bpy.app.handlers import persistent
import os
import sys
existing_addon_md5 = ""
try:
    bpy.ops.preferences.addon_enable(module="{addon_name}")
except Exception as e:
    print("Addon enable failed:", e)

def watch_update_tick():
    global existing_addon_md5
    if os.path.exists("{addon_signature}"):
        with open("{addon_signature}", "r") as f:
            addon_md5 = f.read()
        if existing_addon_md5 == "":
            existing_addon_md5 = addon_md5
        elif existing_addon_md5 != addon_md5:
            print("Addon file changed, start to update the addon")
            try:
                bpy.ops.preferences.addon_disable(module="{addon_name}")
                all_modules = sys.modules
                all_modules = dict(sorted(all_modules.items(),key= lambda x:x[0])) #sort them
                for k,v in all_modules.items():
                    if k.startswith("{addon_name}"):
                        del sys.modules[k]
                bpy.ops.preferences.addon_enable(module="{addon_name}")
            except Exception as e:
                print("Addon update failed:", e)
            existing_addon_md5 = addon_md5
            print("Addon updated")
    return 1.0

@persistent
def register_watch_update_tick(dummy):
    print("Watching for addon update...")
    bpy.app.timers.register(watch_update_tick)

register_watch_update_tick(None)
bpy.app.handlers.load_post.append(register_watch_update_tick)
"""

def get_addon_info(filename: str):
    """Extract bl_info from the addon's __init__.py"""
    file_content = read_utf8(filename)
    try:
        parsed_ast = ast.parse(file_content)
        for node in ast.walk(parsed_ast):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "bl_info":
                        return ast.literal_eval(node.value)
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return None

def execute_blender_script(args, addon_path):
    """Execute a script in Blender"""
    process = subprocess.Popen(args, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    try:
        for line in process.stderr:
            line: str
            if line.lstrip().startswith("File"):
                line = line.replace(addon_path, PROJECT_ROOT)
            sys.stderr.write(line)
    except KeyboardInterrupt:
        sys.stderr.write("interrupted, terminating the child process...\n")
    finally:
        process.terminate()
        process.wait()

def update_addon_for_test():
    """Update the addon in the Blender addon folder for testing"""
    # 애드온 경로 확인
    if not os.path.exists(BLENDER_ADDON_PATH):
        os.makedirs(BLENDER_ADDON_PATH, exist_ok=True)
        
    # 타겟 디렉토리 생성
    test_addon_path = os.path.join(BLENDER_ADDON_PATH, ADDON_NAME)
    
    # 기존 설치 제거
    if os.path.exists(test_addon_path):
        remove_folder_safely(test_addon_path)
    
    # 애드온 복사
    source_addon_path = os.path.join(PROJECT_ROOT, ADDON_NAME)
    shutil.copytree(source_addon_path, test_addon_path)
    
    # MD5 해시 생성
    addon_md5 = get_md5_folder(source_addon_path)
    write_utf8(os.path.join(test_addon_path, _addon_md5__signature), addon_md5)
    
    print(f"Addon updated in {test_addon_path}")
    return test_addon_path

def start_watch_for_update(stop_event):
    """Watch for file changes and update the addon"""
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    class FileUpdateHandler(FileSystemEventHandler):
        def __init__(self):
            super(FileUpdateHandler, self).__init__()
            self.has_update = False
            self.last_update_time = 0
            self.update_delay = 0.5  # 0.5초 딜레이 추가

        def on_any_event(self, event):
            source_path = event.src_path
            current_time = time.time()
            
            # .py 파일만 감시하고 애드온 폴더 내의 파일만 체크
            if source_path.endswith(".py") and ADDON_NAME in source_path:
                # 너무 빈번한 업데이트 방지
                if current_time - self.last_update_time > self.update_delay:
                    print(f"File changed: {source_path}")
                    self.has_update = True
                    self.last_update_time = current_time

        def clear_update(self):
            self.has_update = False

    path = os.path.join(PROJECT_ROOT, ADDON_NAME)
    event_handler = FileUpdateHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while not stop_event.is_set():
            time.sleep(0.5)  # 0.5초마다 체크
            if event_handler.has_update:
                try:
                    update_addon_for_test()
                    event_handler.clear_update()
                    print("Addon updated due to file changes")
                except Exception as e:
                    print(f"Error updating addon: {e}")
                    print(
                        "Addon update failed: Please make sure no other process is"
                        " using the addon folder. You might need to restart the test to update the addon in Blender.")
        print("Stop watching for update...")

    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()

def test_addon(enable_watch=True):
    """Test the addon in Blender with optional hot reload"""
    # 블렌더 경로 확인
    if not os.path.isfile(BLENDER_EXE_PATH):
        raise ValueError(f"Blender executable not found at {BLENDER_EXE_PATH}")
    
    # 애드온 업데이트
    test_addon_path = update_addon_for_test()
    
    # 종료 이벤트
    stop_event = threading.Event()
    thread = None
    
    # 테스트 종료 시 처리할 작업
    def exit_handler():
        print("Clean up resources...")
        if thread and thread.is_alive():
            stop_event.set()
            thread.join(timeout=1.0)  # 최대 1초 대기
        
        # 애드온 폴더를 삭제하지 않도록 설정 (개발 중에는 유지)
        # if os.path.exists(test_addon_path):
        #     try:
        #         shutil.rmtree(test_addon_path)
        #         print(f"Removed test addon from {test_addon_path}")
        #     except Exception as e:
        #         print(f"Failed to remove {test_addon_path}: {e}")
    
    # 종료 핸들러 등록
    atexit.register(exit_handler)
    
    if not enable_watch:
        print('Hot reload disabled, changes will not be automatically applied')
    else:
        # Start watching for file changes
        thread = threading.Thread(target=start_watch_for_update, args=(stop_event,))
        thread.daemon = True  # 메인 스레드 종료 시 함께 종료되도록 설정
        thread.start()

    python_script = start_up_command.format(addon_name=ADDON_NAME,
                                           addon_signature=os.path.join(test_addon_path,
                                                                       _addon_md5__signature).replace("\\", "/"))

    try:
        print(f"Starting Blender with addon {ADDON_NAME}")
        execute_blender_script([BLENDER_EXE_PATH, "--python-use-system-env", "--python-expr", python_script],
                              test_addon_path)
    finally:
        exit_handler()
        print("Test completed.")

def zip_folder(source_folder, output_name, is_extension=False):
    """Zip a folder for distribution"""
    import zipfile
    
    # 릴리즈 경로가 존재하는지 확인하고 생성
    if not os.path.exists(RELEASE_DIR):
        os.makedirs(RELEASE_DIR, exist_ok=True)
    
    output_filename = f"{output_name}.zip"
    output_path = os.path.join(RELEASE_DIR, output_filename)
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_folder)
                if not is_extension:
                    # For addon, include the folder name
                    arcname = os.path.join(os.path.basename(source_folder), arcname)
                zipf.write(file_path, arcname)
    
    print(f"Saved zip file to: {output_path}")
    return output_path

def release_addon(need_zip=True, with_timestamp=False, with_version=False, is_extension=None):
    """Release the addon as a zip file or folder"""
    # Use provided is_extension value or default to DIST_AS_EXTENSION
    if is_extension is None:
        is_extension = DIST_AS_EXTENSION
    
    # Prepare release directory
    if not os.path.exists(RELEASE_DIR):
        os.makedirs(RELEASE_DIR, exist_ok=True)
    
    # 임시 폴더 생성
    if not os.path.exists(TEST_RELEASE_DIR):
        os.makedirs(TEST_RELEASE_DIR, exist_ok=True)
    
    # Prepare temporary folder for release
    release_folder = os.path.join(TEST_RELEASE_DIR, ADDON_NAME)
    
    # 안전하게 기존 폴더 삭제
    if os.path.exists(release_folder):
        if not remove_folder_safely(release_folder):
            print("Warning: Could not remove existing folder. Will try to continue...")
    
    # 소스 애드온 경로
    source_addon_path = os.path.join(PROJECT_ROOT, ADDON_NAME)
    
    # 폴더 복사
    try:
        shutil.copytree(source_addon_path, release_folder)
    except Exception as e:
        print(f"Error copying addon files: {e}")
        # 다른 방식으로 시도
        os.makedirs(release_folder, exist_ok=True)
        for item in os.listdir(source_addon_path):
            s = os.path.join(source_addon_path, item)
            d = os.path.join(release_folder, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    
    # Read bl_info for version info if needed
    bl_info = None
    init_file = os.path.join(source_addon_path, "__init__.py")
    if with_version and os.path.exists(init_file):
        bl_info = get_addon_info(init_file)
    
    # Prepare zip filename
    zip_name = ADDON_NAME
    if is_extension:
        zip_name = f"{zip_name}_ext"
    
    if with_version and bl_info and 'version' in bl_info:
        version_str = '.'.join([str(x) for x in bl_info['version']])
        zip_name = f"{zip_name}_v{version_str}"
    
    if with_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"{zip_name}_{timestamp}"
    
    # Create zip file if needed
    if need_zip:
        zip_path = zip_folder(release_folder, zip_name, is_extension)
        print(f"Addon released: {zip_path}")
        
        # Extension mode: 배포를 위해 확장 디렉토리에 복사
        if is_extension and os.path.exists(BLENDER_EXTENSION_PATH):
            print(f"Copying extension to: {BLENDER_EXTENSION_PATH}")
            ext_folder = os.path.join(BLENDER_EXTENSION_PATH, ADDON_NAME)
            if os.path.exists(ext_folder):
                remove_folder_safely(ext_folder)
            
            try:
                shutil.copytree(release_folder, ext_folder)
            except Exception as e:
                print(f"Error copying to extension directory: {e}")
            
        return zip_path
    
    # If no zip needed, copy to final location
    final_folder = os.path.join(RELEASE_DIR, ADDON_NAME)
    if os.path.exists(final_folder):
        remove_folder_safely(final_folder)
    
    try:
        shutil.copytree(release_folder, final_folder)
    except Exception as e:
        print(f"Error copying to release directory: {e}")
    
    print(f"Addon released to folder: {final_folder}")
    
    # Extension mode: 배포를 위해 확장 디렉토리에 복사
    if is_extension and os.path.exists(BLENDER_EXTENSION_PATH):
        print(f"Copying extension to: {BLENDER_EXTENSION_PATH}")
        ext_folder = os.path.join(BLENDER_EXTENSION_PATH, ADDON_NAME)
        if os.path.exists(ext_folder):
            remove_folder_safely(ext_folder)
        
        try:
            shutil.copytree(release_folder, ext_folder)
        except Exception as e:
            print(f"Error copying to extension directory: {e}")
        
    return final_folder