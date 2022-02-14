import logging
import sys
import ctypes
import util.process
from sys import argv, exit
from platform import system
from util.log_setup import setup_logging
from settings_window import SettingsWindow
from PySide6.QtWidgets import QApplication

setup_logging("qt_settings")
logger = logging.getLogger("discord_fm").getChild(__name__)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt) or issubclass(exc_type, SystemExit):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


if __name__ == "__main__":
    sys.excepthook = util.process.handle_exception

    # Set app ID so Windows will show the correct icon on the taskbar
    if system() == "Windows":
        app_id = u"com.androidwg.discordfm.ui"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app = QApplication(argv)

    main_window = SettingsWindow()
    main_window.show()
    main_window.call_running_status()

    exit(app.exec())
