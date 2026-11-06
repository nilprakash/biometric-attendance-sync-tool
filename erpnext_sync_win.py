import os
import sys
import logging
import time
from pathlib import Path

# 1. Detect how the program is running
IS_PYINSTALLER = getattr(sys, 'frozen', False)
IS_NUITKA = '__compiled__' in globals()

# Force the environment context to look inside the executable's folder
if IS_PYINSTALLER or IS_NUITKA:
    exe_dir = os.path.dirname(sys.executable)
    sys.path.insert(0, exe_dir)
    os.chdir(exe_dir)
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

# 2. Configure logging (Fixed path relative to current runtime directory)
log_file_path = os.path.join(os.getcwd(), "startup.log")

logging.basicConfig(
    filename=log_file_path,
    filemode='a',
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

from SMWinservice import SMWinservice
from erpnext_sync import main
import win32serviceutil
import servicemanager

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
            try:
                main()
            except Exception as e:
                logging.error(f"Error inside primary execution loop: {e}")
            time.sleep(15)

if __name__ == '__main__':
    # CRITICAL NATIVE EXECUTION FIX:
    # When launched by Windows Service Manager, no command line args are passed
    if len(sys.argv) == 1:
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(PythonCornerExample)
            servicemanager.StartServiceCtrlDispatcher()
        except Exception as e:
            logging.error(f"Critical SCM Dispatcher Initialization failure: {e}")
            sys.exit(1)
    else:
        # Fall back to SMWinservice command line handling for: install, remove, start, stop
        try:
            PythonCornerExample.parse_command_line()
        except Exception as e:
            logging.error(f"Critical: Failed to handle command line flags: {e}")
            sys.exit(1)
