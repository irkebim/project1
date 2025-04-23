# irkebim/auto_reload.py
import importlib
import os
import time
import threading

WATCHED_MODULES = [
    ".operator_cube",
    ".panel_main",
    ".preferences_default",
]

_running = False
_thread = None

def reload_modules():
    print("♻️ [AutoReload] Reloading modules...")
    for modname in WATCHED_MODULES:
        try:
            full_name = __package__ + modname
            module = importlib.import_module(full_name)
            importlib.reload(module)
            print(f"✅ [AutoReload] Reloaded: {modname}")
        except Exception as e:
            print(f"❌ [AutoReload] Failed to reload {modname}: {e}")

def _watch(path):
    print(f"👀 [AutoReload] Watching folder: {path}")
    last_mtime = {}
    global _running
    while _running:
        time.sleep(1)
        for fname in os.listdir(path):
            if fname.endswith(".py"):
                fpath = os.path.join(path, fname)
                try:
                    mtime = os.path.getmtime(fpath)
                    if fname not in last_mtime:
                        last_mtime[fname] = mtime
                    elif last_mtime[fname] != mtime:
                        last_mtime[fname] = mtime
                        print(f"🔁 [AutoReload] Detected change in {fname}")
                        reload_modules()
                except FileNotFoundError:
                    continue

def start_watchdog():
    global _thread, _running
    if _thread and _thread.is_alive():
        return
    _running = True
    _thread = threading.Thread(target=_watch, args=(os.path.dirname(__file__),), daemon=True)
    _thread.start()

def stop_watchdog():
    global _running
    _running = False
    print("🛑 [AutoReload] Watcher stopped.")
