import logging
import os.path
import plistlib
import shutil
import stat
import zipfile
from pathlib import Path
from shutil import copytree

import util.timeout
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
                    "Received error when trying to create shortcut", exc_info=e
                )
                return False

    def install(self, path: str):
        logger.info("Installing for macOS...")

        if APP_PATH.is_dir():
            shutil.rmtree(APP_PATH)

        # TODO: Make this compatible with DMG files
        logger.debug("Copying new app into user's Applications folder")
        shutil.copytree(path, APP_PATH)


def get_app_folder_and_version(app_name: str) -> tuple:
    """Gets the version and install path of Discord.fm with the provided .app path.

    :param app_name: Path to .app of Discord.fm
    :type app_name: str
    :return: Tuple with installation path and a version string respectively. If an installation is not found, a tuple of
    None and None are returned.
    :rtype: tuple
    """
    path = os.path.join("/Applications", app_name)
    if os.path.exists(path):
        with open(os.path.join(path, "Contents", "Info.plist"), "rb") as file:
            plist = plistlib.load(file)
            return path, plist["CFBundleShortVersionString"]
    else:
        logger.warning("Discord.fm installation not found")
        return "", ""


@util.timeout.exit_after(180)
def copy_to_applications(temp_dir: str, installer_path: str):
    """Copies the .app folder from the downloaded Zip to the /Applications folder.

    :param temp_dir: Temporary directory to be used
    :type temp_dir: str
    :param installer_path: Path where the .zip containing the .app folder is located
    :type installer_path: str
    """
    logger.info("Installing for macOS...")

    zip_path = os.path.join(temp_dir, installer_path)
    with zipfile.ZipFile(zip_path, "r") as downloaded_zip:
        downloaded_zip.extractall(temp_dir)
        logger.debug("Extracted Discord.fm.app")

        # For some reason zipfile extracts the main executable inside the .app as a
        # non-executable file, so we need to manually do that
        main_executable = os.path.join(
            temp_dir, "Discord.fm.app/Contents/MacOS/Discord.fm"
        )
        st = os.stat(main_executable)
        os.chmod(main_executable, st.st_mode | stat.S_IEXEC)
        logger.debug("Made Discord.fm file executable")

        copytree(
            os.path.join(temp_dir, "Discord.fm.app"),
            "/Applications/Discord.fm.app",
            symlinks=True,
        )
        logger.debug("Copied to Applications")
