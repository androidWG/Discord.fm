import os
import sys
import util.timeout


# From https://stackoverflow.com/a/13790741/8286014
def resource_path(relative_path: str) -> str:
    """Gets the absolute path to a file, dealing with temp resource folders from PyInstaller

    :param relative_path: Path of a file in relative space
    :type relative_path: str
    :return: Absolute path to a resource
    :rtype: str
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)