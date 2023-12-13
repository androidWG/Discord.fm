import importlib
import os
import platform
import sys
from pathlib import Path

import util


# TODO: Move this module to root


class BaseInstall:
    def get_executable_path(self):
        pass

    def get_startup(self):
        pass

    def set_startup(self, new_value: bool, exe_path: str) -> bool:
        pass

    def install(self, installer_path: Path):
        pass


def get_install() -> BaseInstall:
    if platform.system() == "Windows":
        module = importlib.import_module("util.install.windows")
    elif platform.system() == "Darwin":
        module = importlib.import_module("util.install.macos")
    elif platform.system() == "Linux":
        module = importlib.import_module("util.install.linux")
    else:
        raise NotImplementedError("System is not supported")

    _install = module.instance()()
    return _install


def get_exe_path():
    if util.is_frozen() and not util.is_running_in_flatpak():
        return os.path.dirname(sys.executable)
    else:
        install = get_install()
        install.get_executable_path()
