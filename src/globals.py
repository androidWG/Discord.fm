import enum

import packaging.version

from settings import Settings
from wrappers.discord_rp import DiscordRP

__version = "0.7.1"
__debug = True


def get_version(parsed=False):
    if parsed:
        return packaging.version.parse(__version)
    else:
        return __version


def get_debug():
    return __debug


class Status(enum.Enum):
    ENABLED = 0
    DISABLED = 1
    KILL = 2
    WAITING_FOR_DISCORD = 3
    STARTUP = 4
    UPDATING = 5


local_settings = Settings("Discord.fm")
discord_rp = DiscordRP()

current = Status(Status.STARTUP)
manager = None


def change_status(value: Status):
    global current, manager
    current = value

    if manager is not None:
        manager.tray_icon.ti.update_icon()
