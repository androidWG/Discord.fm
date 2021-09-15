import ctypes
from platform import system
from sys import argv, exit
from PySide6.QtWidgets import QApplication
from settings_window import SettingsWindow
from util.log_setup import setup_logging

setup_logging("qt_settings")

if __name__ == "__main__":
    # Set app ID so Windows will show the correct icon on the taskbar
    if system() == "Windows":
        app_id = u"com.androidwg.discordfm.ui"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    app = QApplication(argv)

    main_window = SettingsWindow()
    main_window.show()
    main_window.set_running_status()

    exit(app.exec())
