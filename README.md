# Discord.fm
![Platforms: Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Platforms: macOS](https://img.shields.io/badge/macos-000000?style=for-the-badge&logo=apple&logoColor=white)

[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/AndroidWG/Discord.fm.svg?logo=lgtm&logoWidth=20&style=flat-square)](https://lgtm.com/projects/g/AndroidWG/Discord.fm/context:python)
![GitHub](https://img.shields.io/github/license/AndroidWG/Discord.fm?style=flat-square)
[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=flat-square&logo=discord&logoWidth=20&logoColor=white)](https://github.com/qwertyquerty/pypresence)

Multi-platform background service that shows what you're scrobbling on Last.fm to on Discord, with automatic updates and support for Discord Canary.

Forked from [Last.fm-Discord-Rich-Presence](https://github.com/Gust4Oliveira/Last.fm-Discord-Rich-Presence) by [Gust4Oliveira](https://github.com/Gust4Oliveira)

![Screenshot of the app showing Rich Presence info on Discord](https://i.imgur.com/t4TCs0T.png)

## Setup
### Windows
- Download the latest [release](https://github.com/AndroidWG/Discord.fm/releases/latest)
- Run the installer
- Wait a bit and the app's settings will open. Type in your Last.fm username and close the window.
- Done!

Discord.fm will start with Windows automatically, and a tray icon will appear where you can enable or disable the Rich Presence status, open settings or exit the app.

### macOS
Coming Soon™. Right now the macOS version works almost fully, and only some big important issues need to be worked out.

## Building/Setting up dev environment
We need to build PyInstaller ourselves to avoid having the application be falsely flagged by antivirus programs as a virus. If you don't intend to build for distribution, you can skip the 3rd step.

1. Clone the repo with `git clone https://github.com/AndroidWG/Discord.fm.git`
2. Build PyInstaller:
    1. Make sure you have a C compiler like MSVC, GCC or CLang installed
    2. Clone the PyInstaller repo with `git clone --branch master https://github.com/pyinstaller/pyinstaller.git`
    3. Enter the repo with `cd pyinstaller`
    4. Checkout the v4.5.1 commit with `git checkout 5a02f55c696f16b98f23a8b487f3daa8f644a8d2`
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

## Known Issues
- Album artwork sadly cannot be set directly from the app, only through the Discord Developer Console. This has no workaround. By the way, this is why no music Rich Presence app does this.
