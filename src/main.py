import logging
import platform
import sys
from os.path import isfile

import app_manager
import globals
import util.log_setup
import process
from globals import get_debug, get_version

if __name__ == "__main__":
    print("Application started")
    util.log_setup.setup_logging("main")

    logger = logging.getLogger("discord_fm").getChild(__name__)
    logger.info(
        f' -------- Discord.fm version {get_version()} {"(debug mode)" if get_debug() else ""} -------- '
    )

    logger.info(f'Current working path: "{abspath(os.curdir)}"')

    if not isfile(util.resource_path(".env")):
        print(".env file not found, unable to get API keys and data")
        sys.exit()

    if platform.system() == "Darwin" and process.check_process_running("discord_fm", "discord.fm"):
        logger.info("Discord.fm is already running, opening settings...")
        process.open_settings()
        sys.exit(2)

    sys.excepthook = process.handle_exception

    globals.manager = app_manager.AppManager()
    try:
        globals.manager.start()
    except KeyboardInterrupt:
        globals.manager.close()
        sys.exit()
