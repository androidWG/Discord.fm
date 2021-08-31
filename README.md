# Discord.fm
Background service that shows what you're listening to on Discord from a Last.fm account.

![Screenshot of the app showing Rich Presence info on Discord.](https://i.imgur.com/t4TCs0T.png)

## Setup

### Windows

> Virus Warning Disclaimer
>
>PyInstaller applications tend to get detected as a virus by Windows Defender, AVG, and other antivirus software. Of course this program doesn't do anything malicious at all, and I applied a work-around that should prevent it from happening, but it's not guaranteed.

- Download the latest [release](https://github.com/AndroidWG/Last.fm-Discord-RPC/releases/latest).
- Extract the zip file
- Run `python -m pip install -r requirements.txt`
- Run main.py
- Close the app from the tray
- Open `%localappdata\LastFMDiscordRPC%` and edit the `settings.ini` file with your Last.fm username on the "username" field
- Run main.py again

Later you'll be able to use a GUI and installer to make the thing run by itself.

## Dependencies
- pypresence
- pylast
- pystray

## Known Issues
- General crashes and instability
- Only Windows is supported
- API spam/busy waiting
- Album artwork sadly cannot be set directly from the app, only through the Discord Developer Console. This has no workaround. By the way, this is why no music Rich Presence app does this.
