import atexit
import ctypes
import logging
import platform
import struct
import subprocess
import sys
import threading
import time
from threading import Thread

import pypresence

import loop_handler
import process
import settings
import ui
import util
import util.install
import util.updates
import version
import wrappers.discord_rp
from process import executable_info
from util.status import Status
from wrappers import system_tray_icon

logger = logging.getLogger("discord_fm").getChild(__name__)


class AppManager:
    name = "discord.fm"
    rpc_state = True
    second_user_notification_called = False

    def __init__(self):
        self.settings = settings.Settings("Discord.fm")
        self.status = Status(Status.STARTUP)

        if self.settings.get("username") == "":
            logger.critical(
                "No username found - please add a username to settings and restart the app"
            )
            self.open_settings(wait=True)

        self.tray_icon = system_tray_icon.SystemTrayIcon(self)
        self.loop = loop_handler.LoopHandler(self)
        self.discord_rp = wrappers.discord_rp.DiscordRP()

    def get_debug(self) -> bool:
        return self.settings.get("debug")

    def _perform_checks(self):
        if not util.is_frozen():
            logger.warning("Running in non-frozen mode")

        if process.check_process_running(
            "discord_fm", "discord.fm"
        ) and not util.arg_exists("--ignore-open"):
            logger.error("Discord.fm is already running")
            self.close()

        if self.settings.get("auto_update"):
            logger.debug("Checking for updates")

            latest, latest_asset = util.updates.get_newest_release(self)
            current = version.get_version(True)
            if (
                latest is not None
                and latest > current
                or util.arg_exists("--force-update")
            ):
                self.status = Status.UPDATING
                self.tray_icon.ti.update_menu()

                logger.info(
                    f"Found newer version (current v{current} vs. latest v{latest})"
                )
                path = util.updates.download_asset(self, latest_asset)

                installation = util.install.get_install()
                installation.install(path)
                logger.info("Quitting to allow installation of newer version")
                self.close()

        if util.arg_exists("-o"):
            logger.info('"-o" argument was found, opening settings')
            self.open_settings()

    def start(self):
        atexit.register(self.close)
        self._perform_checks()

        if self.status != Status.KILL:
            self.status = Status.ENABLED
            self.tray_icon.ti.update_menu()

            try:
                t = Thread(target=self.loop.handle_update, daemon=True)
                t.start()
                self.tray_icon.ti.run()
            except (KeyboardInterrupt, SystemExit):
                logger.info("Caught KeyboardInterrupt or SystemExit")

        self.close()

    def reload(self):
        logger.info("Reloading...")

        try:
            self.discord_rp.exit_rp()
        except (
            RuntimeError,
            AttributeError,
            AssertionError,
            pypresence.InvalidID,
        ) as e:
            logger.debug(
                "Exception catched when attempting to exit from Rich Presence",
                exc_info=e,
            )
        except NameError:
            return

        self.status = Status.DISABLED
        self.loop.reload_lastfm()
        self.status = Status.ENABLED

    def close(self):
        self.status = Status.KILL
        logger.info("Closing app...")

        try:
            self.discord_rp.exit_rp()
            self.tray_icon.ti.stop()
        except (
            RuntimeError,
            AttributeError,
            AssertionError,
            pypresence.InvalidID,
            NameError,
        ) as e:
            logger.debug("Exception caught when attempting to close app", exc_info=e)

        try:
            sc = self.loop.sc
            if not sc.empty():
                for event in sc.queue:
                    sc.cancel(event)
                    logger.debug(f'Event "{event.action}" canceled')
        except (AttributeError, NameError) as e:
            logger.debug(
                "Exception caught when attempting to flush global scheduler",
                exc_info=e,
            )

        sys.exit()

    def toggle_rpc(self, new_value: bool):
        self.rpc_state = new_value

        if self.rpc_state:
            self.status = Status.ENABLED
        else:
            self.status = Status.DISABLED
            self.discord_rp.disconnect()

        logger.info(f"Changed state to {self.rpc_state}")

    def attempt_to_connect_rp(self):
        if self.discord_rp.connected:
            logger.debug("Already connected to Discord")
            return

        logger.info("Attempting to connect to Discord")
        if process.check_process_running("Discord", "DiscordCanary"):
            try:
                self.discord_rp.connect()
                logger.info("Successfully connected to Discord")
            except (
                FileNotFoundError,
                pypresence.InvalidPipe,
                pypresence.DiscordNotFound,
                pypresence.DiscordError,
                ValueError,
                struct.error,
            ) as e:
                logger.debug(f"Received {e} when connecting to Discord RP")
            except PermissionError as e:
                if (
                    not self.second_user_notification_called
                    and platform.system() == "Windows"
                ):
                    logger.critical(
                        "Another user has Discord open, notifying user", exc_info=e
                    )

                    title = "Another user has Discord open"
                    message = (
                        "Discord.fm will not update your Rich Presence or theirs. Please close the other "
                        "instance before scrobbling with this user. "
                    )

                    util.basic_notification(title, message)
                    self.second_user_notification_called = True
        else:
            time.sleep(10)

    def disconnect_rp(self):
        if self.discord_rp.connected:
            self.discord_rp.disconnect()
        else:
            logger.debug("Already disconnected from Discord")

    def open_settings(self, wait: bool = False):
        if wait:
            self._create_settings_window()
        else:
            thread = threading.Thread(target=self._create_settings_window)
            thread.start()

    def _create_settings_window(self):
        logger.debug("Opening settings")

        # Set app ID so Windows will show the correct icon on the taskbar
        if platform.system() == "Windows":
            app_id = "com.androidwg.discordfm.ui"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        window = ui.SettingsWindow(self)
        window.mainloop()

    # From https://stackoverflow.com/a/16993115/8286014
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt) or issubclass(exc_type, SystemExit):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )
        logger.debug(f"Current status: {self.status}")

        if self.status != Status.KILL:
            path = executable_info.get_local_executable("discord_fm", "main.py")
            subprocess.Popen(path + ["--ignore-open"])

        self.close()
