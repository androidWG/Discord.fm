import enum


class ScrobbleStatus(enum.Enum):
    SCROBBLING = 0
    FIRST_CHECK = 1
    NOT_SCROBBLING = 2
