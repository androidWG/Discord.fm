from __future__ import annotations

import enum

import packaging.version

import settings

__VERSION = "0.8.0"
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


local_settings = None
current = Status(Status.STARTUP)
discord_rp = None
manager = None


def load_settings():
    global local_settings
    local_settings = settings.Settings("Discord.fm")


def change_status(value: Status):
    global current, manager
    current = value

    if manager is not None:
        # noinspection PyUnresolvedReferences
        manager.tray_icon.ti.update_icon()
