import logging
import os
import shutil
import sys
from platform import system

import process

logger = logging.getLogger("discord_fm").getChild(__name__)


# From https://stackoverflow.com/a/13790741/8286014
# noinspection PyProtectedMember
def resource_path(*paths: str, base_path: str = ".") -> str:
    """Gets the absolute path to a file, dealing with temp resources folders from PyInstaller

    :param paths: Multiple args that make a file path without separators to a local resource.
    :type paths: str
    :param base_path: Base path to get absolute path. Default is . to get it relative to the current working directory.
    :type base_path: str
    :return: Absolute path to a resource
    :rtype: str
    """
    if is_frozen():
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(base_path)

    return os.path.join(base_path, *paths)


def replace_instances(
    file: str, tags: list, out_file: str = "temp_", encoding: str = "utf-8"
):
    """Takes a text file and replaces all instances of a tag with a string.

    :param encoding: Encoding to open and save to file with.
    :type encoding: str
    :param file: Path to file that will be modified
    :type file: str
    :param tags: List of tuples containing the tag and its replacement respectively
    :type tags: list
    :param out_file: (optional) File to write to. By default, a file named "temp_" will be created and then renamed
    to the original file
    :type out_file:
    """
    with open(file, "rt", encoding=encoding) as file_in:
        with open(out_file, "wt", encoding=encoding) as file_out:
            for line in file_in:
                replaced_line = line
                for tag in tags:
                    replaced_line = replaced_line.replace(tag[0], tag[1])

                file_out.write(replaced_line)

    logger.debug(f"Replaced tags in {file}")

    if out_file == "temp_":
        shutil.move("temp_", file)
        logger.debug("Renamed temp_ file")


def check_dark_mode() -> bool:
    """Returns true if dark mode is enabled on Windows or macOS.

    :return: If dark mode is turned on.
    :rtype: bool
    """
    if system() == "Windows":
        import winreg

        access_registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        try:
            access_key = winreg.OpenKey(access_registry, key_path)
        except FileNotFoundError:
            return False

        try:
            value = winreg.QueryValueEx(access_key, "SystemUsesLightTheme")[0]
        except FileNotFoundError:
            return False
        return value == 0
    elif system() == "Darwin":
        # TODO: Maybe add proper checking for dark mode on macOS and Linux
        return True
    else:
        return True


def arg_exists(*args):
    """Returns true if *any* of the provided args is found in the script args.

    :param args: Strings to be searched on sys.argv
    :type args: str
    """
    for arg in args:
        if sys.argv.__contains__(arg):
            return True

    return False


def is_frozen():  # I could just use hasattr() directly but this makes it more clear what is happening
    return hasattr(sys, "_MEIPASS")


def basic_notification(title: str, message: str):
    import plyer

    logger.debug(f'Sending notification with title "{title}" and message "{message}"')
    if system() == "Windows":
        icon = resource_path("resources", "icon.ico")
    else:
        icon = resource_path(
            "resources", "white" if check_dark_mode() else "black", "icon.png"
        )

    if system() == "Darwin":
        from aquaui.notification.native_notification import Notification

        mac_notif = (
            Notification(message)
            .with_subtitle(title)
            .with_identity_image(resource_path("resources/icon.png"))
        )

        mac_notif.send()
    else:
        plyer.notification.notify(
            title=title,
            message=message,
            app_name="Discord.fm",
            app_icon=icon,
        )


def is_running_in_flatpak() -> bool:
    return os.getenv("container") is not None


def is_discord_running() -> bool:
    import pypresence.utils

    if is_running_in_flatpak():
        ipc_path = pypresence.utils.get_ipc_path(0)
        logger.debug(
            f"Determining if Discord is running, detected ipc_path: {ipc_path}"
        )
        return ipc_path is not None
    else:
        return process.check_process_running("Discord", "DiscordCanary")
