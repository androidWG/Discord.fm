import argparse
import os
import platform
import shutil
import stat
import subprocess
import sys
from glob import glob
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
    ITALIC = "\033[3m"


PYINSTALLER_VER = "6.11.1"
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


def _check_util(cmd: str) -> bool:
    return shutil.which(cmd) is None


def _check_util_and_exit(cmd: str, message: str = None) -> None:
    if shutil.which(cmd) is None:
        print(f"{Colors.FAIL}{message}{Colors.ENDC}")
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

        self._args = parsed_args

    def _find_tools(self) -> None:
        _print_subheader("Finding Python and adding .venv to path")
        self.python = self._run(PYTHON_FIND_CMD, padding=3)[1]
        if self.current_platform == "Windows":
            venv_path = ".venv/Lib/site-packages"
        else:
            venv_path = glob(".venv/lib/python3*/site-packages")[0]

        if os.path.isdir(venv_path):
            sys.path.append(p.abspath(venv_path))

    def _check_package(self, pkg: str, message: str = None) -> None:
        _print_subheader(f"Checking Python package '{pkg}'")

        result = self._run([self.python, "-c", f'"import {pkg}"'], padding=3)[1]
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
        echo: bool = True,
        passthrough_formatting: bool = False,
        padding: int = 1,
        **kwargs,
    ) -> tuple[bool, str]:
        if isinstance(cmd, str):
            command = cmd.split(" ")
        else:
            command = cmd

        cmd_print = f"{Colors.GREY}{' '*padding}─ {" ".join(command)}{Colors.ENDC}"
        if self.output:
            # Don't print newline to be able to replace this line later
            print(cmd_print, end="\r")

        env = os.environ.copy()
        sep = ";" if self.current_platform == "Windows" else ":"
        env["PYTHONPATH"] = str(p.abspath("src") + sep + p.abspath("tests"))
        if self.no_venv:
            env["UV_PYTHON_PREFERENCE"] = "only-system"

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=env,
            **kwargs,
        )

        lines: list[str] = []
        message: str = ""

        for line in iter(process.stdout):
            stripped_line = line.rstrip()

            lines.append(stripped_line)
            if echo and self.output and stripped_line != "":
                # Print over old line if there's output
                if len(lines) <= 1:
                    print(cmd_print.replace("─", "┬"))

                if message != "":
                    print(message.replace("┴", "│"))

                message = f"{Colors.GREY}{' '*padding}┴ {Colors.ENDC if passthrough_formatting else ''}{stripped_line}{Colors.ENDC if not passthrough_formatting else ''}"
                print(message, end="\r")

        print("")

        result = "\n".join(lines)
        process.stdout.close()
        process.wait()

        return process.returncode, result

    def sync(self):
        _print_header("Syncing")
        result = self._run(
            "uv sync --dev --no-binary-package pyinstaller --no-binary-package pypresence"
        )

        if result[0] != 0:
            print(f"{Colors.FAIL}Failed syncing with uv. Please check log{Colors.ENDC}")
            sys.exit(1)

    def build_pyinstaller(self) -> None:
        _check_util_and_exit(
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
                self._check_package(
                    "psutil",
                    "psutil is required to build Discord.fm. Install using pip install psutil",
                )

                _print_subheader("Checking other packages")
                if self.current_platform == "Darwin" and self._args.package:
                    if not _check_util("appdmg"):
                        if not _check_util("npm"):
                            print(
                                f"{Colors.FAIL}npm not found - it is needed to install appdmg to package macOS builds for distribution. "
                                f"Download at https://nodejs.org/en/download/{Colors.ENDC}"
                            )
                            sys.exit(2)
                        else:
                            print(
                                f"{Colors.FAIL}appdmg not found - it is needed to package macOS builds for distribution. "
                                f"Install using {Colors.GREY}npm install -g appdmg {Colors.FAIL}{Colors.ITALIC}(you might need to use sudo){Colors.ENDC}"
                            )
                            sys.exit(2)
                elif self.current_platform == "Windows" and self._args.installer:
                    _check_util_and_exit(
                        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
                        "Inno Setup is required to build the installer for Windows. Download at https://jrsoftware.org/isdl.php",
                    )

                # TODO: Add message and exit code when build failed
                bt = build.get_build_tool(self.python, self._args.flatpak)
                _print_subheader("Preparing files")
                bt.prepare_files()
                if self._args.executable:
                    _print_subheader("Building executable")
                    bt.build()
                    if self._args.package:
                        _print_subheader("Packaging")
                        bt.package()
                if self._args.installer:
                    _print_subheader("Building installer")
                    bt.make_installer()
                if self._args.cleanup:
                    _print_subheader("Cleaning up")
                    bt.cleanup()

                _print_header("Build completed", Colors.OKGREEN)
            case "run":
                _print_header("Running main.py")
                self._find_tools()
                self._check_package(
                    "tkinter",
                    TKINTER_MESSAGE,
                )

                self._run(
                    [self.python, "main.py"],
                    cwd=p.abspath("src"),
                    passthrough_formatting=True,
                )

                sys.exit(0)
            case "test":
                _print_header("Testing")
                self._find_tools()

                result = self._run(
                    [self.python, "-m", "pytest", "tests/"],
                    passthrough_formatting=True,
                )

                if result[0] != 0:
                    _print_header("Tests failed, check report above", Colors.FAIL)
                    sys.exit(1)
                else:
                    _print_header("Tests passed", Colors.OKGREEN)
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

    sub_test = subparsers.add_parser("test", help="Test Discord.fm using pytest")

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
        "--skip-packaging",
        action="store_false",
        dest="package",
        help="Don't package executables for distribution (only some platforms perform packaging).",
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

    _check_util_and_exit(
        "uv",
        "uv is needed for package management. Instructions at https://docs.astral.sh/uv/getting-started/installation/",
    )

    setup = Setup(args)
    setup.execute_command()
