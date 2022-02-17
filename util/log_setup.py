import copy
import datetime
import logging.config
import logging.handlers
import os
import re
import datetime as dt
from settings import local_settings, get_debug


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


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def formatter_message(message, use_color=True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        new_record = copy.copy(record)
        levelname = new_record.levelname

        if levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            new_record.levelname = levelname_color
        return logging.Formatter.format(self, new_record)


def delete_old_logs(name: str):
    """Keeps only last x logs, as specified in the settings file, from the logs folder based on the ``name`` argument.

    :param name:  Log name to use
    :type name: str
    """
    logs = []

    print("Deleting old logs")
    for file in os.listdir(local_settings.logs_path):
        contains_ext = re.search(r"\.log\.?\d?$", file) is not None
        if contains_ext and file.__contains__(name):
            logs.append(file)

    logs.sort(reverse=True)
    del logs[:local_settings.get("max_logs") - 1]

    for log in logs:
        try:
            path = os.path.join(local_settings.logs_path, log)
            print(f"Deleting file {path}")
            os.remove(path)
        except PermissionError as e:
            logging.warning(f"PermissionError while trying to delete log file \"{log}\"", exc_info=e)


def setup_logging(name: str):
    prefix = "debug" if get_debug() else ""
    filename = f'{prefix}_{name}_{datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")}.log'
    log_path = os.path.join(local_settings.logs_path, filename)

    delete_old_logs(name)

    base_format = "[$BOLD%(levelname)-8s$RESET] ($BOLD%(filename)s:%(lineno)d$RESET) %(message)s"
    colored_format = formatter_message(base_format, True)

    config = {"version": 1,
              "formatters": {
                  "coloredFormatter": {
                      "format": colored_format,
                      "style": "%",
                      "validate": False,
                      "class": "util.log_setup.ColoredFormatter"
                  },
                  "millisecondFormatter": {
                      "format": "%(asctime)s | %(levelname)-8s | %(message)s",
                      "datefmt": "%H:%M:%S.%f",
                      "style": "%",
                      "class": "util.log_setup.MillisecondFormatter"
                  }
              },
              "handlers": {
                  "console": {
                      "class": "logging.StreamHandler",
                      "level": "DEBUG",
                      "formatter": "coloredFormatter",
                      "stream": "ext://sys.stdout"
                  },
                  "file": {
                      "class": "logging.handlers.RotatingFileHandler",
                      "filename": log_path,
                      "level": "DEBUG" if get_debug() else "INFO",
                      "formatter": "millisecondFormatter",
                      "maxBytes": 512000,
                      "backupCount": 2
                  }
              },
              "loggers": {
                  "discord_fm": {
                      "handlers": ["console", "file"],
                      "level": "DEBUG" if get_debug() else "INFO",
                      "propagate": True
                  }
              },
              "disable_existing_loggers": True}

    logging.config.dictConfig(config)

    print("Logging setup finished")
