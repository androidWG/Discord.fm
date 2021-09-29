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
It's highly recommended building your own version of PyInstaller if you want to distribute this app toa void false positives in antivirus programs. Please follow [these instructions](https://stackoverflow.com/a/53705283/8286014) to build it form source and install it on your venv.

- Download and install [Qt](https://www.qt.io/download-qt-installer)
- Clone the repo with `git clone https://github.com/AndroidWG/Discord.fm.git`
- Build PyInstaller:
  - Clone the PyInstaller repo with `git clone https://github.com/pyinstaller/pyinstaller.git`
  - Enter the repo with `cd pyinstaller`
  - Checkout the v4.5.1 commit with `git checkout 5a02f55c696f16b98f23a8b487f3daa8f644a8d2`
  - Enter the bootloader folder with `cd bootloader`
  - Build with `python ./waf distclean all`
  - Go back to Discord.fm repo with `cd ../../Discord.fm`
- Run `python -m venv venv` to set up a virtual environment
- Activate the venv with `venv\Scripts\activate.bat` on Windows or `source venv/bin/activate` on macOS/Linux
- Run `python -m pip install -r requirements.txt` to install dependencies
- Run `python ../pyinstaller/setup.py install` to install your build of PyInstaller
- Make a `.env` file on the repo's root folder with 3 keys:
```
lastfm_key = "<Last.fm API key>"
lastfm_secret = "<Last.fm API secret>"

discord_app_id = "<Discord Client ID>"
```
- Done! You can now build binaries for your OS with `python build/build.py` or run the script directly with `python main.py`

## Known Issues
- Album artwork sadly cannot be set directly from the app, only through the Discord Developer Console. This has no workaround. By the way, this is why no music Rich Presence app does this.
