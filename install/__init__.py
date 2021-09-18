import os
import platform
import sys
from install import windows, macos


def get_executable(windows_exe, macos_path, script_path):
    if getattr(sys, "frozen", False):
        if platform.system() == "Windows":
            path = windows.get_install_folder_and_version()[0]
            return [os.path.join(path, windows_exe)]
        elif platform.system() == "Darwin":
            return macos_path
        else:
            raise NotImplementedError
    else:
        python_path = os.path.abspath("venv/Scripts/python.exe"
                                      if platform.system() == "Windows"
                                      else "venv/bin/python")

        return [python_path, script_path]
