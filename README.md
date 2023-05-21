<p align="center">
  <img src="https://i.imgur.com/sBPf84B.png" style="max-height: 128px">
</p>
<p align="center">
  <img src="https://i.imgur.com/EcePBfb.gif" style="max-height: 350px">
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

Multi-platform background service that shows what you're scrobbling on Last.fm to on Discord, with automatic updates,
cover art image and support for Discord Canary.

Forked from [Last.fm-Discord-Rich-Presence](https://github.com/Gust4Oliveira/Last.fm-Discord-Rich-Presence)
by [Gust4Oliveira](https://github.com/Gust4Oliveira)

## Setup

### Windows

> **NOTE:** Only 64-bit Windows is supported.

- Download the [latest release](https://github.com/AndroidWG/Discord.fm/releases/latest)
- Run the installer
- Wait a bit and the app's settings will open. Type in your Last.fm username and close the window.
- Done!

Discord.fm will start with Windows automatically, and a tray icon will appear where you can enable or disable the Rich
Presence status, open settings or exit the app.

### macOS

macOS support is 85% finished, but no build is available yet. Expect a release in the near future.

### Linux

While some Linux code is written, the app needs a major rewrite to support building for Flatpak (since it is extremely
sandboxed). No releases are planned in the near future.

## Setting up dev environment

### Requirements

- Python 3.11 or above
- [packaging](https://pypi.org/project/packaging/)

#### On Windows

- A C compiler, such as MSVC or GCC (we recommend [MSYS2](https://www.msys2.org/), includes GCC)
    - [PyInstaller](https://github.com/pyinstaller/pyinstaller) is used to freeze the app for distribution. However,
      using pip to install it will trigger false positives in many antiviruses. This is why we will need to build it
      ourselves, and thus the need for a C compiler.
        - More
          info [here](https://stackoverflow.com/questions/43777106/program-made-with-pyinstaller-now-seen-as-a-trojan-horse-by-avg)

After all requirements are met, just clone the repo and run the setup:

````commandline
git clone https://github.com/androidWG/Discord.fm
cd Discord.fm
python setup.py setup
````

The script should set up everything for you. Then, you can run the app with

```commandline
python setup.py run
```

### Building

Simply use the `setup.py` script again:

````commandline
python setup.py build
````

The script will set up anything if needed, then build the app and subsequently the installer - both only for the current
platform. You can pass the flag `--installer-only` or `--build-only` to skip the other step.

A full list of parameters can be viewed by passing the flag `-h` or simply running the script with no flags or commands.
