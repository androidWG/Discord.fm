import importlib
import os
import platform
import sys

import util


if platform.system() == "Windows":
    module = importlib.import_module("util.install.windows")
elif platform.system() == "Darwin":
    raise NotImplementedError("macOS is not implemented yet")
elif platform.system() == "Linux":
    raise NotImplementedError("Linux is not implemented yet")
else:
    raise NotImplementedError("System is not supported")

_install = module.instance()()


def get_exe_path():
    if platform.system() == "Linux":
        raise NotImplementedError
    else:
        if util.is_frozen():
            return os.path.dirname(sys.executable)
        else:
            _install.get_executable_path()


def get_start_with_system():
    return _install.get_startup()


def set_start_with_system(new_value: bool, exe_path: str) -> bool:
    return _install.set_startup(new_value, exe_path)
