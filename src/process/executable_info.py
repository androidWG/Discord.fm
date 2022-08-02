import os
from platform import system
from typing import List

from util import is_frozen
from util.install import get_install_folder
from process import logger


class ExecutableInfo:
    def __init__(
        self, name, windows_exe_name, macos_app_name, linux_executable_name, script_path
    ):
        """Holds info about an executable and gives its path independent of platform or app state (frozen or not).

        :param name: General process name
        :param windows_exe_name: Name of the specific Windows .exe for this executable.
        :param macos_app_name: Name of the specific macOS .app folder for this executable.
        :param script_path: Path of the script to be run if the app is not frozen.
        """
        self.name = name
        self.windows_exe_name = windows_exe_name
        self.macos_app_name = macos_app_name
        self.linux_executable_name = linux_executable_name
        self.script_path = script_path

    @property
    def path(self) -> List[str]:
        """Gets the full path of this executable for this instance of the app. If the app is not frozen, a path to the
        Python interpreter with the script as an argument will be passed."""
        install_path = get_install_folder(self.windows_exe_name, self.macos_app_name)

        current_platform = system()
        if current_platform == "Windows":
            path = os.path.abspath(self.windows_exe_name)
        elif current_platform == "Darwin":
            path = os.path.abspath(self.macos_app_name)
        else:
            path = os.path.abspath(self.linux_executable_name)

        if os.path.isfile(path):
            logger.debug(f'Path for "{self.name}": "{path}"')
            return [path]
        elif os.path.isfile(install_path) and is_frozen():
            logger.debug(f'Path for "{self.name}": "{install_path}"')
            return [install_path]
        elif not is_frozen():
            python_path = os.path.abspath(
                "venv/Scripts/python.exe"
                if current_platform == "Windows"
                else "venv/bin/python"
            )
            logger.debug(f'Path for "{self.name}": "{[python_path, self.script_path]}"')
            return [python_path, self.script_path]
