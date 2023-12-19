<p align="center">
  <img src="https://i.imgur.com/sBPf84B.png" style="max-height: 128px">
</p>
<p align="center">
  <img src="https://i.imgur.com/EcePBfb.gif" style="max-height: 350px">
</p>

----

<p align="center">
   <img src="https://img.shields.io/badge/Windows-blue?style=for-the-badge&logo=windows&logoColor=white&labelColor=black" alt="Windows Platform Badge">
   <img src="https://img.shields.io/badge/Linux-gold?style=for-the-badge&logo=linux&logoColor=white&labelColor=black" alt="Linux Platform Badge">
</p>

<p align="center">
   <img alt="GitHub release downloads (latest by date)" src="https://img.shields.io/github/downloads/androidWG/Discord.fm/latest/total?label=downloads&style=flat-square&labelColor=black">
    <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/androidWG/Discord.fm/test-build.yml?style=flat-square&labelColor=black&label=build %26 tests">
   <img src="https://img.shields.io/github/license/AndroidWG/Discord.fm?style=flat-square&labelColor=black" alt="License: MIT">
   <img src="https://img.shields.io/badge/using-pypresence-00bb88.svg?style=flat-square&logo=discord&logoWidth=20&logoColor=white&labelColor=black" alt="Using pypresence package">
</p>

Multi-platform background service that shows what you're scrobbling on Last.fm to on Discord, with automatic updates,
cover art image, support for Discord Canary and a UI for changing settings.

Originally forked from [Last.fm-Discord-Rich-Presence](https://github.com/Gust4Oliveira/Last.fm-Discord-Rich-Presence)
by [Gust4Oliveira](https://github.com/Gust4Oliveira)

## Setup
The app currently supports Windows (minimum **Windows 10**) and Linux through generic binaries with an installer script. Flatpak support is incoming and macOS support is planned.

- Download the [latest release](https://github.com/AndroidWG/Discord.fm/releases/latest)
- Run the installer
- Wait a bit and the app's settings will open. Type in your Last.fm username and close the window.
- Done!

## Setting up dev environment

Discord.fm provides a setup script with some useful functions for devs. A full list of parameters can be viewed by running the command `python setup.py -h` or simply running the script with no flags or commands.

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
