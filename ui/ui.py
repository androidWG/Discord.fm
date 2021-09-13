import sys

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication
from settings_window import SettingsWindow
from util.log_setup import setup_logging

setup_logging("qt_settings")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = SettingsWindow()
    main_window.show()
    main_window.get_running_status()

    sys.exit(app.exec())
