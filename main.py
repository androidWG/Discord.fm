import logging
import sys
import globals
import util.process
from app_manager import AppManager
from util.log_setup import setup_logging
from settings import get_debug, get_version

if __name__ == "__main__":
    print("Application started")
    setup_logging("main")

    logger = logging.getLogger("discord_fm").getChild(__name__)
    logger.info(f' -------- Discord.fm version {get_version()} {"(debug mode)" if get_debug() else ""} -------- ')

    sys.excepthook = util.process.handle_exception

    globals.manager = AppManager()
    try:
        globals.manager.start()
    except KeyboardInterrupt:
        globals.manager.close()
        sys.exit()
