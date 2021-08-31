import datetime
import logging
import os
import datetime as dt
import sys
from util.settings import local_settings


class MillisecondFormatter(logging.Formatter):
    """A formatter for standard library 'logging' that supports '%f' wildcard in format strings."""
    converter = dt.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)[:-3]
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


def delete_old_logs(name: str):
    """Keeps only last x logs, as specified in the settings file, from the logs folder based on the ``name`` argument.

    :param name:  Log name to use
    :type name: str
    """
    logs = []
    for file in os.listdir(local_settings.logs_path):
        if file.endswith(".log") and file.__contains__(name):
            logs.append(file)

    logs.sort(reverse=True)
    del logs[:local_settings.max_logs - 1]

    for log in logs:
        os.remove(os.path.join(local_settings.logs_path, log))


def setup_logging(name: str):
    filename = name + datetime.datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S") + ".log"
    log_path = os.path.join(local_settings.logs_path, filename)

    delete_old_logs(name)

    logging.basicConfig(
        filename=log_path,
        filemode="w",
        level=logging.DEBUG)

    # Set custom Formatter to support DateFormats with milliseconds
    formatter = MillisecondFormatter(fmt="%(asctime)s | %(levelname)-8s | %(message)s",
                                     datefmt="%H:%M:%S.%f")
    log_handler = logging.getLogger().handlers[0]
    log_handler.setFormatter(formatter)

    # Add stdout to log exceptions and also idk why but it makes logging calls print to console too
    # Part of code from https://stackoverflow.com/a/16993115/8286014
    system_handler = logging.StreamHandler(stream=sys.stdout)
    logging.getLogger().addHandler(system_handler)

    logging.info("Logging setup finished")
