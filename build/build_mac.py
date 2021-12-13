"""Build Discord.fm

This script runs PyInstaller and by default, the installer build script for the current platform. It should be run
form the root folder with "python build/build.py". It accepts an optional parameter -NI (or --no-installer) to prevent
the script from generating an installer."""
import os
import shutil
import subprocess
import sys
from time import sleep
from util.process import stream_process

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import get_version


def arg_exists(*args):
    for arg in args:
        if sys.argv.__contains__(arg):
            return True

    return False


version = get_version()

# noinspection PyUnboundLocalVariable
main_args = [
    "build/discord_fm_mac.spec",
    "--distpath=./dist",
    "--workpath=pyinstaller_temp",
    "-y"
]

ui_args = [
    "build/settings_ui_mac.spec",
    "--distpath=./dist",
    "--workpath=pyinstaller_temp",
    "-y"
]

# Run PyInstaller
if not arg_exists("--no-build", "-NB"):
    run_command = [f"{os.path.abspath('venv/bin/python')} -O -m PyInstaller"]

    if not arg_exists("--ui-only"):
        print("\nRunning PyInstaller for main.py...")
        process = subprocess.Popen(" ".join(run_command + main_args), shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        while stream_process(process):
            sleep(0.1)

    if not arg_exists("--main-only"):
        print("\nRunning PyInstaller for ui.py...")
        process = subprocess.Popen(" ".join(run_command + ui_args), shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        while stream_process(process):
            sleep(0.1)

# Clean temp file after use
try:
    shutil.rmtree("pyinstaller_temp")
except FileNotFoundError:
    pass

# Make platform installer
# installer.make_macos_installer(version)

print(f"Finished building version {version} for macOS")
