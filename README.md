<p align="center">
  <img src="https://i.imgur.com/sBPf84B.png" style="max-height: 128px">
</p>
<p align="center">
  <img src="https://i.imgur.com/EcePBfb.gif" style="max-height: 350px">
</p>

---

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

Multi-platform background service that shows what you're scrobbling on Last.fm to on Discord, with automatic updates, cover art image, support for Discord Canary and a UI for changing settings.

Based on [Last.fm-Discord-Rich-Presence](https://github.com/Gust4Oliveira/Last.fm-Discord-Rich-Presence) by [Gust4Oliveira](https://github.com/Gust4Oliveira)

## Install

### Platform support overview

|                    | Windows | macOS | Linux (generic) | Linux (Flatpak) |
| ------------------ | :-----: | :---: | :-------------: | :-------------: |
| Basic Function     |   ✅    |  🟥   |       ✅        |       🟥        |
| Building/Packaging |   ✅    |  ✅   |       ✅        |       🟧        |
| Start with System  |   ✅    |  🟧   |       🟧        |       🟥        |
| Updates            |   ✅    |  🟥   |       🟧        |       ➖        |

✅ _Fully working_ | 🟧 _Needs testing/WIP_ | 🟥 _Not working_ | ➖ _Not applicable_

### Instructions

-   Download the [latest release](https://github.com/androidWG/Discord.fm/releases/latest)
-   Run the installer
    -   `*setup.exe` on Windows, `install.sh` on Linux (generic)
-   Wait a bit and the app's settings will open. Type in your Last.fm username and close the window.
-   Done!

## Setting up dev environment or running as a Python script

Discord.fm provides a setup script with some useful functions for devs. A full list of parameters can be viewed by running the command
`python setup.py -h` or simply running the script with no flags or commands.

The app can also be run unfrozen by running `python setup.py run`. Check requirements and full instructions below:

### Requirements

-   Python 3.12 or above
-   [uv](https://docs.astral.sh/uv/getting-started/installation/)
-   tkinter
-   `packaging` Python package

#### Build requirements

-   C compiler (GCC, MSVC, etc.)
    -   [PyInstaller](https://github.com/pyinstaller/pyinstaller) is used to freeze the app for distribution. However, using pip to install it will trigger false positives in many antiviruses. This is why we will need to build it ourselves, and thus the need for a C compiler. More info [here](https://stackoverflow.com/questions/43777106/program-made-with-pyinstaller-now-seen-as-a-trojan-horse-by-avg).
-   `psutil` Python package
-   `appdmg` Node package (**macOS only**)
-   [Inno Setup](https://jrsoftware.org/isinfo.php) (**Windows only** for installer building)

> [!WARNING] > On **Linux** PyGObject dependencies are required by [pystray](https://pystray.readthedocs.io/en/latest/faq.html#how-do-i-use-pystray-in-a-virtualenv-on-linux) for running or building - follow instructions for
> "**Installing from PyPI with pip**" for your distro on this link: https://pygobject.gnome.org/getting_started.html

#### Platform notes

<details>
<summary>Windows</summary>

-   Visual Studio with the C++ development option includes MSVC, if you don't have VS I recommend [MSYS2](https://www.msys2.org/) - includes GCC

</details>

<details>
<summary>Linux</summary>

-   tkinter might not be included in your installation, check by running
    `python -m tkinter`. Check install help for you distro here: https://stackoverflow.com/a/25905642

</details>

<details>
<summary>macOS</summary>

-   [appdmg](https://github.com/LinusU/node-appdmg) is needed to create a distribution-ready file (.dmg) on macOS. You'll need [node](https://nodejs.org/en/download/) to run it, once you have it it can be installed with `npm install -g appdmg`
</details>

---

After all requirements are met, clone the repo:

```commandline
git clone https://github.com/androidWG/Discord.fm
cd Discord.fm
```

The setup script will set everything up when you before running any of its commands. You can set it up yourself manually too - the script checks for dependencies and other things, but ultimately setup is a single call for `uv sync` with arguments. Copy the command under the `sync` method in the `setup.py` file and run to install dependencies.

### Running

```commandline
python setup.py run
```

### Building

```commandline
python setup.py build
```

The script will set up anything if needed, then build the app and subsequently the installer (only on Windows) - both only for the current platform. You can pass the flag
`--installer-only` or `--build-only` to skip the other step.
