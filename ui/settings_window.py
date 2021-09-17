import logging
import os
from platform import system

from settings import local_settings
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, \
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget
from util import process, open_logs_folder, resource_path, check_dark_mode


class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.setWindowTitle("Discord.fm Settings")

        icon_color = "white" if check_dark_mode() else "black"
        icon_path = os.path.join("resources", f"{icon_color}", "settings.png")

        icon = QIcon(resource_path(icon_path, ".."))
        self.setWindowIcon(icon)
        self.setMaximumSize(270, 200)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        username_layout = QHBoxLayout()
        username_layout.setSpacing(7)
        self.username_input = QLineEdit(placeholderText="Username")
        self.username_input.editingFinished.connect(
            lambda: self.save_setting("username", self.username_input.text()))
        username_layout.addWidget(QLabel("Last.fm Username"))
        username_layout.addWidget(self.username_input)

        cooldown_layout = QHBoxLayout()
        cooldown_layout.setSpacing(7)
        self.cooldown_spinner = QSpinBox(minimum=2, maximum=60, value=2)
        self.cooldown_spinner.valueChanged.connect(
            lambda: self.save_setting("cooldown", self.cooldown_spinner.value()))
        cooldown_layout.addWidget(QLabel("Cooldown"))
        cooldown_layout.addWidget(self.cooldown_spinner)
        cooldown_layout.addWidget(QLabel("seconds"))
        cooldown_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(7)
        self.logs_button = QPushButton("Open Logs Folder")
        self.logs_button.clicked.connect(open_logs_folder)
        self.service_button = QPushButton("Start Service")
        self.service_button.clicked.connect(
            lambda: process.start_stop_service("discord_fm", "discord_fm.exe", "Discord.fm"))
        buttons_layout.addWidget(self.logs_button)
        buttons_layout.addWidget(self.service_button)

        self.tray_icon_check = QCheckBox("Show tray icon")
        self.tray_icon_check.stateChanged.connect(
            lambda: self.save_setting("tray_icon", self.tray_icon_check.isChecked()))

        # noinspection PyTypeChecker
        self.auto_update_check = QCheckBox("Automatically download and install updates", enabled=False)
        self.auto_update_check.stateChanged.connect(
            lambda: self.save_setting("auto_update", self.auto_update_check.isChecked()))
        self.status_label = QLabel("Waiting...")

        layout.addLayout(username_layout)
        layout.addLayout(cooldown_layout)
        layout.addWidget(self.tray_icon_check)
        layout.addWidget(self.auto_update_check)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.status_label)

        self.set_running_status()

        self.timer = QTimer()
        self.timer.timeout.connect(self.set_running_status)
        self.timer.start(1000)

        self.load_settings()
        self.setLayout(layout)

    @staticmethod
    def save_setting(name, value):
        local_settings.define(name, value)

    def load_settings(self):
        settings_dict = local_settings.settings_dict
        self.username_input.setText(settings_dict["username"])
        self.cooldown_spinner.setValue(settings_dict["cooldown"])
        self.tray_icon_check.setChecked(settings_dict["tray_icon"])
        self.auto_update_check.setChecked(settings_dict["auto_update"])

    def set_running_status(self):
        logging.debug("Getting running status...")

        if process.check_process_running("discord_fm"):
            self.status_label.setText("Running")
            self.service_button.setText("Stop Service")
        else:
            self.status_label.setText("Stopped")
            self.service_button.setText("Start Service")

        self.status_label.repaint()
