import logging
import os
import platform
import sys

logger = logging.getLogger("discord_fm").getChild(__name__)


def get_local_executable(name):
    current_platform = platform.system()

    if current_platform == "Windows":
        exe = name + ".exe"
    else:
        exe = name

    if getattr(sys, "frozen", False):
        app_path = sys._MEIPASS
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(app_path, exe)
