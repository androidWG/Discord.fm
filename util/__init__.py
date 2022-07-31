import os
import sys
import shutil
import logging
from platform import system
from plyer import notification as plyer_notif
from aquaui.notification.native_notification import Notification

logger = logging.getLogger("discord_fm").getChild(__name__)


# From https://stackoverflow.com/a/13790741/8286014
# noinspection PyProtectedMember
def resource_path(relative_path: str, base_path: str = ".") -> str:
    """Gets the absolute path to a file, dealing with temp resources folders from PyInstaller

    :param relative_path: Path of a file in relative space
    :type relative_path: str
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

    return os.path.join(base_path, relative_path)


def replace_instances(file: str, tags: list, out_file: str = "temp_", encoding: str = "utf-8"):
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
    logger.debug(f'Sending notification with title "{title}" and message "{message}"')
    if system() == "Windows":
        icon = resource_path("resources/icon.ico")
    else:
        icon = resource_path("resources/white/icon.png" if check_dark_mode() else "resources/black/icon.png")

    if system() == "Darwin":
        mac_notif = Notification(message)\
            .with_subtitle(title)\
            .with_identity_image(resource_path("resources/icon.png"))  # the image on the right of the notification

        mac_notif.send()
    else:
        plyer_notif.notify(
            title=title,
            message=message,
            app_name="Discord.fm",
            app_icon=icon,
        )
