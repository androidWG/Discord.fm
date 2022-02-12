import sys
import globals
import util.process
from app_manager import AppManager
from util.log_setup import setup_logging

if __name__ == "__main__":
    sys.excepthook = util.process.handle_exception
    setup_logging("main")

    globals.manager = AppManager()
    globals.manager.start()
