import settings
import eel.browsers
from util import log_setup

log_setup.setup_logging("ui")


@eel.expose
def save_setting(name, value):
    settings.define(name, value)


@eel.expose
def get_settings():
    return settings.get_dict()


eel.init("web")
eel.browsers.set_path("electron", "C:\\Users\\samu-\\Repos\\Discord.fm\\node_modules\\electron\\dist\\electron.exe")
eel.start("settings.html", mode="electron")
