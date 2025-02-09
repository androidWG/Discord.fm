<p align="center">
  <img src="https://i.imgur.com/sBPf84B.png" style="max-height: 128px">
</p>
<p align="center">
  <img src="https://i.imgur.com/EcePBfb.gif" style="max-height: 350px">
</p>

----

<p align="center">
   <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logoColor=white" alt="Windows Platform Badge">
   <img src="https://img.shields.io/badge/MacOS-grey?style=for-the-badge&logoColor=white" alt="macOS Platform Badge">
   <img src="https://img.shields.io/badge/Linux-yellow?style=for-the-badge&logoColor=white" alt="Linux Platform Badge">
</p>

<p align="center">
   <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/downloads/androidWG/Discord.fm/latest/total?label=downloads&style=flat-square">
    <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/androidWG/Discord.fm/test-build.yml?style=flat-square">
   <img src="https://img.shields.io/github/license/AndroidWG/Discord.fm?style=flat-square" alt="License: MIT">
   <img src="https://img.shields.io/badge/using-pypresence-00bb88.svg?style=flat-square&logo=discord&logoWidth=20&logoColor=white" alt="Using pypresence package">
</p>

Multi-platform background service that shows what you're scrobbling on Last.fm to on Discord, with automatic updates,
cover art image, support for Discord Canary and a UI for changing settings.

Based on [Last.fm-Discord-Rich-Presence](https://github.com/Gust4Oliveira/Last.fm-Discord-Rich-Presence)
by [Gust4Oliveira](https://github.com/Gust4Oliveira)

## Setup

The app currently supports Windows (minimum **Windows 10**) and Linux through generic binaries with an installer script.
Flatpak support is incoming and macOS support is planned.

- Download the [latest release](https://github.com/androidWG/Discord.fm/releases/latest)
- Run the installer
- Wait a bit and the app's settings will open. Type in your Last.fm username and close the window.
- Done!

## Setting up dev environment

Discord.fm provides a setup script with some useful functions for devs. A full list of parameters can be viewed by
running the command `python setup.py -h` or simply running the script with no flags or commands.

### Requirements

- Python 3.12 or above
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- C compiler (GCC, MSVC, etc.)
    - [PyInstaller](https://github.com/pyinstaller/pyinstaller) is used to freeze the app for distribution. However,
      using pip to install it will trigger false positives in many antiviruses. This is why we will need to build it
      ourselves, and thus the need for a C compiler. More
      info [here](https://stackoverflow.com/questions/43777106/program-made-with-pyinstaller-now-seen-as-a-trojan-horse-by-avg).
- tkinter
- packaging
    - Simply run `pip install packaging`

#### Platform notes

<details>
<summary>Windows</summary>

- Visual Studio with the C++ development option includes MSVC, if you don't have VS I
  recommend [MSYS2](https://www.msys2.org/) - includes GCC

</details>

<details>
<summary>Linux</summary>

- [PyGObject dependencies](https://pygobject.gnome.org/getting_started.html) - required
  by [pystray](https://pystray.readthedocs.io/en/latest/faq.html#how-do-i-use-pystray-in-a-virtualenv-on-linux), follow
  instructions for "**Installing from PyPI with pip**"
- tkinter might not be included in your installation, check by running `python -m tkinter`. Check install help
  for you distro here: https://stackoverflow.com/a/25905642

</details>

After all requirements are met, clone the repo:

````commandline
git clone https://github.com/androidWG/Discord.fm
cd Discord.fm
````

Then run setup:

```commandline
python setup.py setup
```

The script should set up everything for you. You can set it up yourself manually too:

```commandline
uv sync --dev
```

### Building

Simply use the `setup.py` script again:

````commandline
python setup.py build
````

The script will set up anything if needed, then build the app and subsequently the installer - both only for the current
platform. You can pass the flag `--installer-only` or `--build-only` to skip the other step.
