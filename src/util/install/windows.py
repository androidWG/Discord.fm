import logging
import os.path
import platform
import subprocess

import pywintypes
import win32com.client

import util.timeout

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


def get_installed_exe_path() -> str | None:
    """Gets the path for the installed executable of Discord.fm from the Windows Registry."""
    # Only Windows has the winreg package, so make sure the script doesn't go apeshit in other systems
    if platform.system() == "Windows":
        import winreg

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


def get_install_folder_and_version() -> tuple:
    """Gets the version and install path of Discord.fm from the Windows Registry.

    :return: Tuple with installation path and a version string respectively. If an installation is not found,
    a tuple of None and None are returned.
    :rtype: tuple
    """
    # Only Windows has the winreg package, so make sure the script doesn't go apeshit in other systems
    if platform.system() == "Windows":
        import winreg

        logger.debug("Attempting to find Windows install...")

        access_registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        discord_fm_key_location = REGISTRY_PATH

        try:
            access_key = winreg.OpenKey(access_registry, discord_fm_key_location)
        except FileNotFoundError:
            logger.warning("Discord.fm installation not found")
            return None, None

        install_location = winreg.QueryValueEx(access_key, "InstallLocation")[0]
        version = winreg.QueryValueEx(access_key, "DisplayVersion")[0]

        logger.info(f"Found install info - Location: {install_location}")

        return install_location, version


@util.timeout.exit_after(180)
def do_silent_install(installer_path: str):
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


def get_startup_shortcut() -> bool:
    return os.path.isfile(LINK_ABS_PATH)


def set_startup_shortcut(new_value: bool, exe_path: str) -> bool:
    shortcut_exists = get_startup_shortcut()
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
            logging.error("Recieved error when trying to create shortcut", exc_info=e)
            return False
