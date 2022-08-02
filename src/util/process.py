import logging
import os
import subprocess
import sys
from platform import system
from typing import List

import psutil

import globals as g
from globals import local_settings
from util import is_frozen
from util.install import get_install_folder

logger = logging.getLogger("discord_fm").getChild(__name__)


class ExecutableInfo:
    def __init__(
        self, name, windows_exe_name, macos_app_name, linux_executable_name, script_path
    ):
        """Holds info about an executable and gives its path independent of platform or app state (frozen or not).

        :param name: General process name
        :param windows_exe_name: Name of the specific Windows .exe for this executable.
        :param macos_app_name: Name of the specific macOS .app folder for this executable.
        :param script_path: Path of the script to be run if the app is not frozen.
        """
        self.name = name
        self.windows_exe_name = windows_exe_name
        self.macos_app_name = macos_app_name
        self.linux_executable_name = linux_executable_name
        self.script_path = script_path

    @property
    def path(self) -> List[str]:
        """Gets the full path of this executable for this instance of the app. If the app is not frozen, a path to the
        Python interpreter with the script as an argument will be passed."""
        install_path = get_install_folder(self.windows_exe_name, self.macos_app_name)

        current_platform = system()
        if current_platform == "Windows":
            path = os.path.abspath(self.windows_exe_name)
        elif current_platform == "Darwin":
            path = os.path.abspath(self.macos_app_name)
        else:
            path = os.path.abspath(self.linux_executable_name)

        if os.path.isfile(path):
            logger.debug(f'Path for "{self.name}": "{path}"')
            return [path]
        elif os.path.isfile(install_path) and is_frozen():
            logger.debug(f'Path for "{self.name}": "{install_path}"')
            return [install_path]
        elif not is_frozen():
            python_path = os.path.abspath(
                "venv/Scripts/python.exe"
                if current_platform == "Windows"
                else "venv/bin/python"
            )
            logger.debug(f'Path for "{self.name}": "{[python_path, self.script_path]}"')
            return [python_path, self.script_path]


# noinspection PyUnreachableCode
def get_external_process(
    *process_names: str, ignore_self: bool = True
) -> List[psutil.Process]:
    """Returns a list of all the processes that match any of the names given as args, and ignores itself by default.

    :param process_names: Argument list of process names to look for. These strings will be made lowercase and have
    ".exe" removed from them.
    :param ignore_self: Should the method ignore itself and all related processes.
    """
    related_processes = []
    if ignore_self:
        try:
            related_processes.append(psutil.Process().pid)
            related_processes.append(psutil.Process(os.getppid()).pid)
        except psutil.NoSuchProcess as e:
            logger.error("Unable to get related processes", exc_info=e)
    matched = []

    try:
        process_list = psutil.process_iter()
    except psutil.AccessDenied:
        g.manager.close()  # Exit from here since the unexpected exception handler uses kill_process
        return []

    for process in process_list:
        try:
            for proc in process_names:
                name = process.name().lower().replace(".exe", "")
                if proc.lower() == name and process.pid not in related_processes:
                    matched.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    logger.debug(f"Found {len(matched)} matches for {process_names}")
    return matched


def check_process_running(*process_names: str) -> bool:
    """Check if there is any running process that contains the given names process_name.

    :param process_names: Argument list of process names to look for. These strings will be made lowercase and have
    ".exe" removed from them.
    :return: Boolean indicating if the processes are running
    """
    logger.debug(f"Checking if {process_names} is running...")
    return len(get_external_process(*process_names)) != 0


def kill_process(process_name: str, ignore_self=True):
    """Tries to kill any running process tree that contains the given name process_name.

    :param process_name: Name of the process to kill, will be made lowercase and have ".exe" removed from it.
    :param ignore_self: Should the method ignore itself and all related processes.
    """
    logger.debug(f'Attempting to kill process tree "{process_name}"...')
    proc = get_external_process(process_name, ignore_self=ignore_self)[0]
    proc_pid = proc.pid if proc.parent() is None else proc.parent().pid

    parent = psutil.Process(proc_pid)
    children = parent.children()
    children.append(parent)

    for p in children:
        try:
            logger.debug(f'Killing process "{p.name()}" ({p.pid})')
            p.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def stream_process(process: subprocess.Popen):
    """Prints all lines from the process `process`'s stdout.

    :param process: Popen process to stream from.
    """
    go = process.poll() is None
    for line in process.stdout:
        print(line.decode("utf-8"), end="")
    return go


def start_stop_process(process: ExecutableInfo):
    """Checks if `process` is running, if it is, try to kill it. If it isn't, run it.

    :param process: Executable to start or stop.
    """
    if check_process_running(process.name):
        kill_process(process.name)
    else:
        subprocess.Popen(process.path)


def open_settings():
    """Opens the settings UI. Works even if the app is not frozen (is running as a script)."""
    logger.debug("Opening settings UI")
    settings_proc = ExecutableInfo(
        "settings_ui",
        "settings_ui.exe",
        "Discord.fm Settings.app",
        "discord_fm",
        os.path.join("ui", "ui.py"),
    )
    subprocess.Popen(settings_proc.path, cwd=os.getcwd())


def open_logs_folder():
    """Opens the app's log folder on the system's file explorer"""
    logger.debug("Opening logs folder")
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

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    logger.debug(f"Current status: {g.current}")

    if g.current != g.Status.KILL:
        main_proc = ExecutableInfo(
            "Discord.fm", "discord_fm.exe", "Discord.fm.app", "discord_fm", "main.py"
        )
        subprocess.Popen(main_proc.path + ["--ignore-open"])

    g.manager.close()
