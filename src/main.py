import logging
import sys
from os.path import isfile

import globals
import util.process
from app_manager import AppManager
from globals import get_debug, get_version
from util.log_setup import setup_logging

if __name__ == "__main__":
    print("Application started")
    setup_logging("main")

    if not isfile(util.resource_path(".env")):
        print(".env file not found, unable to get API keys and data")
        sys.exit()

    logger = logging.getLogger("discord_fm").getChild(__name__)
    logger.info(
        f' -------- Discord.fm version {get_version()} {"(debug mode)" if get_debug() else ""} -------- '
    )

    sys.excepthook = util.process.handle_exception

    globals.manager = AppManager()
    try:
        globals.manager.start()
    except KeyboardInterrupt:
        globals.manager.close()
        sys.exit()
