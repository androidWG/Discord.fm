import importlib
import os
import platform
import sys

import build.base

sys.path.append(os.path.abspath("src"))
import globals


def get_build_tool() -> build.base.BuildTool:
    version = globals.get_version(parsed=True)

    if platform.system() == "Windows":
        module = importlib.import_module("build.windows")
    elif platform.system() == "Darwin":
        module = importlib.import_module("build.macos")
    elif platform.system() == "Linux":
        module = importlib.import_module("build.linux")
    else:
        raise NotImplementedError("System is not supported")

    _build_tool = module.instance()(version=version)
    return _build_tool
