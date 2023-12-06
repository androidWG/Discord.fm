import logging
import shutil
from pathlib import Path

from util import resource_path
from util.install import base

logger = logging.getLogger("discord_fm").getChild(__name__)

APP_PATH = Path("~/Applications/Discord.fm.app").expanduser()
PLIST_NAME = "net.androidwg.discordfm.launch.plist"
LAUNCH_AGENTS_PATH = Path("~/Library/LaunchAgents").expanduser()
PLIST_PATH = Path(LAUNCH_AGENTS_PATH, PLIST_NAME)


class MacOSInstall(base.BaseInstall):
    def get_executable_path(self) -> str | None:
        logger.debug("Attempting to find macOS install...")
        if APP_PATH.is_dir():
            logger.info(f"Found app folder - Location: {APP_PATH}")
            return str(APP_PATH)
        else:
            return None

    def get_startup(self) -> bool:
        return PLIST_PATH.is_file()

    def set_startup(self, new_value: bool, exe_path: str) -> bool:
        shortcut_exists = self.get_startup()
        if shortcut_exists and not new_value:
            PLIST_PATH.unlink()
            return False
        elif shortcut_exists and new_value:
            plist = resource_path("resources", PLIST_NAME)
            try:
                shutil.copy(plist, LAUNCH_AGENTS_PATH)
            except (PermissionError, FileNotFoundError) as e:
                logging.error(
                    "Received error when trying to create LaunchAgent", exc_info=e
                )
                return False

    def install(self, path: str):
        logger.info("Installing for macOS...")

        if APP_PATH.is_dir():
            shutil.rmtree(APP_PATH)

        # TODO: Make this compatible with DMG files
        logger.debug("Copying new app into user's Applications folder")
        shutil.copytree(path, APP_PATH)


def instance():
    return MacOSInstall
