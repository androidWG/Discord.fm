import logging
import os
import platform
import sys
from os.path import abspath, isfile

import app_manager
import globals as g
import process
import util.log_setup

if __name__ == "__main__":
    print("Application started")
    g.load_settings()

    util.log_setup.setup_logging("main")

    logger = logging.getLogger("discord_fm").getChild(__name__)
    logger.info(
        f' -------- Discord.fm version {g.get_version()} {"(debug mode)" if g.get_debug() else ""} -------- '
    )

    logger.info(f'Current working path: "{abspath(os.curdir)}"')

    if not isfile(util.resource_path(".env")):
        logger.critical(".env file not found, unable to get API keys and data")
        sys.exit()

    if platform.system() == "Darwin" and process.check_process_running(
            "discord_fm", "discord.fm"
    ):
        logger.info("Discord.fm is already running, opening settings...")
        process.open_settings()
        sys.exit(2)

    sys.excepthook = process.handle_exception

    g.manager = app_manager.AppManager()
    try:
        g.manager.start()
    except KeyboardInterrupt:
        g.manager.close()
        sys.exit()
