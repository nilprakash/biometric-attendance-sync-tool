import os
import sys
import logging

# 1. Detect how the program is running
IS_PYINSTALLER = getattr(sys, 'frozen', False)
IS_NUITKA = '__compiled__' in globals()

# Force the environment context to look inside the executable's folder
if IS_PYINSTALLER or IS_NUITKA:
    # Get the directory containing the actual .exe file
    exe_dir = os.path.dirname(sys.executable)
    
    # Force context inside the executable's folder
    sys.path.insert(0, exe_dir)
    os.chdir(exe_dir)
else:
    # Standard dev script execution (VS Code / uv venv)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

# 2. Configure logging to write to startup.log inside the app folder
log_file_path = "startup.log"

logging.basicConfig(
    filename=log_file_path,
    filemode='a',  # 'a' appends to logs, change to 'w' if you want a fresh log file on every launch
    level=logging.ERROR, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    import local_config as config # type: ignore
except ModuleNotFoundError:
    logging.error("Critical: 'local_config.py' file is completely missing! Please create it from the template.")
    sys.exit(1)
except SyntaxError as e:
    logging.error(f"Critical: Syntax error inside 'local_config.py' on line {e.lineno}! Detailed error: {e.msg}")
    sys.exit(1)
except Exception as e:
    logging.error(f"Critical: Failed to load 'local_config.py' due to a runtime error: {e}")
    sys.exit(1)


import time
from pathlib import Path
from SMWinservice import SMWinservice
from erpnext_sync import main

class PythonCornerExample(SMWinservice):
    _svc_name_ = "ERPNextBiometricPushService"
    _svc_display_name_ = "ERPNext Biometric Push Service"
    _svc_description_ = "Service to push biometric data from device to ERPNext"

    def start(self):
        self.isrunning = True

    def stop(self):
        self.isrunning = False

    def main(self):
        while self.isrunning:
            main()
            time.sleep(15)

if __name__ == '__main__':
    try:
        PythonCornerExample.parse_command_line()
    except Exception as e:
        logging.error(f"Critical: Failed to load initialize from main of erpnext_sync_win.py due to a runtime error: {e}")
        sys.exit(1)
