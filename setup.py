import argparse
import os
import platform
import shutil
import subprocess
import sys
from os import path as p
from typing import List

import venv

import build

PYINSTALLER_VER = "5.4.1"

current_platform = platform.system()
python = ""
env_path = ""
pip = ""


def _delete(path: str | os.PathLike[str]):
    if p.isdir(path):
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            print(f'Folder "{path}" was not found!')
    elif p.isfile(path):
        try:
            os.remove(path)
        except FileNotFoundError:
            print(f'File "{path}" was not found!')
    else:
        raise ValueError("Not a valid path")


def _run(cmd_list: List[str], cwd=os.getcwd()):
    for cmd in cmd_list:
        subprocess.run(cmd, cwd=cwd)


def check_venv():
    env_name = "venv"
    if not p.isdir(env_name):
        global python, env_path
        env = venv.EnvBuilder(with_pip=True)
        env.create(env_name)

    if platform.system() == "Windows":
        python = p.abspath(p.join(env_name, "Scripts", "python.exe "))
    else:
        python = p.abspath(p.join(env_name, "bin", "python "))

    env_path = p.abspath(env_name)


def check_dependencies():
    global pip
    pip = python + "-m pip install "
    commands = [pip + "-r requirements.txt", pip + "black wheel"]

    if platform.system() == "Windows":
        commands.append(pip + "pywin32")
        commands.append(
            env_path + p.join("Scripts", "pywin32_postinstall.py") + " -install"
        )
    elif platform.system() == "Darwin":
        commands.append(pip + "aquaui")
    elif platform.system() == "Linux":
        commands.append(pip + "PyYAML requirements-parser")

    _run(commands)


def check_pyinstaller():
    if platform.system() == "Windows":
        if shutil.which("git") is None:
            print(
                "git is required to build PyInstaller. Download it from https://git-scm.com/download"
            )
            sys.exit(2)

        _delete("pyinstaller")

        commands = ["git clone https://github.com/pyinstaller/pyinstaller.git"]
        _run(commands)

        commands = [f"git checkout tags/v{PYINSTALLER_VER}"]
        _run(commands, p.abspath("pyinstaller"))

        commands = [python + "./waf distclean all"]
        _run(commands, p.abspath(p.join("pyinstaller", "bootloader")))

        commands = [python + "setup.py install"]
        _run(commands, p.abspath("pyinstaller"))

        _delete("pyinstaller")
    elif platform.system() == "Linux":
        print("Linux does not use PyInstaller, skipping")
    else:
        commands = [pip + "PyInstaller"]
        _run(commands)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Setup & manage the Discord.fm project")
    parser.add_argument(
        "command",
        type=str,
        nargs="?",
        required=True,
        choices=["setup", "build"],
        help="Command to be executed.",
    )
    parser.add_argument(
        "--installer-only",
        "-i",
        action="store_false",
        dest="executable",
        help="Builds only the installer for the current platform. Will fail if no distribution executables are found.",
    )
    parser.add_argument(
        "--build-only",
        "-i",
        action="store_false",
        dest="installer",
        help="Builds only the main executables of the program, and skips building the installer.",
    )
    parser.add_argument(
        "--dirty",
        action="store_false",
        dest="cleanup",
        help="Skips cleanup, leaving temporary files and folders.",
    )

    if current_platform not in ["Windows", "Linux", "Darwin"]:
        print(f'Platform "{current_platform}" is unsupported!')

    args = parser.parse_args()
    if args.command == "setup":
        check_venv()
        check_dependencies()
    elif args.command == "build":
        check_venv()
        check_dependencies()
        check_pyinstaller()

        bt = build.get_build_tool()
        bt.prepare_files()
        if args.executable:
            bt.build()
        if args.installer:
            bt.make_installer()
        if args.cleanup:
            bt.cleanup()
