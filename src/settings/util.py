import logging
import os
import re
import shutil
from pathlib import Path
from platform import system

import util

APP_ID = "net.androidwg.discord_fm"

logger = logging.getLogger("discord_fm").getChild(__name__)


def _make_dir(path: Path):
    """Creates a directory specified in path if it doesn't exist, ignoring it if it does.

    :param path: Path of the directory to be created.
    :type path: str
    """
    try:
        os.mkdir(path)
        logger.debug(f'Created folder "{path}"')
    except FileExistsError:
        logger.debug(f'Folder "{path}" already exists')


def _clear_executables(app_data_path: Path):
    """Removes all executable files leftover from previous updates.

    :param app_data_path: Path of the app data directory containing the files
    :type app_data_path: str
    """
    update_folder = app_data_path.joinpath("updated_version")
    if update_folder.is_dir():
        logger.debug(f"Removing leftover update folder")
        shutil.rmtree(update_folder)

    for file in os.listdir(app_data_path):
        if re.match(r"\.(?:tar|exe|dmg)(?:.xz|.gz)?$", file):
            logger.debug(f"Removing leftover update file {file}")
            app_data_path.joinpath(file).unlink(missing_ok=True)


def setup_app_data_dir(folder_name: str) -> str:
    """Gets the folder where to store app configuration files.

    :param folder_name: Name of the folder to create inside the system's app data directory.
    :type folder_name: str
    :return: Path to logs folder.
    :rtype: str
    """
    current_platform = system()

    if current_platform == "Windows":
        # Here it's AppData NOT LocalAppData, since settings should always be present for the user
        path = Path(os.getenv("appdata"), folder_name)
    elif current_platform == "Darwin":
        path = Path("~/Library/Application Support", folder_name).expanduser()
    elif current_platform == "Linux":
        if util.is_running_in_flatpak():
            path = Path("~/.var/app/", APP_ID).expanduser()
        else:
            path = Path(
                f"~/.config/{folder_name.replace('.', '_').lower()}"
            ).expanduser()
    else:
        raise NotImplementedError("Platform not supported")

    _make_dir(path)
    _clear_executables(path)
    return str(path.absolute())


def setup_logs_dir(folder_name: str) -> str:
    """Gets the folder where to store log files based on OS.

    :param folder_name: Name of the folder to create inside the system's logs directory (for Windows, it will be the
    same as app data directory)
    :type folder_name: str
    :return: Path to logs folder.
    :rtype: str
    """
    current_platform = system()

    if current_platform == "Windows":
        # And here it's LocalAppData NOT AppData, since logs can occupy a lot of space and are not needed by the app
        path = Path(os.getenv("localappdata"), folder_name)
    elif current_platform == "Darwin":
        path = Path("~/Library/Logs", folder_name).expanduser()
    elif current_platform == "Linux":
        if util.is_running_in_flatpak():
            path = Path("~/.var/app/", APP_ID, "logs").expanduser()
        else:
            path = Path(
                f"~/.config/{folder_name.replace('.', '_').lower()}/logs"
            ).expanduser()
    else:
        raise NotImplementedError("Platform not supported")

    _make_dir(path)
    return str(path.absolute())
