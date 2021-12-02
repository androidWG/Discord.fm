# Discord.fm
[![Total alerts](https://img.shields.io/lgtm/alerts/g/AndroidWG/Discord.fm.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/AndroidWG/Discord.fm/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/AndroidWG/Discord.fm.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/AndroidWG/Discord.fm/context:python)

Background service that shows what you're scrobbling on Last.fm to on Discord.

Forked from [Last.fm-Discord-Rich-Presence](https://github.com/Gust4Oliveira/Last.fm-Discord-Rich-Presence) by [Gust4Oliveira](https://github.com/Gust4Oliveira)

![Screenshot of the app showing Rich Presence info on Discord](https://i.imgur.com/t4TCs0T.png)

## Setup
### Windows
- Download the latest [release](https://github.com/AndroidWG/Discord.fm/releases/latest)
- Run the installer
- The Settings interface will open when you're finished. Put your Last.fm Username and close the window.
- Done

Discord.fm will start with Windows automatically.

A tray icon will appear where you can enable or disable the Rich Presence status, open settings or close the app.

**NOTE:** Automatic updates will be available soon.

## Building/Setting up dev environment
We need to build PyInstaller ourselves to avoid having the application be falsely flagged by antivirus programs as a virus. If you don't intend to build for distribution, you can skip the 3rd step.

1. Download and install [Qt](https://www.qt.io/download-qt-installer)
2. Clone the repo with `git clone https://github.com/AndroidWG/Discord.fm.git`
3. Build PyInstaller:
    1. Make sure you have a C compiler like MSVC, GCC or CLang installed
    2. Clone the PyInstaller repo with `git clone --branch master https://github.com/pyinstaller/pyinstaller.git`
    3. Enter the repo with `cd pyinstaller`
    4. Checkout the v4.5.1 commit with `git checkout 5a02f55c696f16b98f23a8b487f3daa8f644a8d2`
    5. Enter the bootloader folder with `cd bootloader`
    6. Build with `python ./waf distclean all`
    7. Go back to Discord.fm repo with `cd ../../Discord.fm`
4. Run `python -m venv venv` to set up a virtual environment
5. Activate the venv with `venv\Scripts\activate.bat` on Windows or `source venv/bin/activate` on macOS/Linux
6. Run `python -m pip install -r requirements.txt` to install dependencies
7. Run `python ../pyinstaller/setup.py install` to install your build of PyInstaller
8. Make a `.env` file on the repo's root folder with 3 keys:
```
lastfm_key = "<Last.fm API key>"
lastfm_secret = "<Last.fm API secret>"

discord_app_id = "<Discord Client ID>"
```
9. Done! You can now build binaries for your OS with `python build/build.py` or run the script directly with `python main.py`

## Known Issues
- Album artwork sadly cannot be set directly from the app, only through the Discord Developer Console. This has no workaround. By the way, this is why no music Rich Presence app does this.
