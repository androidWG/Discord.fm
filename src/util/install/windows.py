import logging
import os.path
import subprocess
import winreg

import pywintypes
import win32com.client

from util.install import BaseInstall


REGISTRY_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{5DD6EAF6-9E8F-4240-ADF1-29FD79B30E3F}_is1"
LINK_PATH = [
    "Microsoft",
    "Windows",
    "Start Menu",
    "Programs",
    "Startup",
    "Discord.fm.lnk",
]
LINK_ABS_PATH = os.path.join(os.path.expandvars("%appdata%"), *LINK_PATH)

logger = logging.getLogger("discord_fm").getChild(__name__)


class WindowsInstall(BaseInstall):
    def get_executable_path(self) -> str | None:
        logger.debug("Attempting to find Windows install...")

        access_registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        discord_fm_key_location = REGISTRY_PATH

        try:
            access_key = winreg.OpenKey(access_registry, discord_fm_key_location)
        except FileNotFoundError:
            logger.warning("Discord.fm installation not found")
            return None

        exe_location = winreg.QueryValueEx(access_key, "DisplayIcon")[0]

        logger.info(f"Found executable - Location: {exe_location}")

        return exe_location

    def get_startup(self):
        return os.path.isfile(LINK_ABS_PATH)

    def set_startup(self, new_value: bool, exe_path: str) -> bool:
        shortcut_exists = self.get_startup()
        if shortcut_exists and not new_value:
            os.remove(LINK_ABS_PATH)
            return False
        elif not shortcut_exists and new_value:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(LINK_ABS_PATH)
            shortcut.IconLocation = exe_path
            shortcut.Targetpath = exe_path

            try:
                shortcut.save()
                return True
            except pywintypes.com_error as e:
                logging.error(
                    "Received error when trying to create shortcut", exc_info=e
                )
                return False

    def install(self, installer_path: str):
        """Runs an Inno Setup installer in silent mode under a subprocess and waits for it to finish.

        :param installer_path: Path where the .zip containing the .app folder is located
        :type installer_path: str
        """
        logger.info("Installing for Windows...")

        command = (
            f'"{installer_path}" /VERYSILENT /SUPPRESSMSGBOXES /CLOSEAPPLICATIONS /FORCECLOSEAPPLICATIONS '
            f"/CURRENTUSER "
        )
        logger.debug(f"Running command: {command}")
        subprocess.Popen(command, shell=True)


def instance():
    return WindowsInstall
