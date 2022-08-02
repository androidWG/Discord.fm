import logging
import platform
import subprocess

import util.timeout

logger = logging.getLogger("discord_fm").getChild(__name__)


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

        access_registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        discord_fm_key_location = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Discord.fm"

        try:
            access_key = winreg.OpenKey(access_registry, discord_fm_key_location)
        except FileNotFoundError:
            logger.warning("Discord.fm installation not found")
            return None, None

        install_location = winreg.QueryValueEx(access_key, "Install Folder")[0]
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
