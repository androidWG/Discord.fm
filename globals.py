import enum


class Status(enum.Enum):
    ENABLED = 0
    DISABLED = 1
    KILL = 2
    WAITING_FOR_DISCORD = 3


current = Status(Status.ENABLED)
