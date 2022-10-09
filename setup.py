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
MARKER_NAME = ".setup_done"

current_platform = platform.system()
python = ""
env_path = ""
pip = []


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


def _run(
        cmd_list: List[List[str]] | List[str], cwd=os.getcwd()
) -> List[subprocess.CompletedProcess]:
    if type(cmd_list[0]) is str:
        commands = [cmd_list]
    else:
        commands = cmd_list

    results = []
    for cmd in commands:
        print(f'Running command "{cmd}"...\n')
        result = subprocess.run(cmd, cwd=cwd, stdout=sys.stdout, stderr=sys.stderr)
        results.append(result)

    return results


def check_venv(force: bool):
    print("Getting venv...\n")
    global python, env_path, pip

    env_name = "venv"
    if not p.isdir(env_name) or force:
        print("Creating new venv...\n")
        _delete("venv")
        env = venv.EnvBuilder(with_pip=True)
        env.create(env_name)

    if platform.system() == "Windows":
        python = p.abspath(p.join(env_name, "Scripts", "python.exe"))
    else:
        python = p.abspath(p.join(env_name, "bin", "python"))

    env_path = p.abspath(env_name)
    pip = [python, "-m", "pip", "install"]


def check_dependencies(force: bool):
    print("Checking dependencies...\n")
    marker = p.join(env_path, MARKER_NAME)
    if not p.isfile(marker) or force:
        pip_install = pip + ["black", "wheel"]
        commands = [pip + ["-r", "requirements.txt"]]

        if platform.system() == "Windows":
            pip_install.append("pywin32")
            commands.append(
                [
                    python,
                    p.join(env_path, "Scripts", "pywin32_postinstall.py"),
                    "-install",
                ]
            )
        elif platform.system() == "Darwin":
            pip_install.append("aquaui")
        elif platform.system() == "Linux":
            pip_install.append("PyYAML requirements-parser")

        commands.insert(1, pip_install)
        results = _run(commands)
        for r in results:
            if r.returncode != 0:
                print("Error while checking dependencies!")
                sys.exit(2)

        with open(marker, "w"):
            pass
    else:
        print("Dependencies already isntalled by setup.py")


def check_pyinstaller():
    print("Checking PyInstaller...\n")
    if platform.system() == "Windows":
        if shutil.which("git") is None:
            print(
                "git is required to build PyInstaller. Download it from https://git-scm.com/download"
            )
            sys.exit(2)

        _delete("pyinstaller")

        commands = ["git", "clone", "https://github.com/pyinstaller/pyinstaller.git"]
        _run(commands)

        commands = ["git", "checkout", f"tags/v{PYINSTALLER_VER}"]
        _run(commands, p.abspath("pyinstaller"))

        commands = [python, "./waf", "distclean", "all"]
        _run(commands, p.abspath(p.join("pyinstaller", "bootloader")))

        commands = [python, "setup.py", "install"]
        _run(commands, p.abspath("pyinstaller"))

        _delete("pyinstaller")
    elif platform.system() == "Linux":
        print("Linux does not use PyInstaller, skipping")
    else:
        commands = pip + ["PyInstaller"]
        _run(commands)


if __name__ == "__main__":
    # region ArgumentParser Setup
    parser = argparse.ArgumentParser(
        description="Setup and manage the Discord.fm project."
    )
    parser.add_argument(
        "command",
        type=str,
        nargs="?",
        choices=["setup", "build", "run", "format"],
        help="Command to be executed",
    )
    parser.add_argument(
        "-i",
        "--installer-only",
        action="store_false",
        dest="executable",
        help="Builds only the installer for the current platform. Will fail if no distribution executables are found",
    )
    parser.add_argument(
        "-b",
        "--build-only",
        action="store_false",
        dest="installer",
        help="Builds only the main executables of the program, and skips building the installer",
    )
    parser.add_argument(
        "-d",
        "--dirty",
        action="store_false",
        dest="cleanup",
        help="Skips cleanup, leaving temporary files and folders",
    )

    parser.add_argument(
        "-f",
        action="store_true",
        dest="force",
        help="Force setup from scratch. WARNING: Completely removed the venv folder!",
    )
    # endregion
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        parser.exit(1, "No command given")

    if current_platform not in ["Windows", "Linux", "Darwin"]:
        parser.exit(3, f'Platform "{current_platform}" is unsupported!')

    if args.command == "setup":
        check_venv(args.force)
        check_dependencies(args.force)
        print("\nSetup completed")
    elif args.command == "build":
        check_venv(args.force)
        check_dependencies(args.force)
        check_pyinstaller()

        print("Building Discord.fm\n")
        bt = build.get_build_tool()
        bt.prepare_files()
        if args.executable:
            bt.build()
        if args.installer:
            bt.make_installer()
        if args.cleanup:
            bt.cleanup()

        print("\nBuild completed")
    elif args.command == "run":
        check_venv(args.force)
        check_dependencies(args.force)

        print("Running main.py...\n")
        subprocess.Popen([python, "main.py"], cwd=p.abspath("src"))
    elif args.command == "format":
        check_venv(args.force)
        check_dependencies(args.force)

        paths = ["src", "build/*.py", "tests"]
        _run([python, "-m", "black"] + paths)

        print("\nFormatting completed")
