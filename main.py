import sys
import globals
import util.process
from app_manager import AppManager
from util.log_setup import setup_logging

if __name__ == "__main__":
    setup_logging("main")
    sys.excepthook = util.process.handle_exception

    globals.manager = AppManager()
    try:
        globals.manager.start()
    except KeyboardInterrupt:
        globals.manager.close()
        sys.exit()
