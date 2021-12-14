import os
import sys
import util
import wrappers.last_fm_user
from main import reload
from threading import Thread, get_ident, Timer
from settings import local_settings, get_version
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon, Qt, QCloseEvent
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QSlider, \
    QStatusBar, QVBoxLayout, QWidget, QMessageBox


class SettingsWindow(QMainWindow):
    starting = False
    stopping = False

    # noinspection PyArgumentList,PyTypeChecker
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.thread = None
        self.setWindowTitle("Discord.fm Settings")

        icon_color = "white" if util.check_dark_mode() else "black"
        icon_path = os.path.join("resources", f"{icon_color}", "settings.png")

        icon = QIcon(util.resource_path(icon_path, ".."))
        self.setWindowIcon(icon)
        self.setMaximumSize(270, 200)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        # region Username Input
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
        # endregion

        # region Cooldown Slider
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
        # endregion

        # region Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(7)

        self.logs_button = QPushButton("Open Logs Folder")
        self.logs_button.clicked.connect(util.open_logs_folder)
        self.service_button = QPushButton("Start Service")
        self.service_button.clicked.connect(
            lambda: self.call_start_stop())
        buttons_layout.addWidget(self.logs_button)
        buttons_layout.addWidget(self.service_button)

        # noinspection PyTypeChecker
        self.auto_update_check = QCheckBox("Automatically download and install updates")
        self.auto_update_check.stateChanged.connect(
            lambda: self.save_setting("auto_update", self.auto_update_check.isChecked()))
        # endregion

        # region Status Bar
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Waiting...")
        version_label = QLabel("v" + get_version())
        version_label.setAlignment(Qt.AlignRight)
        self.status_bar.addPermanentWidget(version_label, 1)
        self.status_bar.addWidget(self.status_label, 7)
        self.status_bar.setSizeGripEnabled(False)
        # endregion

        layout.addLayout(username_layout)
        layout.addWidget(self.username_status)
        layout.addLayout(cooldown_layout)
        layout.addWidget(self.auto_update_check)
        layout.addLayout(buttons_layout)

        # region Running Status Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.call_running_status)
        self.timer.start(1000)
        self.call_running_status()
        # endregion

        self.load_settings()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setStatusBar(self.status_bar)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._check_username()
        if not self.valid_username:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Confirmation")

            icon_color = "white" if util.check_dark_mode() else "black"
            icon_path = os.path.join("resources", f"{icon_color}", "settings.png")

            icon = QIcon(util.resource_path(icon_path, ".."))
            msg_box.setWindowIcon(icon)

            msg_box.setText("The username you set is not valid.")
            msg_box.setInformativeText("Please change it to a valid username.")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)
            msg_box.setIcon(QMessageBox.Warning)

            msg_box.exec()
            event.ignore()
        else:
            event.accept()

        reload()

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

    def _set_running_status(self):
        is_running = util.process.check_process_running("discord_fm")
        if is_running and not self.stopping:
            self.service_button.setEnabled(True)
            self.status_label.setText("Running")
            self.service_button.setText("Stop Service")
            self.starting = False
        elif not is_running and not self.starting:
            self.service_button.setEnabled(True)
            self.status_label.setText("Stopped")
            self.service_button.setText("Start Service")
            self.stopping = False

        self.status_bar.repaint()

    def call_running_status(self):
        if not getattr(sys, "frozen", False):
            self.status_label.setText("Cannot check if service is running")
            self.service_button.setText("Start Service")
            return

        Thread(target=self._set_running_status()).start()

    def call_start_stop(self):
        def _update():
            nonlocal self
            if self.starting or self.stopping:
                self._set_running_status()

        if util.process.check_process_running("discord_fm"):
            self.stopping = True
            self.service_button.setText("Stopping...")

            Thread(target=util.process.kill_process, args=["discord_fm"]).start()
        else:
            self.starting = True
            self.service_button.setText("Starting...")

            args = ["discord_fm", "discord_fm.exe", "Discord.fm.app", "main.py"]
            Thread(target=util.process.start_process, args=args).start()

        self.service_button.setEnabled(False)
        Timer(12, _update)

    def _check_username(self):
        if self.thread.ident != get_ident():
            return

        try:
            user = wrappers.last_fm_user.LastFMUser(self.username_input.text())
            user_valid = user.check_username()
        except ValueError:
            user_valid = False

        if user_valid:
            self.username_status.setText("Username is valid")
            self.valid_username = True
        elif not user_valid:
            self.username_status.setText("Invalid username")
            self.valid_username = False
        else:
            self.username_status.setText("No internet connection")
            self.valid_username = True

    def start_check_username(self):
        self.username_status.setText("Checking...")
        self.username_status.setVisible(True)

        self.thread = Thread(target=self._check_username)
        self.thread.start()
