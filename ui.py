import random

import settings
import eel.browsers
import os
import platform
import subprocess
from util import log_setup

log_setup.setup_logging("ui")


@eel.expose
def save_setting(name, value):
    settings.define(name, value)


@eel.expose
def get_settings():
    return settings.get_dict()


@eel.expose
def get_running_status():
    # Temporary function that will later return running status
    random_running = random.randint(0, 50)
    return bool(random_running)


@eel.expose
def open_logs_folder():
    if platform.system() == "Windows":
        os.startfile(settings.logs_path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", settings.logs_path])
    else:
        subprocess.Popen(["xdg-open", settings.logs_path])


eel.init("web")
eel.browsers.set_path("electron", "C:\\Users\\samu-\\Repos\\Discord.fm\\node_modules\\electron\\dist\\electron.exe")
eel.start("settings.html", mode="electron")
