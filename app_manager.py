import atexit
import logging
import sys
import util
import loop_handler
import globals as g
import util.process
import util.updates
import util.install
from time import sleep
from pypresence import InvalidID
from settings import local_settings, get_version
from wrappers import system_tray_icon

logger = logging.getLogger("discord_fm").getChild(__name__)


class AppManager:
    def __init__(self):
        self.tray_icon = system_tray_icon.SystemTrayIcon(self.close)
        while True:  # Keep prompting for a valid username until one is found
            try:
                self.loop = loop_handler.LoopHandler(self.tray_icon)
                break
            except ValueError:
                util.basic_notification("Invalid username",
                                        "Please change to a valid username.")
                self.open_settings_and_wait()
                local_settings.load()

    def start(self):
        atexit.register(g.manager.close)

        if not util.is_frozen():
            logger.warning("Running in non-frozen mode")

        if util.process.check_process_running("discord_fm") and not util.arg_exists("--ignore-open"):
            logger.error("Discord.fm is already running")
            self.close()

        if local_settings.get("auto_update"):
            logger.debug("Checking for updates")

            latest, latest_asset = util.updates.get_newest_release()
            current = get_version(True)
            if latest is not None and latest > current or util.arg_exists("--force-update"):
                g.current = g.Status.UPDATING
                self.tray_icon.ti.update_menu()

                logger.info(f"Found newer version (current v{current} vs. latest v{latest})")
                path = util.updates.download_asset(latest_asset)

                util.install.windows.do_silent_install(path)
                logger.info("Quitting to allow installation of newer version")
                self.close()

        if util.arg_exists("-o"):
            logger.info("\"-o\" argument was found, opening settings")
            self.open_settings_and_wait()

        no_username = local_settings.get("username") == ""
        if no_username and not util.is_frozen():
            logger.critical("No username found - please add a username to settings and restart the app")
            self.close()
        elif no_username and util.is_frozen():
            logger.info("No username found, opening settings UI and waiting for it to be closed...")
            self.open_settings_and_wait()

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
            self.tray_icon.discord_rp.exit_rp()
        except (RuntimeError, AttributeError, AssertionError, InvalidID):
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
            self.tray_icon.discord_rp.exit_rp()
            self.tray_icon.ti.stop()
        except (RuntimeError, AttributeError, AssertionError, InvalidID, NameError):
            pass

        try:
            sc = self.loop.sc
            if not sc.empty():
                for event in sc.queue:
                    sc.cancel(event)
                    logger.debug(f"Event \"{event.action}\" canceled")
        except (AttributeError, NameError):
            pass

        sys.exit()

    def open_settings_and_wait(self):
        util.process.open_settings()
        if not util.is_frozen():
            self.close()

        # Starting the process takes a bit, if we went straight into the next while block, the method would
        # finish immediately because "settings_ui" is not running.
        while not util.process.check_process_running("settings_ui"):
            pass

        while util.process.check_process_running("settings_ui"):
            sleep(1.5)
