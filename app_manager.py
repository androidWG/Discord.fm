import atexit
import logging
import sys
import loop_handler
import util
import globals as g
import util.process
from time import sleep
from os.path import isfile
from pypresence import InvalidID
from settings import local_settings
from wrappers import system_tray_icon
from util.updates import check_version_and_download

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
                                        "Please open Discord.fm Settings to change to a valid username.")
                open_settings_and_wait()

    def start(self):
        atexit.register(g.manager.close)

        if util.process.check_process_running("discord_fm") and not util.arg_exists("--ignore-open"):
            logger.info("Discord.fm is already running!")
            self.close()

        if util.updates.check_version_and_download() and not util.is_frozen():
            logger.info("Quitting to allow installation of newer version")
            self.close()

        if not isfile(util.resource_path(".env")):
            logger.critical(".env file not found, unable to get API keys and data!")
            self.close()

        if util.arg_exists("-o"):
            logger.info("\"-o\" argument was found, opening settings")
            open_settings_and_wait()
        elif local_settings.first_load:
            logger.info("First load, opening settings UI and waiting for it to be closed...")
            open_settings_and_wait()

        no_username = local_settings.get("username") == ""
        if no_username and not util.is_frozen():
            logger.critical("No username found - please add a username to settings and restart the app")
            self.close()
        elif no_username and util.is_frozen():
            logger.info("No username found, opening settings UI and waiting for it to be closed...")
            open_settings_and_wait()

        if g.current != g.Status.KILL:
            g.current = g.Status.ENABLED
            self.tray_icon.ti.update_menu()
        else:
            return

        try:
            self.loop.handle_update()
        except (KeyboardInterrupt, SystemExit):
            self.close()

        sys.exit()

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
        logger.info("Closing app...")
        g.current = g.Status.KILL

        try:
            self.tray_icon.discord_rp.exit_rp()
            self.tray_icon.tray_icon.stop()
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


def open_settings_and_wait():
    util.process.open_settings()
    # Starting the process takes a bit, if we went straight into the next while block, the method would
    # finish immediately because "settings_ui" is not running.
    while not util.process.check_process_running("settings_ui"):
        pass

    while util.process.check_process_running("settings_ui"):
        sleep(1.5)
