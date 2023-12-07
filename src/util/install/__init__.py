import importlib
import os
import platform
import sys

import util


class BaseInstall:
    def get_executable_path(self):
        pass

    def get_startup(self):
        pass

    def set_startup(self, new_value: bool, exe_path: str) -> bool:
        pass

    def install(self, installer_path: str):
        pass


def get_install() -> BaseInstall:
    if platform.system() == "Windows":
        module = importlib.import_module("util.install.windows")
    elif platform.system() == "Darwin":
        raise NotImplementedError("macOS is not implemented yet")
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
