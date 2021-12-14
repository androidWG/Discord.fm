import atexit
import logging
import os
import sys
import time
import tray
import loop
import util
import util.log_setup
import util.updates
from settings import local_settings
from wrappers import system_tray_icon
from util.updates import check_version_and_download
from util.log_setup import setup_logging


# From https://stackoverflow.com/a/16993115/8286014
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt) or issubclass(exc_type, SystemExit):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def check_first_load_and_username():
    no_username = local_settings.get("username") == ""
    if local_settings.first_load or no_username and util.is_frozen():
        logging.info("First load, opening settings UI and waiting for it to be closed...")
        util.open_settings()

        while not util.process.check_process_running("settings_ui"):
            pass

        while util.process.check_process_running("settings_ui"):
            time.sleep(1.5)
    elif no_username and not util.is_frozen():
        logging.critical("No username found - please add a username to settings and restart the app")
        tray.close_app()


if __name__ == "__main__":
    setup_logging("main")

    tray_icon = system_tray_icon.SystemTrayIcon(close_app)
    atexit.register(close_app)

    if util.process.check_process_running("discord_fm"):
        logging.info("Discord.fm is already running, opening settings")

        util.open_settings()
        tray.close_app()

    if util.updates.check_version_and_download():
        logging.info("Quitting to allow installation of newer version")
        tray.close_app()

    if not os.path.isfile(util.resource_path(".env")):
        logging.critical(".env file not found, unable to get API keys and data!")
        tray.close_app()

    if util.arg_exists("-o"):
        logging.info("\"-o\" argument was found, opening settings")
        util.open_settings()

    check_first_load_and_username()
    tray_icon.wait_for_discord()  # lgtm [py/unreachable-statement]

    try:
        loop.handle_update()
    except (KeyboardInterrupt, SystemExit):
        tray.close_app()

    sys.exit()
