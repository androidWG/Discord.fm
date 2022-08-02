import atexit
import logging
import platform
import struct
import sys
import time

import pypresence

import globals as g
import loop_handler
import process
import util
import util.install
import util.updates
import wrappers.discord_rp
from globals import get_version
from wrappers import system_tray_icon

logger = logging.getLogger("discord_fm").getChild(__name__)


class AppManager:
    def __init__(self):
        self.tray_icon = system_tray_icon.SystemTrayIcon(self.close)
        self.loop = loop_handler.LoopHandler(self.tray_icon)

        g.discord_rp = wrappers.discord_rp.DiscordRP()

    def _perform_checks(self):
        if not util.is_frozen():
            logger.warning("Running in non-frozen mode")

        if process.check_process_running("discord_fm") and not util.arg_exists(
            "--ignore-open"
        ):
            logger.error("Discord.fm is already running")
            self.close()

        if g.local_settings.get("auto_update"):
            logger.debug("Checking for updates")

            latest, latest_asset = util.updates.get_newest_release()
            current = get_version(True)
            if (
                latest is not None
                and latest > current
                or util.arg_exists("--force-update")
            ):
                g.current = g.Status.UPDATING
                self.tray_icon.ti.update_menu()

                logger.info(
                    f"Found newer version (current v{current} vs. latest v{latest})"
                )
                path = util.updates.download_asset(latest_asset)

                util.install.windows.do_silent_install(path)
                logger.info("Quitting to allow installation of newer version")
                self.close()

        if util.arg_exists("-o"):
            logger.info('"-o" argument was found, opening settings')
            self.open_settings_and_wait()

        no_username = g.local_settings.get("username") == ""
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
        self._wait_for_discord()
        self._perform_checks()

        if g.current != g.Status.KILL:
            g.current = g.Status.ENABLED
            self.tray_icon.ti.update_menu()

            try:
                self.loop.handle_update()
            except (KeyboardInterrupt, SystemExit):
                pass

        self.close()

    def reload(self):
        logger.info("Reloading...")

        try:
            g.discord_rp.exit_rp()
        except (RuntimeError, AttributeError, AssertionError, pypresence.InvalidID):
            pass
        except NameError:
            return

        g.current = g.Status.DISABLED
        self.loop.reload_lastfm()
        g.current = g.Status.ENABLED

    def close(self):
        g.current = g.Status.KILL
        logger.info("Closing app...")

        try:
            g.discord_rp.exit_rp()
            self.tray_icon.ti.stop()
        except (
            RuntimeError,
            AttributeError,
            AssertionError,
            pypresence.InvalidID,
            NameError,
        ):
            pass

        try:
            sc = self.loop.sc
            if not sc.empty():
                for event in sc.queue:
                    sc.cancel(event)
                    logger.debug(f'Event "{event.action}" canceled')
        except (AttributeError, NameError):
            pass

        sys.exit()

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

    def _wait_for_discord(self):
        g.current = g.Status.WAITING_FOR_DISCORD
        logger.info("Attempting to connect to Discord")

        notification_called = False
        self.tray_icon.ti.update_menu()

        while True:
            if process.check_process_running("Discord", "DiscordCanary"):
                try:
                    g.discord_rp.connect()
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

        g.current = g.Status.ENABLED
        self.tray_icon.ti.update_menu()
