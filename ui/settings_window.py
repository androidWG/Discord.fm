import logging
import os
import subprocess
import psutil
import settings
from platform import system
from PySide6.QtCore import QSize, QTimer
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QSizePolicy, \
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget


def save_setting(name, value):
    settings.define(name, value)


def open_logs_folder():
    if system() == "Windows":
        os.startfile(settings.logs_path)
    elif system() == "Darwin":
        subprocess.Popen(["open", settings.logs_path])
    else:
        subprocess.Popen(["xdg-open", settings.logs_path])


def start_stop_service():
    print("bruh")


class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.setWindowTitle("Discord.fm Settings")

        layout = QVBoxLayout()
        layout.setSpacing(5)

        username_layout = QHBoxLayout()
        username_layout.setSpacing(7)
        self.username_input = QLineEdit(placeholderText="Username")
        self.username_input.textChanged.connect(lambda: save_setting("username", self.username_input.text()))
        username_layout.addWidget(QLabel("Last.fm Username"))
        username_layout.addWidget(self.username_input)

        cooldown_layout = QHBoxLayout()
        cooldown_layout.setSpacing(7)
        self.cooldown_spinner = QSpinBox(minimum=2, maximum=60, value=2)
        self.cooldown_spinner.valueChanged.connect(lambda: save_setting("cooldown", self.cooldown_spinner.value()))
        cooldown_layout.addWidget(QLabel("Cooldown"))
        cooldown_layout.addWidget(self.cooldown_spinner)
        cooldown_layout.addWidget(QLabel("seconds"))
        cooldown_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(7)
        self.logs_button = QPushButton("Open Logs Folder")
        self.logs_button.clicked.connect(open_logs_folder)
        self.service_button = QPushButton("Start Service")
        self.service_button.clicked.connect(start_stop_service)
        buttons_layout.addWidget(self.logs_button)
        buttons_layout.addWidget(self.service_button)

        self.tray_icon_check = QCheckBox("Show tray icon")
        self.tray_icon_check.stateChanged.connect(lambda: save_setting("tray_icon", self.tray_icon_check.isChecked()))
        self.auto_update_check = QCheckBox("Automatically download and install updates", enabled=False)
        self.auto_update_check.stateChanged.connect(
            lambda: save_setting("auto_update", self.auto_update_check.isChecked()))
        self.status_label = QLabel("Waiting...")

        layout.addLayout(username_layout)
        layout.addLayout(cooldown_layout)
        layout.addWidget(self.tray_icon_check)
        layout.addWidget(self.auto_update_check)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.status_label)

        self.get_running_status()

        self.timer = QTimer()
        self.timer.timeout.connect(self.get_running_status)
        self.timer.start(1000)

        self.setLayout(layout)

    def get_running_status(self):
        logging.debug("Getting running status...")

        self.status_label.setText("Stopped")
        for proc in psutil.process_iter():
            try:
                if "discord_fm" in proc.name().lower():
                    self.status_label.setText("Running")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        self.status_label.repaint()
