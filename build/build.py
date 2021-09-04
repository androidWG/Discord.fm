"""Build Discord.fm

This script runs PyInstaller and by default, the installer build script for the current platform. It should be run
form the root folder with "python build/build.py". It accepts an optional parameter -NI (or --no-installer) to prevent
the script from generating an installer.

`UPX <https://upx.github.io/>`_ can be used by PyInstaller by adding a folder named "upx" inside the project
root containing a UPX release's files.

To build the Windows installer you'll need Inno Setup 6 installed."""
import os
import platform
import shutil
import PyInstaller.__main__
import sys
# import installer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main
import util

current_platform = platform.system()

version = main.__version
version_split = version.split(".")

# Make Version Info file for Windows
temp_ver_info_file = "file_version_info.temp"
tags = [
    ("#VERSION#", version),
    ("#VERSION_TUPLE#", f"{version_split[0]}, {version_split[1]}, {version_split[2]}, 0")
]
util.replace_instances("build/file_version.txt", tags, temp_ver_info_file)

# Choose right icon
if current_platform == "Darwin":
    icon_file = "resources/icon.icns"
elif current_platform == "Windows":
    icon_file = "resources/icon.ico"

main_args = [
    "main.py",
    "--icon=%s" % icon_file,
    "--name=discord_fm",
    "--version-file=%s" % temp_ver_info_file,
    f"--add-data=resources/tray_icon.png{os.pathsep}resources",
    "--additional-hooks-dir=hooks",
    "--workpath=pyinstaller_temp",
    "--osx-bundle-identifier=com.androidwg.discordfm",
    "-y",
    "--noconsole",
]

ui_args = [
    "ui.py",
    "--name=settings_ui",
    "--version-file=%s" % temp_ver_info_file,
    "--hidden-import=bottle_websocket",
    f"--add-data=eel/eel/eel.js{os.pathsep}eel",
    f"--add-data=electron{os.pathsep}electron",
    f"--add-data=web{os.pathsep}web",
    f"--add-data=main.js{os.pathsep}electron/resources/app",
    f"--add-data=package.json{os.pathsep}electron/resources/app",
    "--additional-hooks-dir=hooks",
    "--workpath=pyinstaller_temp",
    "--osx-bundle-identifier=com.androidwg.discordfm.ui",
    "-y",
    "--noconsole",
    "--onefile",
]

# If UPX folder is found inside root, make sure that PyInstaller uses it
if os.path.exists("upx/"):
    ui_args.append("--upx-dir=%s" % "upx/")

# Run PyInstaller
print("Running PyInstaller for main.py...")
PyInstaller.__main__.run(main_args)

print("Running PyInstaller for ui.py...")
PyInstaller.__main__.run(ui_args)

# Clean temp file after use
os.remove(temp_ver_info_file)
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
