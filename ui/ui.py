import sys
import ctypes
import util.process
from sys import argv, exit
from platform import system
from util.log_setup import setup_logging
from settings_window import SettingsWindow
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    sys.excepthook = util.process.handle_exception
    setup_logging("qt_settings")

    # Set app ID so Windows will show the correct icon on the taskbar
    if system() == "Windows":
        app_id = u"com.androidwg.discordfm.ui"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app = QApplication(argv)

    main_window = SettingsWindow()
    main_window.show()
    main_window.call_running_status()

    exit(app.exec())
