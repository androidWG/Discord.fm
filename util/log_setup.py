import datetime
import logging.config
import os
import datetime as dt
import re
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


def delete_old_logs(name: str):
    """Keeps only last x logs, as specified in the settings file, from the logs folder based on the ``name`` argument.

    :param name:  Log name to use
    :type name: str
    """
    logs = []

    for file in os.listdir(local_settings.logs_path):
        contains_ext = re.search(r"\.log\.?\d?$", file) is not None
        if contains_ext and file.__contains__(name):
            logs.append(file)

    logs.sort(reverse=True)
    del logs[:local_settings.get("max_logs") - 1]

    for log in logs:
        try:
            os.remove(os.path.join(local_settings.logs_path, log))
        except PermissionError as e:
            logging.warning(f"PermissionError while trying to delete log file \"{log}\"", exc_info=e)


def setup_logging(name: str):
    prefix = "debug_" if get_debug() else ""
    filename = prefix + name + datetime.datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S") + ".log"
    log_path = os.path.join(local_settings.logs_path, filename)

    delete_old_logs(name)

    config = {"version": 1,
              "formatters": {
                  "millisecondFormatter": {
                      "format": "%(asctime)s | %(levelname)-8s | %(message)s",
                      "datefmt": "%H:%M:%S.%f",
                      "style": "%",
                      "validate": True,
                      "class": "util.log_setup.MillisecondFormatter"
                  }
              },
              "handlers": {
                  "console": {
                      "class": "logging.StreamHandler",
                      "level": "DEBUG" if get_debug() else "INFO",
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
