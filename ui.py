import logging
import sys
import settings
import eel.browsers
import os
import platform
import subprocess
from util import log_setup, resource_path, process

log_setup.setup_logging("ui")


# From https://stackoverflow.com/a/16993115/8286014
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception
process_name = "discord_fm"


@eel.expose
def save_setting(name, value):
    settings.define(name, value)


@eel.expose
def get_settings():
    return settings.get_dict()


@eel.expose
def get_running_status():
    return process.check_process_running(process_name)


@eel.expose
def start_stop_service():
    if process.check_process_running(process_name):
        process.kill_process(process_name)
    else:
        subprocess.Popen("C:\\Users\\samu-\\Repos\\Discord.fm\\dist\\discord_fm.exe")


@eel.expose
def open_logs_folder():
    if platform.system() == "Windows":
        os.startfile(settings.logs_path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", settings.logs_path])
    else:
        subprocess.Popen(["xdg-open", settings.logs_path])


eel.init("web")
eel.browsers.set_path("electron", resource_path(os.path.join("electron", "electron.exe")))
eel.start("settings.html", mode="electron")
