import logging
import psutil


# From https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
def check_process_running(name):
    """Check if there is any running process that contains the given name processName."""
    logging.debug(f"Checking if {name} process is running...")
    for proc in psutil.process_iter():
        try:
            if name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def kill_process(name):
    logging.debug(f"Attempting to kill {name} process...")
    for proc in psutil.process_iter():
        try:
            if name.lower() in proc.name().lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            logging.info(f"Process \"{name}\" doesn't exit")

