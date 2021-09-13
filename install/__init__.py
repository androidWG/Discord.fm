import os
import platform
import sys
from install import windows, macos


def get_executable(macos_path):
    if getattr(sys, 'frozen', False):
        if platform.system() == "Windows":
            path = windows.get_install_folder_and_version()[0]
            return [os.path.join(path, "discord_fm.exe")]
        else:
            raise NotImplementedError
    else:
        python_path = os.path.abspath("venv/Scripts/python")
        if platform.system() == "Windows":
            python_path += ".exe"

        return [python_path, "main.py"]
