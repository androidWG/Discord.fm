import argparse
import os
import platform
import shutil
import stat
import subprocess
import sys
from os import path as p

import build

PYINSTALLER_VER = "6.11.1"
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


def _check_util(cmd: str) -> None:
    if shutil.which(cmd) is None:
        print(
            "git is required to build PyInstaller. Download it from https://git-scm.com/download"
        )
        sys.exit(2)


def _run_simple(cmd: str | list[str], **kwargs) -> str | None:
    print(f'Running simple command "{cmd}"...\n')

    if isinstance(cmd, str):
        command = cmd.split(" ")
    else:
        command = cmd

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        **kwargs,
    )

    lines: list[str] = []
    for line in iter(process.stdout.readline, b""):
        line_as_string = line.decode().rstrip()
        lines.append(line_as_string)
        print(line_as_string)

    result = "\n".join(lines)
    process.stdout.close()
    process.wait()

    return result


def build_pyinstaller() -> None:
    _check_util("git")
    _delete("pyinstaller")

    _run_simple("git clone https://github.com/pyinstaller/pyinstaller.git")
    _run_simple(f"git checkout tags/v{PYINSTALLER_VER}", cwd=p.abspath("pyinstaller"))
    _run_simple(
        f"{python} ./waf all", cwd=p.abspath(p.join("pyinstaller", "bootloader"))
    )


if __name__ == "__main__":
    # region ArgumentParser Setup
    parser = argparse.ArgumentParser(
        description="Setup and manage the Discord.fm project."
    )
    # parser.add_argument(
    #     "--global",
    #     action="store_true",
    #     dest="no_venv",
    #     help="Force script to use global Python instead of venv",
    # )

    subparsers = parser.add_subparsers(help="Command to be executed", dest="command")

    sub_setup = subparsers.add_parser(
        "setup", help="Setup Discord.fm development environment"
    )
    sub_setup.add_argument(
        "--flatpak",
        action="store_true",
        help="Makes a manifest, builds and installs a Flatpak instead of Linux binaries.",
    )

    sub_build = subparsers.add_parser(
        "build", help="Build Discord.fm distribution binaries"
    )
    sub_build.add_argument(
        "-f", "--force", action="store_true", help="Force setup from scratch."
    )
    sub_build.add_argument(
        "-i",
        "--installer-only",
        action="store_false",
        dest="executable",
        help="Builds only the installer for the current platform. Will fail if no distribution executables are found",
    )
    sub_build.add_argument(
        "-b",
        "--build-only",
        action="store_false",
        dest="installer",
        help="Builds only the main executables of the program, and skips building the installer",
    )
    sub_build.add_argument(
        "-d",
        "--dirty",
        action="store_false",
        dest="cleanup",
        help="Skips cleanup, leaving temporary files and folders",
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
            if current_platform == "Windows":
                build_pyinstaller()

            _run_simple("uv ")

            print(f"Python path: {python}\nEnv path: {env_path}\nPip path: {pip}")
            print("\nSetup completed")
        case "build":
            check_venv(args.force, args.no_venv)
            check_pyinstaller(args.force)

            print("\nBuilding Discord.fm")
            bt = build.get_build_tool(python, args.flatpak)
            bt.prepare_files()
            if args.executable:
                bt.build()
                bt.package()
            if args.installer:
                bt.make_installer()
            if args.cleanup:
                bt.cleanup()

            print("\nBuild completed")
        case "run":
            check_venv(args.force, args.no_venv)

            print("\nRunning main.py...")
            _run_simple([python, "main.py"], cwd=p.abspath("src"), check=True)
        case "test":
            check_venv(args.force, args.no_venv)

            print("\n Running tests with pytest")
            env = os.environ.copy()
            env["PYTHONPATH"] = p.abspath("src") + ";" + p.abspath("tests")

            _run_simple(
                [python, "-m", "pytest", "tests/"],
                env=env,
            )

            print("\n Tests completed")
        case "format":
            check_venv(args.force, args.no_venv)

            paths = ["src", "build/*.py", "tests"]
            _run_simple([python, "-m", "black"] + paths)

            print("\nFormatting completed")
