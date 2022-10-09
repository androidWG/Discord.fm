import importlib
import os
import platform
import sys

import base

sys.path.append(os.path.abspath("src"))
import globals


def get_build_tool() -> base.BuildTool:
    version = globals.get_version(parsed=True)

    if platform.system() == "Windows":
        module = importlib.import_module("windows")
    elif platform.system() == "Darwin":
        module = importlib.import_module("macos")
    elif platform.system() == "Linux":
        module = importlib.import_module("linux")
    else:
        raise NotImplementedError("System is not supported")

    _build_tool = module.instance()(version=version)
    return _build_tool
