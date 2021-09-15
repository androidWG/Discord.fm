"""Build Discord.fm

This script runs PyInstaller and by default, the installer build script for the current platform. It should be run
form the root folder with "python build/build.py". It accepts an optional parameter -NI (or --no-installer) to prevent
the script from generating an installer.

`UPX <https://upx.github.io/>`_ can be used by PyInstaller by adding a folder named "upx" inside the project
root containing a UPX release's files.

To build the Windows installer you'll need Inno Setup 6."""
import os
import platform
import shutil
import subprocess
import sys
import installer
from time import sleep
from util.process import stream_process

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import __version
import util


def arg_exists(*args):
    for arg in args:
        if sys.argv.__contains__(arg):
            return True

    return False


current_platform = platform.system()
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

util.replace_instances("build/file_version.txt", main_tags, temp_ver_main_file)
util.replace_instances("build/file_version.txt", main_tags, temp_ver_ui_file)

# Choose right icon
if current_platform == "Darwin":
    main_icon = "resources/icon.icns"
    settings_icon = "resources/settings.icns"
elif current_platform == "Windows":
    main_icon = "resources/icon.ico"
    settings_icon = "resources/settings.ico"

# noinspection PyUnboundLocalVariable
main_args = [
    "main.py",
    f"--icon={main_icon}",
    "--name=discord_fm",
    f"--version-file={temp_ver_main_file}",
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
    f"--icon={settings_icon}",
    "--name=settings_ui",
    f"--version-file={temp_ver_ui_file}",
    f"--add-data=resources/black/.{os.pathsep}resources/black",
    f"--add-data=resources/white/.{os.pathsep}resources/white",
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
    executable_format = ".exe" if platform.system() == "Windows" else ""
    run_command = [f"{os.path.abspath('venv/Scripts/python') + executable_format} -O -m PyInstaller"]

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
    if current_platform == "Windows":
        installer.make_windows_installer(version)
    elif current_platform == "Darwin":
        pass  # installer.make_macos_installer(version)

print(f"Finished building version {version}")
