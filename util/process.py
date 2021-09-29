import logging
import os
import subprocess
import psutil
from platform import system
from install import get_executable


def get_external_process(*process_names) -> list[psutil.Process]:
    related_processes = [psutil.Process().pid, psutil.Process(os.getppid()).pid]
    matched = []

    for process in psutil.process_iter():
        try:
            for name in process_names:
                cleaned_name = process.name().lower().replace(".exe", "")
                if name.lower() == cleaned_name and process.pid not in related_processes:
                    logging.debug(f"Found matching process, name \"{cleaned_name}\" and ID {process.pid}")

                    matched.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return matched


def check_process_running(*process_names):
    """Check if there is any running process that contains the given name process_name."""
    logging.info(f"Checking if {process_names} is running...")
    return len(get_external_process(*process_names)) != 0


def kill_process(process_name):
    """Tries to kill any running process that contains the given name process_name."""
    logging.debug(f"Attempting to kill {process_name} process...")
    for process in get_external_process(process_name):
        process.kill()


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
        print(line.decode("utf-8"), end="")
    return go
