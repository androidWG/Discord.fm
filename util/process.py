import logging
import os
import subprocess
import psutil
from platform import system
from install import get_executable


# From https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
def check_process_running(process_name):
    """Check if there is any running process that contains the given name process_name."""
    logging.debug(f"Checking if {process_name} process is running...")
    for proc in psutil.process_iter():
        try:
            if process_name.lower() in proc.name().lower() and not proc.pid == os.getpid():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def kill_process(process_name):
    """Tries to kill any running process that contains the given name process_name."""
    logging.debug(f"Attempting to kill {process_name} process...")
    for proc in psutil.process_iter():
        try:
            if process_name.lower() in proc.name().lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            logging.info(f"Process \"{process_name}\" doesn't exist")


def start_stop_service(name, windows_exe_name, macos_app_name, script_path):
    if check_process_running(name):
        kill_process(name)
    else:
        start_process(name, windows_exe_name, macos_app_name, script_path)


def start_process(name, windows_exe_name, macos_app_name, script_path):
    current_os = system()
    if current_os == "Windows":
        path = os.path.abspath(windows_exe_name)
    elif current_os == "Darwin":
        path = os.path.abspath(macos_app_name)
    else:
        path = os.path.abspath(name)

    if os.path.isfile(path):
        logging.debug("Found executable in current working folder")
        install_path = path
    else:
        install_path = get_executable(windows_exe_name, f"/Applications/{macos_app_name}", script_path)
    subprocess.Popen(args=install_path)


def stream_process(process):
    go = process.poll() is None
    for line in process.stdout:
        logging.info(line.decode("utf-8"), end="")
    return go
