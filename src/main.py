import logging
import sys
import globals
import util.process
import packaging.version
from app_manager import AppManager
from os.path import isfile
from util.log_setup import setup_logging

__version = "0.7.0"
__debug = True


def get_version(parsed=False):
    if parsed:
        return packaging.version.parse(__version)
    else:
        return __version


def get_debug():
    return __debug


if __name__ == "__main__":
    print("Application started")
    setup_logging("main")

    if not isfile(util.resource_path(".env")):
        print(".env file not found, unable to get API keys and data")
        sys.exit()

    logger = logging.getLogger("discord_fm").getChild(__name__)
    logger.info(f' -------- Discord.fm version {get_version()} {"(debug mode)" if get_debug() else ""} -------- ')

    sys.excepthook = util.process.handle_exception

    globals.manager = AppManager()
    try:
        globals.manager.start()
    except KeyboardInterrupt:
        globals.manager.close()
        sys.exit()
