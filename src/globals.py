from __future__ import annotations

import enum

import packaging.version

from settings import Settings

__VERSION = "0.7.1"
__DEBUG = True


def get_version(parsed: bool = False) -> packaging.version.Version | str:
    if parsed:
        return packaging.version.parse(__VERSION)
    else:
        return __VERSION


def get_debug() -> bool:
    return __DEBUG


class Status(enum.Enum):
    ENABLED = 0
    DISABLED = 1
    KILL = 2
    WAITING_FOR_DISCORD = 3
    STARTUP = 4
    UPDATING = 5


local_settings = Settings("Discord.fm")
current = Status(Status.STARTUP)
discord_rp = None
manager = None


def change_status(value: Status):
    global current, manager
    current = value

    if manager is not None:
        # noinspection PyUnresolvedReferences
        manager.tray_icon.ti.update_icon()
