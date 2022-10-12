import importlib
import os
import platform
import sys

import packaging.version

sys.path.append(os.path.abspath("src"))
import app_manager
import build.base


def get_build_tool() -> build.base.BuildTool:
    version: packaging.version.Version = packaging.version.parse(app_manager.AppManager.version)

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
