import importlib
import os
import platform
import sys

from packaging.version import Version

sys.path.append(os.path.abspath("src"))
import version
import build.base


def get_build_tool(py_path: str, flatpak: bool = False) -> build.base.BuildTool:
    ver: Version = version.get_version(True)

    if flatpak:
        module = importlib.import_module("build.flatpak")
    elif platform.system() == "Windows":
        module = importlib.import_module("build.windows")
    elif platform.system() == "Darwin":
        module = importlib.import_module("build.macos")
    elif platform.system() == "Linux":
        module = importlib.import_module("build.linux")
    else:
        raise NotImplementedError("System is not supported")

    _build_tool = module.instance()(py_path=py_path, version=ver)
    return _build_tool
