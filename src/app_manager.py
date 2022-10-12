import atexit
import logging
import platform
import struct
import subprocess
import sys
import time
from threading import Thread

import packaging.version
import pypresence

import loop_handler
import process
import settings
import util
import util.install
import util.updates
import wrappers.discord_rp
from process import executable_info
from util.status import Status
from wrappers import system_tray_icon

logger = logging.getLogger("discord_fm").getChild(__name__)


class AppManager:
    name = "discord.fm"
    _version = "0.8.0"

    def __init__(self):
        self.settings = settings.Settings("Discord.fm")
        self.status = Status(Status.STARTUP)

        self.tray_icon = system_tray_icon.SystemTrayIcon(self)
        self.loop = loop_handler.LoopHandler(self)
        self.discord_rp = wrappers.discord_rp.DiscordRP()

    def get_version(self, parsed: bool = False) -> packaging.version.Version | str:
        if parsed:
            return packaging.version.parse(self._version)
        else:
            return self._version

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
            current = self.get_version(True)
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

                util.install.windows.do_silent_install(path)
                logger.info("Quitting to allow installation of newer version")
                self.close()

        if util.arg_exists("-o"):
            logger.info('"-o" argument was found, opening settings')
            self.open_settings_and_wait()

        no_username = self.settings.get("username") == ""
        if no_username and not util.is_frozen():
            logger.critical(
                "No username found - please add a username to settings and restart the app"
            )
            self.close()
        elif no_username and util.is_frozen():
            logger.info(
                "No username found, opening settings UI and waiting for it to be closed..."
            )
            self.open_settings_and_wait()

    def start(self):
        atexit.register(self.close)
        self.wait_for_discord()
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
            logger.debug("Exception catched when attempting to close app", exc_info=e)

        try:
            sc = self.loop.sc
            if not sc.empty():
                for event in sc.queue:
                    sc.cancel(event)
                    logger.debug(f'Event "{event.action}" canceled')
        except (AttributeError, NameError) as e:
            logger.debug(
                "Exception catched when attempting to flush global scheduler",
                exc_info=e,
            )

        sys.exit()

    def wait_for_discord(self):
        self.status = Status.WAITING_FOR_DISCORD
        logger.info("Attempting to connect to Discord")

        notification_called = False
        self.tray_icon.ti.update_menu()

        while True:
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
                    logger.debug(f"Received {e}")
                    continue
                except PermissionError as e:
                    if not notification_called and platform.system() == "Windows":
                        logger.critical(
                            "Another user has Discord open, notifying user", exc_info=e
                        )

                        title = "Another user has Discord open"
                        message = (
                            "Discord.fm will not update your Rich Presence or theirs. Please close the other "
                            "instance before scrobbling with this user. "
                        )

                        util.basic_notification(title, message)

                        notification_called = True
                    continue

                break
            else:
                time.sleep(10)

        self.status = Status.ENABLED
        self.tray_icon.ti.update_menu()

    def open_settings_and_wait(self):
        process.open_settings()
        # Discord.fm can take a little while to start the settings UI, so wait before closing
        time.sleep(1)
        if not util.is_frozen():
            self.close()

        # Starting the process takes a bit, if we went straight into the next while block, the method would
        # finish immediately because "settings_ui" is not running.
        while not process.check_process_running("settings_ui"):
            pass

        while process.check_process_running("settings_ui"):
            time.sleep(1.5)

    def change_status(self, value: Status):
        self.status = value
        self.tray_icon.ti.update_icon()

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
