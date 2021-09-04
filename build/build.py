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
import PyInstaller.__main__
import sys
# import installer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import __version
import util

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
    icon_file = "resources/icon.icns"
elif current_platform == "Windows":
    icon_file = "resources/icon.ico"

main_args = [
    "main.py",
    f"--icon={icon_file}",
    "--name=discord_fm",
    f"--version-file={temp_ver_main_file}",
    f"--add-data=resources/tray_icon.png{os.pathsep}resources",
    "--additional-hooks-dir=hooks",
    "--workpath=pyinstaller_temp",
    "--osx-bundle-identifier=com.androidwg.discordfm",
    "--upx-dir=upx/",
    "-y",
    "--onefile",
    "--noconsole",
]

ui_args = [
    "ui.py",
    "--name=settings_ui",
    f"--version-file={temp_ver_ui_file}",
    "--hidden-import=bottle_websocket",
    f"--add-data=eel/eel/eel.js{os.pathsep}eel",
    f"--add-data=electron{os.pathsep}electron",
    f"--add-data=web{os.pathsep}web",
    f"--add-data=main.js{os.pathsep}electron/resources/app",
    f"--add-data=package.json{os.pathsep}electron/resources/app",
    "--additional-hooks-dir=hooks",
    "--workpath=pyinstaller_temp",
    "--osx-bundle-identifier=com.androidwg.discordfm.ui",
    "--upx-dir=upx/",
    "-y",
    "--noconsole",
    "--onefile",
]

# Run PyInstaller
print("\nRunning PyInstaller for main.py...")
PyInstaller.__main__.run(main_args)

print("\nRunning PyInstaller for ui.py...")
PyInstaller.__main__.run(ui_args)

# Clean temp file after use
os.remove(temp_ver_main_file)
os.remove(temp_ver_ui_file)
try:
    shutil.rmtree("pyinstaller_temp")
except FileNotFoundError:
    pass

# Make platform installer
if not sys.argv.__contains__("--no-installer") and not sys.argv.__contains__("-NI"):
    if current_platform == "Windows":
        pass  # installer.make_windows_installer(version)
    elif current_platform == "Darwin":
        pass  # installer.make_macos_installer(version)

print(f"Finished building version {version}")
