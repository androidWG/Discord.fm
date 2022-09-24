import os
import platform
import sys

import util
from util.install import macos, windows


def get_exe_path():
    if platform.system() == "Linux":
        raise NotImplementedError
    else:
        if util.is_frozen():
            return os.path.dirname(sys.executable)
        else:
            if platform.system() == "Windows":
                return windows.get_installed_exe_path()
            elif platform.system() == "Darwin":
                return macos.get_app_folder_and_version("Discord.fm Settings")[0]


def get_start_with_system():
    if platform.system() == "Windows":
        return windows.get_startup_shortcut()
    else:
        raise NotImplementedError


def set_start_with_system(new_value: bool, exe_path: str) -> bool:
    if platform.system() == "Windows":
        return windows.set_startup_shortcut(new_value, exe_path)
    else:
        raise NotImplementedError
