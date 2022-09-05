<p align="center">
  <img src="https://i.imgur.com/sBPf84B.png" height="128">
</p>
<p align="center">
  <img src="https://i.imgur.com/EcePBfb.gif">
</p>

----

<p align="center">
   <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows Platform Badge">
   <img src="https://img.shields.io/badge/MacOS-grey?style=for-the-badge&logo=apple&logoColor=white" alt="macOS Platform Badge">
</p>

<p align="center">
   <img src="https://img.shields.io/lgtm/grade/python/g/AndroidWG/Discord.fm.svg?logo=lgtm&logoWidth=20&style=flat-square" alt="Language grade: Python">
   <img src="https://img.shields.io/github/license/AndroidWG/Discord.fm?style=flat-square" alt="License: MIT">
   <img src="https://img.shields.io/badge/using-pypresence-00bb88.svg?style=flat-square&logo=discord&logoWidth=20&logoColor=white" alt="Using pypresence package">
</p>

Multi-platform background service that shows what you're scrobbling on Last.fm to on Discord, with automatic updates, cover art image and support for Discord Canary.

Forked from [Last.fm-Discord-Rich-Presence](https://github.com/Gust4Oliveira/Last.fm-Discord-Rich-Presence) by [Gust4Oliveira](https://github.com/Gust4Oliveira)

## Setup
### Windows
> **NOTE:** Only 64-bit Windows 10 is officially supported. Windows versions older than Windows 10 are not guaranteed to work, and 64-bit builds (currently all of them) only work on 64-bit systems.
- Download the [latest release](https://github.com/AndroidWG/Discord.fm/releases/latest)
- Run the installer
- Wait a bit and the app's settings will open. Type in your Last.fm username and close the window.
- Done!

Discord.fm will start with Windows automatically, and a tray icon will appear where you can enable or disable the Rich Presence status, open settings or exit the app.

### macOS
macOS support is 85% finished, but no build is available yet. Expect a release in the near future.

### Linux
While some Linux code is written, the app needs a major rewrite to support building for Flatpak (since it is extremely sandboxed). No releases are planned in the near future.

## Building/Setting up dev environment
We need to build PyInstaller ourselves to avoid having the application be falsely flagged by antivirus programs as a virus. If you don't intend to build for distribution, you can skip the 2nd step.

1. Clone the repo with `git clone https://github.com/AndroidWG/Discord.fm.git`
2. Build PyInstaller:
    1. Make sure you have a C compiler like MSVC, GCC or CLang installed
    2. Clone the PyInstaller repo with `git clone --branch master https://github.com/pyinstaller/pyinstaller.git`
    3. Enter the repo with `cd pyinstaller`
    4. Checkout the v5.3 commit with `git checkout fbf7948be85177dd44b41217e9f039e1d176de6b`
    5. Enter the bootloader folder with `cd bootloader`
    6. Build with `python ./waf distclean all`
    7. Go back to main directory by entering `cd ..`
    8. Run `..\Discord.fm\venv\Scripts\python.exe setup.py install` on Windows or `../Discord.fm/venv/Scripts/python setup.py install` on macOS/Linux to install your build of PyInstaller
    9. Go back to Discord.fm repo with `cd ../Discord.fm`
3. Run `python -m venv venv` to set up a virtual environment
4. Activate the venv with `venv\Scripts\activate.bat` on Windows or `source venv/bin/activate` on macOS/Linux
5. Run `python -m pip install -r requirements.txt` to install dependencies
6. Make a `.env` file on the repo's root folder with 3 keys:
```
lastfm_key = "<Last.fm API key>"
lastfm_secret = "<Last.fm API secret>"

discord_app_id = "<Discord Client ID>"
```
7. Done! You can now build binaries for your OS with `python build/build.py` or run the script directly with `python main.py`