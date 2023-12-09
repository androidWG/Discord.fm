import importlib
import platform
import sys

import util
from util.install.base import BaseInstall


def get_install() -> BaseInstall:
    if platform.system() == "Windows":
        module = importlib.import_module("util.install.windows")
    elif platform.system() == "Darwin":
        raise NotImplementedError("macOS is not implemented yet")
    elif platform.system() == "Linux":
        raise NotImplementedError("Linux is not implemented yet")
    else:
        raise NotImplementedError("System is not supported")

    _install = module.instance()()
    return _install


def get_exe_path():
    if platform.system() == "Linux":
        raise NotImplementedError
    else:
        if util.is_frozen():
            return sys.executable
        else:
            install = get_install()
            return install.get_executable_path()
