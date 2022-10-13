import logging
import os
import subprocess
from platform import system
from typing import List

import psutil

from . import executable_info

logger = logging.getLogger("discord_fm").getChild(__name__)


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


def check_process_running(*process_names: str, ignore_self: bool = True) -> bool:
    """Check if there is any running process that contains the given names process_name.

    :param ignore_self: Should the method ignore itself and all related processes.
    :param process_names: Argument list of process names to look for. These strings will be made lowercase and have
    ".exe" removed from them.
    :return: Boolean indicating if the processes are running
    """
    logger.debug(f"Checking if {process_names} is running...")
    return len(get_external_process(*process_names, ignore_self=ignore_self)) != 0


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
            logger.info(f'Killing process "{p.name()}" ({p.pid})')
            p.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.debug(f"Recieved exception when trying to kill process", exc_info=e)


def stream_process(process: subprocess.Popen):
    """Prints all lines from the process `process`'s stdout.

    :param process: Popen process to stream from.
    """
    go = process.poll() is None
    for line in process.stdout:
        print(line.decode("utf-8"), end="")
    return go


def open_in_explorer(path: str):
    """Opens the app's log folder on the system's file explorer"""
    logger.debug(f'Opening "{path}" in system explorer')
    if system() == "Windows":
        os.startfile(path)
    elif system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
