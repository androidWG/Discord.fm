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
import shutil
import subprocess
import sys
import installer
from time import sleep
from util import arg_exists, replace_instances
from util.process import stream_process

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import __version

version = __version

# Make Version Info files for Windows
version_split = version.split(".")
temp_ver_main_file = "file_version_main.temp"
temp_ver_ui_file = "file_version_ui.temp"
main_tags = [
    ("#VERSION#", version),
    ("#VERSION_TUPLE#", f"{version_split[0]}, {version_split[1]}, {version_split[2]}, 0"),
    ("#DESCRIPTION#", "Discord.fm Service Executable"),
    ("#FILENAME#", "discord_fm")
]
ui_tags = [
    ("#VERSION#", version),
    ("#VERSION_TUPLE#", f"{version_split[0]}, {version_split[1]}, {version_split[2]}, 0"),
    ("#DESCRIPTION#", "Discord.fm Settings UI"),
    ("#FILENAME#", "settings_ui")
]

replace_instances("build/file_version.txt", main_tags, temp_ver_main_file)
replace_instances("build/file_version.txt", main_tags, temp_ver_ui_file)

# noinspection PyUnboundLocalVariable
main_args = [
    "main.py",
    f"--icon=resources/icon.ico",
    "--name=discord_fm",
    f"--version-file={temp_ver_main_file}",
    "--hidden-import=plyer.platforms.win.notification",
    f"--add-data=resources/black/.{os.pathsep}resources/black",
    f"--add-data=resources/white/.{os.pathsep}resources/white",
    f"--add-data=.env{os.pathsep}.",
    "--additional-hooks-dir=hooks",
    "--workpath=pyinstaller_temp",
    "--osx-bundle-identifier=com.androidwg.discordfm",
    "--upx-dir=upx/",
    "-y",
    "--onefile",
    "--noconsole",
]

ui_args = [
    "ui/ui.py",
    f"--icon=resources/settings.ico",
    "--name=settings_ui",
    f"--version-file={temp_ver_ui_file}",
    f"--add-data=resources/black/.{os.pathsep}resources/black",
    f"--add-data=resources/white/.{os.pathsep}resources/white",
    f"--add-data=.env{os.pathsep}.",
    "--additional-hooks-dir=hooks",
    "--workpath=pyinstaller_temp",
    "--osx-bundle-identifier=com.androidwg.discordfm.ui",
    "--noupx",
    "-y",
    "--windowed",
    "--onefile",
]

# Run PyInstaller
if not arg_exists("--no-build", "-NB"):
    run_command = [f"{os.path.abspath('venv/Scripts/python.exe')} -O -m PyInstaller"]

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
os.remove(temp_ver_main_file)
os.remove(temp_ver_ui_file)
try:
    shutil.rmtree("pyinstaller_temp")
except FileNotFoundError:
    pass

# Make platform installer
if not arg_exists("--no-installer", "-NI"):
    installer.make_windows_installer(version)

print(f"Finished building version {version}")
