import argparse
import os
import platform
import shutil
import stat
import subprocess
import sys
from os import path as p

import build


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    GREY = "\033[90m"


PYINSTALLER_VER = "6.11.1"
SYNC_CMD = "uv sync --no-binary-package pyinstaller --dev"
PYTHON_FIND_CMD = "uv python find"
TKINTER_MESSAGE = f"{Colors.FAIL}tkinter is required to build and run Discord.fm. Check instructions for your OS at https://stackoverflow.com/a/25905642{Colors.ENDC}"


def _delete(path: str | os.PathLike[str]) -> None:
    files = []
    if p.isfile(path):
        files.append(path)
    elif p.isdir(path):
        for root, d, f in os.walk(path):
            files += [p.abspath(p.join(root, x)) for x in f]
    else:
        print(f'_delete: {Colors.WARNING}Ignoring invalid path "{path}"{Colors.ENDC}')
        return

    for file in files:
        try:
            os.chmod(file, stat.S_IWRITE)
            os.remove(file)
        except FileNotFoundError:
            print(f"{Colors.FAIL}Unable to find file {file}{Colors.ENDC}")

    shutil.rmtree(p.abspath(path))


def _check_util(cmd: str, message: str = None) -> None:
    if shutil.which(cmd) is None:
        print(message)
        sys.exit(2)


def _print_header(message: str, color=Colors.HEADER) -> None:
    print(f"{Colors.BOLD}{color}{message}{Colors.ENDC}")


def _print_subheader(message: str, color=Colors.HEADER) -> None:
    print(f"{color} └ {message}{Colors.ENDC}")


class Setup:
    current_platform = platform.system()
    python = None

    def __init__(self, parsed_args):
        if self.current_platform not in ["Windows", "Linux", "Darwin"]:
            parser.exit(
                3,
                f'{Colors.FAIL}Platform "{self.current_platform}" is unsupported!{Colors.ENDC}',
            )

        self.no_venv = parsed_args.no_venv
        self.command = parsed_args.command
        self.output = parsed_args.output

    def _find_tools(self) -> None:
        _print_subheader("Finding Python binary")
        self.python = self._run(PYTHON_FIND_CMD)

    def _check_package(self, pkg: str, message: str = None) -> None:
        _print_subheader("Checking Python packages")

        result = self._run([self.python, "-c", f'"import {pkg}"'], use_stderr=True)
        if result == "":
            pass
        elif f"No module named " in result:
            print(message)
            sys.exit(4)
        else:
            print(f"{Colors.FAIL}Unexpected error:")
            print(result)
            print(f"{Colors.ENDC}")
            sys.exit(5)

    def _run(
        self,
        cmd: str | list[str],
        use_stderr: bool = False,
        echo_stderr: bool = True,
        echo_stdout: bool = True,
        **kwargs,
    ) -> str | None:
        if isinstance(cmd, str):
            command = cmd.split(" ")
        else:
            command = cmd

        cmd_print = f"{Colors.GREY} ─ {" ".join(command)}{Colors.ENDC}"
        if self.output:
            # Don't print newline to be able to replace this line later
            print(cmd_print, end="\r")

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

        out_lines: list[str] = []
        err_lines: list[str] = []

        for line in process.stderr:
            err_lines.append(line.rstrip())
            if echo_stderr and self.output:
                # Print over old line if there's output
                if len(err_lines) <= 1 and len(out_lines) == 0:
                    print(cmd_print.replace("─", "┬"))
                print(f"{Colors.GREY} │ {line.rstrip()}{Colors.ENDC}")

        for line in process.stdout:
            out_lines.append(line.rstrip())
            if echo_stdout and self.output:
                # Same here...
                if len(out_lines) <= 1 and len(err_lines) == 0:
                    print(cmd_print.replace("─", "┬"))
                print(f"{Colors.GREY} │ {line}{Colors.ENDC}")

        result = "\n".join(err_lines if use_stderr else out_lines)
        process.stdout.close()
        process.wait()

        # Place a newline if no output is printed so the next print doesn't overwrite the command output
        if len(err_lines) == 0 and len(out_lines) == 0 and self.output:
            print("\n")

        return result

    def sync(self):
        _print_header("Syncing")
        self._run(SYNC_CMD)

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
        self.sync()

        match self.command:
            case "setup":
                _print_header("Setup completed")
            case "build":
                _print_header("Building Discord.fm")
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

                _print_header("Build completed", Colors.OKGREEN)
            case "run":
                _print_header("Running main.py")
                self._find_tools()
                self._check_package(
                    "tkinter",
                    TKINTER_MESSAGE,
                )

                # TODO: Fix no output
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
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_false",
        dest="output",
        help="Hide output from commands",
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
        help="Skips build cleanup, leaving temporary files and folders.",
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
