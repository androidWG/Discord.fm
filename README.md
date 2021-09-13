# Discord.fm
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/AndroidWG/Discord.fm.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/AndroidWG/Discord.fm/context:python)

Background service that shows what you're scrobbling on Last.fm to on Discord.

Forked from [Last.fm-Discord-Rich-Presence](https://github.com/Gust4Oliveira/Last.fm-Discord-Rich-Presence) by [Gust4Oliveira](https://github.com/Gust4Oliveira)

![Screenshot of the app showing Rich Presence info on Discord](https://i.imgur.com/t4TCs0T.png)

## Setup
> Virus Warning Disclaimer
>
>PyInstaller applications tend to get detected as a virus by Windows Defender, AVG, and other antivirus software. Of course this program doesn't do anything malicious at all, and I applied a work-around that should prevent it from happening, but it's not guaranteed.

- Download the latest [release](https://github.com/AndroidWG/Discord.fm/releases/latest)
- Run the installer
- Settings will open when you're finished. Put your Last.fm Username and close the window
- Done

A tray icon will appear where you can enable or disable the Rich Presence status, open settings or close the app.

**NOTE:** Automatic updates will be available soon.

## Building/Setting up dev environment
- Download and install [Qt](https://www.qt.io/download-qt-installer)
- Clone the repo with `git clone https://github.com/AndroidWG/Discord.fm.git` then `cd Discord.fm`
- Run `python -m venv venv` to set up a virtual environment
- Activate venv with `venv\Scripts\activate.bat` on Windows or `source venv/bin/activate` on macOS/Linux
- Run `python -m pip install -r requirements.txt` to install dependencies
- Make a `.env` file on the repo's root folder with 3 keys:
```
lastfm_key = "<Last.fm API key>"
lastfm_secret = "<Last.fm API secret>"

discord_app_id = "<Discord Client ID>"
```
- Done! You can now build binaries for your OS with `python build/build.py` or run the script directly with `python main.py`

## Known Issues
- Only Windows is supported (for now).
- Album artwork sadly cannot be set directly from the app, only through the Discord Developer Console. This has no workaround. By the way, this is why no music Rich Presence app does this.
