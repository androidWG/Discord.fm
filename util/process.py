import logging
import os
import subprocess
import sys
import psutil
from platform import system
from settings import local_settings
from util.install import get_install_folder
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


def get_external_process(*process_names, ignore_self=True) -> list[psutil.Process]:
    logging.debug(f"Searching for process {process_names}...")
    related_processes = [psutil.Process().pid, psutil.Process(os.getppid()).pid] if ignore_self else []
    matched = []

    for process in psutil.process_iter():
        try:
            for proc in process_names:
                name = process.name().lower().replace(".exe", "")
                if proc.lower() == name and process.pid not in related_processes:
                    matched.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    logging.debug(f"Found {len(matched)} matches")
    return matched


def check_process_running(*process_names):
    """Check if there is any running process that contains the given name process_name."""
    logging.info(f"Checking if {process_names} is running...")
    return len(get_external_process(*process_names)) != 0


def kill_process(process_name, ignore_self=True):
    """Tries to kill any running process tree that contains the given name process_name."""
    logging.debug(f"Attempting to kill process tree \"{process_name}\"...")
    proc = get_external_process(process_name, ignore_self=ignore_self)[0]
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
    settings_proc = ExecutableInfo("settings_ui", "settings_ui.exe", "Discord.fm Settings.app",
                                   os.path.join("ui", "ui.py"))
    subprocess.Popen(settings_proc.path)


def open_logs_folder():
    """Opens the app's log folder on the system's file explorer"""
    if system() == "Windows":
        os.startfile(local_settings.logs_path)
    elif system() == "Darwin":
        subprocess.Popen(["open", local_settings.logs_path])
    else:
        subprocess.Popen(["xdg-open", local_settings.logs_path])


# From https://stackoverflow.com/a/16993115/8286014
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt) or issubclass(exc_type, SystemExit):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    main_proc = ExecutableInfo("Discord.fm", "discord_fm.exe", "Discord.fm.app", "main.py")
    subprocess.Popen([main_proc.path, "--ignore-open"])

    sys.exit(10)
