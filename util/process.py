import logging
import os
import subprocess
import psutil
from platform import system
from install import get_install_folder
from util import is_frozen


class ExecutableInfo:
    def __init__(self, name, windows_exe_name="", macos_app_name="", script_path=""):
        self.name = name
        self.windows_exe_name = windows_exe_name
        self.macos_app_name = macos_app_name
        self.script_path = script_path

    @property
    def path(self):
        install_path = get_install_folder(self.windows_exe_name, self.macos_app_name)

        current_platform = system()
        if current_platform == "Windows":
            path = os.path.abspath(self.windows_exe_name)
        elif current_platform == "Darwin":
            path = os.path.abspath(self.macos_app_name)
        else:
            raise NotImplementedError

        if os.path.isfile(path):
            return path
        elif os.path.isfile(install_path) and is_frozen():
            return install_path
        elif not is_frozen():
            python_path = os.path.abspath("venv/Scripts/python.exe"
                                          if current_platform == "Windows" else "venv/bin/python")
            return [python_path, self.script_path]


def get_external_process(*process_names) -> list[psutil.Process]:
    logging.debug(f"Searching for process {process_names}...")
    related_processes = [psutil.Process().pid, psutil.Process(os.getppid()).pid]
    matched = []

    for process in psutil.process_iter():
        try:
            for name in process_names:
                cleaned_name = process.name().lower().replace(".exe", "")
                if name.lower() == cleaned_name and process.pid not in related_processes:
                    matched.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    logging.debug(f"Found {len(matched)} matches")
    return matched


def check_process_running(*process_names):
    """Check if there is any running process that contains the given name process_name."""
    logging.info(f"Checking if {process_names} is running...")
    return len(get_external_process(*process_names)) != 0


def kill_process(process_name):
    """Tries to kill any running process tree that contains the given name process_name."""
    logging.debug(f"Attempting to kill process tree \"{process_name}\"...")
    proc = get_external_process(process_name)[0]
    proc_pid = proc.pid if proc.parent() is None else proc.parent().pid

    parent = psutil.Process(proc_pid)
    children = parent.children(recursive=True)
    children.append(parent)

    for p in children:
        try:
            p.kill()
        except psutil.NoSuchProcess:
            pass


def stream_process(process):
    go = process.poll() is None
    for line in process.stdout:
        print(line.decode("utf-8"), end="")
    return go


def start_stop_service(process: ExecutableInfo):
    if check_process_running(process.name):
        kill_process(process.name)
    else:
        subprocess.Popen(process.path)


def open_settings():
    settings_proc = ExecutableInfo("settings_ui", "settings_ui.exe", "Discord.fm Settings.app", os.path.join("ui", "ui.py"))
    subprocess.Popen(settings_proc.path)
