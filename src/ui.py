import ctypes
import logging
import sys
from platform import system

import process
from globals import get_debug, get_version
from ui import SettingsWindow
from util.log_setup import setup_logging

setup_logging("settings")
logger = logging.getLogger("discord_fm").getChild(__name__)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt) or issubclass(exc_type, SystemExit):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


if __name__ == "__main__":
    sys.excepthook = process.handle_exception
    logger.info(
        f" -------- Discord.fm Settings UI version {get_version()}"
        f' {"(debug mode)" if get_debug() else ""} -------- '
    )

    # Set app ID so Windows will show the correct icon on the taskbar
    if system() == "Windows":
        app_id = "com.androidwg.discordfm.ui"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    window = SettingsWindow()
    window.mainloop()

    sys.exit()
