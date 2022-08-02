"""Build Discord.fm

This script runs PyInstaller and by default, the installer build script for the current platform. It should be run
form the root folder with "python build/build.py".

`UPX <https://upx.github.io/>`_ can be used by PyInstaller by adding a folder named "upx" inside the project
root containing a UPX release's files.

To build the Windows installer you'll need Inno Setup 6.

Options:
    -NI, --no-installer    Builds Discord.fm without creating a Windows installer
    -NB  --no-build        Makes only an installer with an existing build inside dist folder
    --main-only            Builds only the main script and ignores UI script. Installer will try to find both
                           executables anyway
    --ui-only              Builds only the UI script and ignores main script. Installer will try to find both
                           executables anyway"""
import os
import platform
import shutil
import subprocess
import sys
from platform import system
from time import sleep

import installer
from util import arg_exists, replace_instances
from process import stream_process

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from globals import get_debug, get_version

version = get_version()
if get_debug():
    print("\033[93m\033[1mWARNING: Building debug version\033[0m")

# Make Version Info files for Windows
version_split = version.split(".")
icon_main = "resources/icon." + "ico" if system() == "Windows" else "png"
icon_settings = "resources/settings." + "ico" if system() == "Windows" else "png"

temp_ver_main_file = "file_version_main.temp"
temp_ver_ui_file = "file_version_ui.temp"
temp_spec_file = "build.spec"

main_tags = [
    ("#VERSION#", version),
    (
        "#VERSION_TUPLE#",
        f"{version_split[0]}, {version_split[1]}, {version_split[2]}, 0",
    ),
    ("#DESCRIPTION#", "Discord.fm Service Executable"),
    ("#FILENAME#", "discord_fm"),
]
ui_tags = [
    ("#VERSION#", version),
    (
        "#VERSION_TUPLE#",
        f"{version_split[0]}, {version_split[1]}, {version_split[2]}, 0",
    ),
    ("#DESCRIPTION#", "Discord.fm Settings UI"),
    ("#FILENAME#", "settings_ui"),
]
spec_tags = [
    ("#VER_MAIN#", temp_ver_main_file),
    ("#VER_UI#", temp_ver_ui_file),
    ("#ICON_MAIN#", icon_main),
    ("#ICON_UI#", icon_settings),
]

replace_instances("build/file_version.txt", main_tags, temp_ver_ui_file)
replace_instances("build/file_version.txt", ui_tags, temp_ver_main_file)
replace_instances("build/main.spec", spec_tags, temp_spec_file)

# noinspection PyUnboundLocalVariable
main_args = [
    temp_spec_file,
    "--workpath=pyinstaller_temp",
    "--upx-dir=upx/",
    "-y",
]

current_platform = platform.system()
# Run PyInstaller
if not arg_exists("--no-build", "-NB"):
    if current_platform == "Windows":
        venv_path = os.path.abspath("venv/Scripts/python.exe")
    elif current_platform == "Linux":
        venv_path = os.path.abspath("venv/bin/python")
    else:
        raise NotImplementedError("Please use the build_mac.py script")

    run_command = [f"{venv_path} -O -m PyInstaller"]

    print("\nRunning PyInstaller...")
    process = subprocess.Popen(
        " ".join(run_command + main_args),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    while stream_process(process):
        sleep(0.2)

# Clean temp file after use
os.remove(temp_ver_main_file)
os.remove(temp_ver_ui_file)
os.remove(temp_spec_file)
try:
    shutil.rmtree("pyinstaller_temp")
except FileNotFoundError:
    pass

# Make platform installer
if not arg_exists("--no-installer", "-NI"):
    if current_platform == "Windows":
        installer.make_windows_installer(version)
    elif current_platform == "Linux":
        pass
    else:
        raise NotImplementedError

print(f"Finished building version {version}")
