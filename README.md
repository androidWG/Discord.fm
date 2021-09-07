# Discord.fm
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/AndroidWG/Discord.fm.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/AndroidWG/Discord.fm/context:python)
[![Language grade: JavaScript](https://img.shields.io/lgtm/grade/javascript/g/AndroidWG/Discord.fm.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/AndroidWG/Discord.fm/context:javascript)

Background service that shows what you're scrobbling on Last.fm to on Discord.

Forked from [Last.fm-Discord-Rich-Presence](https://github.com/Gust4Oliveira/Last.fm-Discord-Rich-Presence) by [Gust4Oliveira](https://github.com/Gust4Oliveira)

![Screenshot of the app showing Rich Presence info on Discord](https://i.imgur.com/t4TCs0T.png)

## Setup


> Virus Warning Disclaimer
>
>PyInstaller applications tend to get detected as a virus by Windows Defender, AVG, and other antivirus software. Of course this program doesn't do anything malicious at all, and I applied a work-around that should prevent it from happening, but it's not guaranteed.

- Download the latest [release](https://github.com/AndroidWG/Discord.fm/releases/latest).
- Unzip the file and place both executables somewhere nice and warm
- Open `settings_ui.exe` to input your Last.fm username
- Close it
- Run `discord.fm.exe`

A tray icon will appear where you can enable or disable the Rich Presence status or close the app. Later an installer will be provided in later releases to set up things automatically.

**NOTE:** Tray Icon, Auto Update and the Service Running button currently don't work in the UI

## Building/Setting up dev environment
Eel has a small problem which causes an exception when running it inside PyInstaller with the `--no-console` param, so we'll need to modify a single line in Eel's source code.

- Clone the repo with `git clone https://github.com/AndroidWG/Discord.fm.git`
- Download the [Electron v13.3.0](https://github.com/electron/electron/releases/tag/v13.3.0) files for your OS and place all files from the zip inside a new folder called `electron`
- Run `python -m venv venv` to set up a virtual environment
- Run `venv/Scripts/python -m pip install -r requirements.txt` to install dependencies
- Download the [Eel v0.4.0](https://github.com/ChrisKnott/Eel/releases/tag/v0.14.0) source code and unpack the contents in `Eel-0.4.0` inside a new folder called`eel`
- Open `eel/eel/electron.py` with your preferred editor and change lines 11 and 12 as such:
```py
def run(path, options, start_urls):
    cmd = [path] + options['cmdline_args']
    cmd += ['.', ';'.join(start_urls)]
>   #sps.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, stdin=sps.PIPE)
>   sps.Popen(cmd, stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
```
- Run `venv/Scripts/python eel/setup.py develop` then `venv/Scripts/python -m pip install -e eel`

## Known Issues
- Only Windows is supported (for now).
- Electron is a 137 MB executable and practically a very small part of the app, yet uses 80% of its file size. Still need to test what can be done to reduce file size.
- Album artwork sadly cannot be set directly from the app, only through the Discord Developer Console. This has no workaround. By the way, this is why no music Rich Presence app does this.
