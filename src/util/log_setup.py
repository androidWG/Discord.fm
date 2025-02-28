import copy
import datetime
import datetime as dt
import logging.config
import logging.handlers
import os
import re


class MillisecondFormatter(logging.Formatter):
    """A formatter for standard library 'logging' that supports '%f' wildcard in format strings."""

    converter = dt.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        converter = self.converter(record.created)
        if datefmt:
            s = converter.strftime(datefmt)[:-3]
        else:
            t = converter.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


BLACK, RED, GREEN, YELLOW, ORANGE, PURPLE, CYAN, GREY = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
ITALIC_SEQ = "\033[3m"
UNDERLINE_SEQ = "\033[4m"


def formatter_message(message, use_color=True):
    if use_color:
        message = (
            message.replace("$RESET", RESET_SEQ)
            .replace("$BOLD", BOLD_SEQ)
            .replace("$ITALIC", ITALIC_SEQ)
            .replace("$UNDER", UNDERLINE_SEQ)
        )
    else:
        message = (
            message.replace("$RESET", "")
            .replace("$BOLD", "")
            .replace("$ITALIC", "")
            .replace("$UNDER", "")
        )
    return message


COLORS = {
    "WARNING": YELLOW,
    "INFO": GREY,
    "DEBUG": ORANGE,
    "CRITICAL": YELLOW,
    "ERROR": RED,
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        new_record = copy.copy(record)
        levelname = new_record.levelname

        if levelname in COLORS:
            levelname_color = (
                COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            )
            new_record.levelname = levelname_color
        return logging.Formatter.format(self, new_record)


def delete_old_logs(manager):
    """Keeps only last x logs, as specified in the settings file, from the logs folder based on the ``name`` argument.

    :param manager: AppManager object with the name and settings info
    :type manager: AppManager
    """
    # TODO: Add support for RotatingFileHandler (.log, .log.1, .log.2 files)
    logs = []

    print("Deleting old logs")
    for file in os.listdir(manager.settings.logs_path):
        contains_ext = re.search(r"\.log\.?\d?$", file) is not None
        if contains_ext and file.__contains__(manager.name):
            logs.append(file)

    logs.sort(reverse=True)
    logs_to_delete = logs[manager.settings.get("max_logs"):]

    for log in logs_to_delete:
        try:
            path = os.path.join(manager.settings.logs_path, log)
            print(f"Deleting file {path}")
            os.remove(path)
        except PermissionError as e:
            logging.warning(
                f'PermissionError while trying to delete log file "{log}"', exc_info=e
            )


def setup_logging(manager):
    prefix = "debug_" if manager.get_debug() else ""
    filename = f'{prefix}{manager.name}_{datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")}.log'
    log_path = os.path.join(manager.settings.logs_path, filename)

    delete_old_logs(manager)

    base_format = (
        "[$BOLD%(levelname)-8s$RESET] ($BOLD%(filename)s:%(lineno)d$RESET) %(message)s"
    )
    debug_base_format = (
        "[$BOLD%(levelname)-8s$RESET] {$ITALIC%(threadName)-10s$RESET} (%(funcName)s @ "
        "$BOLD%(filename)s:%(lineno)d$RESET) %(message)s "
    )
    chosen_format = debug_base_format if manager.get_debug() else base_format

    colored_format = formatter_message(chosen_format)
    file_format = formatter_message(chosen_format, False)

    config = {
        "version": 1,
        "formatters": {
            "coloredFormatter": {
                "format": colored_format,
                "style": "%",
                "validate": False,
                "class": "util.log_setup.ColoredFormatter",
            },
            "millisecondFormatter": {
                "format": file_format,
                "datefmt": "%H:%M:%S.%f",
                "style": "%",
                "class": "util.log_setup.MillisecondFormatter",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "coloredFormatter",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "encoding": "utf-8",
                "filename": log_path,
                "level": "DEBUG" if manager.get_debug() else "INFO",
                "formatter": "millisecondFormatter",
            },
        },
        "loggers": {
            "discord_fm": {
                "handlers": ["console", "file"],
                "level": "DEBUG" if manager.get_debug() else "INFO",
                "propagate": True,
            }
        },
        "disable_existing_loggers": True,
    }

    logging.config.dictConfig(config)

    print("Logging setup finished")
