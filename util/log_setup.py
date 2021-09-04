import datetime
import logging
import os
import datetime as dt
import sys
import settings


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
    for file in os.listdir(settings.logs_path):
        if file.endswith(".log") and file.__contains__(name):
            logs.append(file)

    logs.sort(reverse=True)
    del logs[:settings.get("max_logs") - 1]

    for log in logs:
        os.remove(os.path.join(settings.logs_path, log))


def setup_logging(name: str):
    filename = name + datetime.datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S") + ".log"
    log_path = os.path.join(settings.logs_path, filename)

    delete_old_logs(name)

    # Set custom Formatter to support DateFormats with milliseconds
    formatter = MillisecondFormatter(fmt="%(asctime)s | %(levelname)-8s | %(message)s",
                                     datefmt="%H:%M:%S.%f")
    root_logger = logging.getLogger()
    root_logger.removeHandler(root_logger.handlers[0])  # Remove stderr handler to prevent duplicate printing
    root_logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    root_logger.addHandler(console_handler)

    logging.info("Logging setup finished")
