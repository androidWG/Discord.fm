import logging
import os
import sys
import last_fm
from threading import Thread, get_ident
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon, Qt, QCloseEvent
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSlider, QVBoxLayout, QWidget, \
    QMessageBox
from settings import local_settings
from util import check_dark_mode, open_logs_folder, process, resource_path


class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.thread = None
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
        self.username_input.textChanged.connect(lambda: self.start_check_username())
        self.username_input.editingFinished.connect(
            lambda: self.save_setting("username", self.username_input.text()))
        username_layout.addWidget(QLabel("Last.fm Username"))
        username_layout.addWidget(self.username_input)

        self.username_status = QLabel("Checking...")
        self.username_status.setContentsMargins(100, 0, 0, 0)
        self.username_status.setVisible(False)

        cooldown_value = local_settings.get("cooldown")
        cooldown_layout = QHBoxLayout()
        cooldown_layout.setSpacing(7)
        self.cooldown_label = QLabel(str(cooldown_value) + "s")
        self.cooldown_label.setFixedWidth(25)
        self.cooldown_slider = QSlider(minimum=2, maximum=30, value=cooldown_value, orientation=Qt.Horizontal)
        self.cooldown_slider.sliderReleased.connect(
            lambda: self.save_setting("cooldown", self.cooldown_slider.value()))
        self.cooldown_slider.valueChanged.connect(
            lambda: self.cooldown_label.setText(f"{self.cooldown_slider.value()}s"))
        cooldown_layout.addWidget(QLabel("Cooldown"))
        cooldown_layout.addWidget(self.cooldown_slider)
        cooldown_layout.addWidget(self.cooldown_label)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(7)
        self.logs_button = QPushButton("Open Logs Folder")
        self.logs_button.clicked.connect(open_logs_folder)
        self.service_button = QPushButton("Start Service")
        self.service_button.clicked.connect(
            lambda: process.start_stop_service("discord_fm", "discord_fm.exe", "Discord.fm.app", "main.py"))
        buttons_layout.addWidget(self.logs_button)
        buttons_layout.addWidget(self.service_button)

        # noinspection PyTypeChecker
        self.auto_update_check = QCheckBox("Automatically download and install updates")
        self.auto_update_check.stateChanged.connect(
            lambda: self.save_setting("auto_update", self.auto_update_check.isChecked()))
        self.status_label = QLabel("Waiting...")

        layout.addLayout(username_layout)
        layout.addWidget(self.username_status)
        layout.addLayout(cooldown_layout)
        layout.addWidget(self.auto_update_check)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.status_label)

        self.set_running_status()

        self.timer = QTimer()
        self.timer.timeout.connect(self.set_running_status)
        self.timer.start(1000)

        self.load_settings()
        self.setLayout(layout)

    # noinspection PySimplifyBooleanCheck
    def closeEvent(self, event: QCloseEvent) -> None:
        if not self.valid_username:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Confirmation")

            icon_color = "white" if check_dark_mode() else "black"
            icon_path = os.path.join("resources", f"{icon_color}", "settings.png")

            icon = QIcon(resource_path(icon_path, ".."))
            msg_box.setWindowIcon(icon)

            msg_box.setText("The username you set is not valid.")
            msg_box.setInformativeText("Do you want to change it now?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            msg_box.setIcon(QMessageBox.Question)

            if msg_box.exec() == QMessageBox.Yes:
                event.ignore()
        else:
            event.accept()

    @staticmethod
    def save_setting(name, value, *extra_func):
        local_settings.define(name, value)
        if extra_func is not None:
            for f in extra_func:
                f()

    def load_settings(self):
        settings_dict = local_settings.settings_dict
        self.username_input.setText(settings_dict["username"])
        self.cooldown_slider.setValue(settings_dict["cooldown"])
        self.auto_update_check.setChecked(settings_dict["auto_update"])

    def set_running_status(self):
        logging.debug("Getting running status...")

        if not getattr(sys, "frozen", False):
            self.status_label.setText("Cannot check if service is running")
            self.service_button.setText("Start Service")
            return

        if process.check_process_running("discord_fm"):
            self.status_label.setText("Running")
            self.service_button.setText("Stop Service")
        else:
            self.status_label.setText("Stopped")
            self.service_button.setText("Start Service")

        self.status_label.repaint()

    def _check_username(self):
        if self.thread.ident != get_ident():
            return

        try:
            user = last_fm.LastFMUser(self.username_input.text())
            user_valid = user.check_username()
        except ValueError:
            user_valid = False

        if user_valid:
            self.username_status.setText("Username is valid")
            self.valid_username = True
        elif user_valid == False:
            self.username_status.setText("Invalid username - check again")
            self.valid_username = False
        else:
            self.username_status.setText("Unable to check username - please verify your connection")
            self.valid_username = True

    def start_check_username(self):
        self.username_status.setText("Checking...")
        self.username_status.setVisible(True)

        self.thread = Thread(target=self._check_username)
        self.thread.start()
