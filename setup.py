import argparse
import os
import platform
import shutil
import stat
import subprocess
import sys
from os import path as p
from typing import List

import build

PYINSTALLER_VER = "5.4.1"
MARKER_NAME = ".setup_done"

current_platform = platform.system()
python = ""
env_path = ""
pip = []


def _delete(path: str | os.PathLike[str]):
    files = []
    if p.isfile(path):
        files.append(path)
    elif p.isdir(path):
        for root, d, f in os.walk(path):
            files += [p.abspath(p.join(root, x)) for x in f]
    else:
        print(f'_delete: Ignoring invalid path "{path}"')
        return

    for file in files:
        try:
            os.chmod(file, stat.S_IWRITE)
            os.remove(file)
        except FileNotFoundError:
            print(f"Unable to find file {file}", file=sys.stderr)

    shutil.rmtree(p.abspath(path))


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


def _run_simple_result(cmd: str) -> str:
    print(f'Running simple command "{cmd}"...\n')
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8").strip()


def check_venv(force: bool, no_venv: bool):
    print("\nGetting venv...")
    global python, env_path, pip

    env_name = _run_simple_result("pipenv --venv")
    if (not p.isdir(env_name) or env_name == "" or force) and not no_venv:
        print("Running pipenv...\n")
        subprocess.run("pipenv --python=3.11 install --dev", stdout=sys.stdout, stderr=sys.stderr)

    python = _run_simple_result("pipenv --py")

    if no_venv:
        python = "python"
        env_path = os.path.dirname(sys.executable)
    else:
        env_path = env_name
    pip = [python, "-m", "pip", "install"]


def __pyinstaller_installed() -> bool:
    packages = p.join(env_path, "Lib", "site-packages")
    for x in os.listdir(packages):
        path = p.join(packages, x)
        if p.isdir(p.abspath(path)) and x.__contains__("pyinstaller"):
            return True

    return False


def check_pyinstaller():
    print("\nChecking PyInstaller...")

    if __pyinstaller_installed():
        print("PyInstaller is already installed, skipping")
        return

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
        choices=["setup", "build", "run", "format", "test"],
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
        help="Force setup from scratch.",
    )
    parser.add_argument(
        "--global",
        action="store_true",
        dest="no_venv",
        help="Force script to use global Python instead of venv",
    )
    # endregion

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        parser.exit(1, "No command given")

    if current_platform not in ["Windows", "Linux", "Darwin"]:
        parser.exit(3, f'Platform "{current_platform}" is unsupported!')

    match args.command:
        case "setup":
            check_venv(args.force, args.no_venv)
            print("\nSetup completed")
        case "build":
            check_venv(args.force, args.no_venv)
            check_pyinstaller()

            print("\nBuilding Discord.fm")
            bt = build.get_build_tool()
            bt.prepare_files()
            if args.executable:
                bt.build()
            if args.installer:
                bt.make_installer()
            if args.cleanup:
                bt.cleanup()

            print("\nBuild completed")
        case "run":
            check_venv(args.force, args.no_venv)

            print("\nRunning main.py...")
            subprocess.run([python, "main.py"], cwd=p.abspath("src"), check=True)
        case "test":
            check_venv(args.force, args.no_venv)

            print("\n Running tests with unittest")
            env = os.environ.copy()
            env["PYTHONPATH"] = p.abspath("src") + ";" + p.abspath("tests")
            subprocess.run(
                [python, "-m", "unittest", "discover"],
                env=env,
                cwd=p.abspath("tests/unit"),
                check=True,
            )

            print("\n Tests completed")
        case "format":
            check_venv(args.force, args.no_venv)

            paths = ["src", "build/*.py", "tests"]
            _run([python, "-m", "black"] + paths)

            print("\nFormatting completed")
