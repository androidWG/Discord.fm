import enum
from settings import Settings
from wrappers.discord_rp import DiscordRP


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
