import os
import platform
import subprocess
import sys
import psutil
import settings
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QCheckBox, QLabel, QLineEdit, QMainWindow, QPushButton, QSpinBox
from PySide6.QtCore import QFile, QIODevice, Slot, QTimer

status_lbl = None


def get_running_status():
    global status_lbl
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if "discord_fm".lower() in proc.name().lower():
                status_lbl.setText("Running")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            status_lbl.setText("Stopped")


@Slot()
def open_logs_folder():
    if platform.system() == "Windows":
        os.startfile(settings.logs_path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", settings.logs_path])
    else:
        subprocess.Popen(["xdg-open", settings.logs_path])


def set_username(value):
    settings.define("username", value)


def set_cooldown(value):
    settings.define("cooldown", value)


def set_tray(value):
    settings.define("tray_icon", bool(value))


def set_update(value):
    settings.define("auto_update", bool(value))


@Slot()
def say_hello():
    print("Hello!!")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    ui_file_name = "settings.ui"
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)

    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        sys.exit(-1)
    window.show()

    # Connect button methods
    service_btn = window.findChild(QPushButton, "serviceBtn")
    service_btn.clicked.connect(say_hello)

    logs_btn = window.findChild(QPushButton, "logsBtn")
    logs_btn.clicked.connect(open_logs_folder)

    username_txt = window.findChild(QLineEdit, "usernameLineEdit")
    username_txt.setText(settings.get("username"))
    username_txt.textChanged.connect(set_username)

    cooldown_txt = window.findChild(QSpinBox, "cooldownSpinBox")
    cooldown_txt.setValue(settings.get("cooldown"))
    cooldown_txt.valueChanged.connect(set_username)

    tray_icon_chk = window.findChild(QCheckBox, "trayIconCheckBox")
    tray_icon_chk.setChecked(settings.get("tray_icon"))
    tray_icon_chk.stateChanged.connect(set_tray)

    auto_update_chk = window.findChild(QCheckBox, "autoUpdateCheckBox")
    auto_update_chk.setChecked(settings.get("auto_update"))
    auto_update_chk.stateChanged.connect(set_update)

    status_lbl = window.findChild(QLabel, "processStatusLbl")

    check_process_timer = QTimer(window)
    check_process_timer.setInterval(1000)
    check_process_timer.timeout.connect(get_running_status)
    check_process_timer.start()

    sys.exit(app.exec())
