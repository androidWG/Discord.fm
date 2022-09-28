import logging
import os
import platform
import sys
from typing import List

logger = logging.getLogger("discord_fm").getChild(__name__)


def get_local_executable(name: str, script_name: str) -> List[str]:
    current_platform = platform.system()

    if current_platform == "Windows":
        exe = name + ".exe"
    else:
        exe = name

    if getattr(sys, "frozen", False):
        app_path = sys._MEIPASS
    else:
        # Jump out from process folder to root project folder
        #     root / src / process / executable_info.py
        #   ^to here^    ^from here^
        root_folder = os.path.abspath(os.path.join(".."))
        py_path = os.path.join(
            root_folder,
            "venv",
            "Scripts" if current_platform == "Windows" else "bin",
            "python",
        )
        script_path = os.path.join(root_folder, "src", script_name)

        return [py_path, script_path]

    return [os.path.join(app_path, exe)]
