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
SYNC_CMD = "uv sync --no-binary-package pyinstaller --dev"
PYTHON_FIND_CMD = "uv python find"
TKINTER_MESSAGE = "tkinter is required to build and run Discord.fm. Check instructions for your OS at https://stackoverflow.com/a/25905642"


def _delete(path: str | os.PathLike[str]) -> None:
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


def _check_util(cmd: str, message: str = None) -> None:
    if shutil.which(cmd) is None:
        print(message)
        sys.exit(2)


class Setup:
    current_platform = platform.system()
    python = None

    def __init__(self, parsed_args):
        if self.current_platform not in ["Windows", "Linux", "Darwin"]:
            parser.exit(3, f'Platform "{self.current_platform}" is unsupported!')

        self.no_venv = parsed_args.no_venv
        self.command = parsed_args.command

    def _find_tools(self) -> None:
        self.python = self._run(PYTHON_FIND_CMD, echo=False)

    def _check_package(self, pkg: str, message: str = None) -> None:
        result = self._run(f"{self.python} -m {pkg}", use_stderr=True, echo=False)
        if f"No module named " in result:
            print(message)
            sys.exit(4)

    def _run(
        self,
        cmd: str | list[str],
        use_stderr: bool = False,
        echo: bool = True,
        **kwargs,
    ) -> str | None:
        # print(f'Running command "{cmd}"...\n')

        if isinstance(cmd, str):
            command = cmd.split(" ")
        else:
            command = cmd

        env = os.environ.copy()
        if self.no_venv:
            env["UV_PYTHON_PREFERENCE"] = "only-system"

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            **kwargs,
        )

        lines: list[str] = []
        out = process.stderr if use_stderr else process.stdout
        for line in out:
            lines.append(line.rstrip())
            if echo:
                print(line)

        result = "\n".join(lines)
        process.stdout.close()
        process.wait()

        return result

    def build_pyinstaller(self) -> None:
        _check_util(
            "git",
            "git is required to clone PyInstaller for building. Download it from https://git-scm.com/download",
        )
        _delete("pyinstaller")

        self._run("git clone https://github.com/pyinstaller/pyinstaller.git")
        self._run(f"git checkout tags/v{PYINSTALLER_VER}", cwd=p.abspath("pyinstaller"))
        self._run(
            f"{self.python} ./waf all",
            cwd=p.abspath(p.join("pyinstaller", "bootloader")),
        )

    def execute_command(self) -> None:
        self._run(SYNC_CMD)

        match self.command:
            case "setup":
                print("\nSetup completed")
            case "build":
                print("\nBuilding Discord.fm")
                self._find_tools()
                self._check_package(
                    "tkinter",
                    TKINTER_MESSAGE,
                )

                bt = build.get_build_tool(self.python, args.flatpak)
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
                print("\nRunning main.py...")
                self._find_tools()
                self._check_package(
                    "tkinter",
                    TKINTER_MESSAGE,
                )

                self._run(
                    [self.python, "main.py"],
                    cwd=p.abspath("src"),
                )

                sys.exit(0)


if __name__ == "__main__":
    # region ArgumentParser Setup
    parser = argparse.ArgumentParser(
        description="Setup and manage the Discord.fm project."
    )
    parser.add_argument(
        "--global",
        action="store_true",
        dest="no_venv",
        help="Force script to use global Python instead of uv's venv",
    )

    subparsers = parser.add_subparsers(help="Command to be executed", dest="command")

    sub_run = subparsers.add_parser("run", help="Run Discord.fm")

    sub_setup = subparsers.add_parser(
        "setup", help="Setup Discord.fm development environment"
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
        help="Builds only the installer for the current platform. Will fail if no distribution executables are found.",
    )
    sub_build.add_argument(
        "-b",
        "--build-only",
        action="store_false",
        dest="installer",
        help="Builds only the main executables of the program, and skips building the installer.",
    )
    sub_build.add_argument(
        "-d",
        "--dirty",
        action="store_false",
        dest="cleanup",
        help="Skips cleanup, leaving temporary files and folders.",
    )
    sub_build.add_argument(
        "--flatpak",
        action="store_true",
        help="Builds and installs a Flatpak instead of Linux binaries.",
    )
    # endregion

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        parser.exit(1, "No command given")

    _check_util(
        "uv",
        "uv is needed for package management. Instructions at https://docs.astral.sh/uv/getting-started/installation/",
    )

    setup = Setup(args)
    setup.execute_command()
