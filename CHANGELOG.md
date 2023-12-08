
# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
 
## [Unreleased] - yyyy-mm-dd
 
### Added

### Changed
 
### Fixed

## [0.10.0] - 2023-12-07
 
### Added
- The first entry on the system tray submenu (accessed by right-clicking) is now a status indicator. Previously, it only showed up if the app was being updated and if Discord wasn't open, now it indicates every status of the app except when Discord is open **and** a song is being scrobbled. 

### Changed
- Checking for Discord and current scrobbling is now always done in deamon threads. This means the programs always exits immediately.
 
### Fixed
- Fixed a bug that would cause a Discord connection error to be ignored and cause it to fail until the next connection attempt
- Fixed more exceptions while closing app

## [0.9.0] - 2023-12-03
## Changes

- Added a Last.fm icon to the cover image shown on Discord
- Added a button that opens the Last.fm page for the current song on Discord

## Bug fixes

- If Discord is closed, the app will now wait properly and republish the last rich presence status if the song being scrobbled is still the same
- The app now handles Last.fm internal errors better
- Fixed many issues with the setup script (CI is now actually working!)

## [0.8.2] - 2023-12-02
## Changes

- Added more tests
- Updated packages
- Code cleanup

## Bug fixes

- Fixed a bug where when exiting the app after having closed Discord, the app would freeze and stay open
- Fixed a bug where the app would attempt to connect to Discord RP even when Discord was closed or unavailable for connection

## [0.8.1] - 2022-12-30
## Bug fixes

- Fixed errors when logging Unicode characters
- Discord would not show rich presence after a few hours since Discord.fm connected. Now the app connects to Discord only when a song is played and disconnects when nothing is playing.

## [0.8.0] - 2022-10-13
## Changes

- Debug is now an option in the settings file (hidden in the UI) instead of a build option fixed in code
- Added "Start with system" option in settings
- Settings UI is now included in the main executable
    - Side effect: "Start/Stop Service" button is removed
- Many, many internal changes
    - Added Black formatter
    - Removed `.env`
    - Moved global variables to the main class `AppManager`
    - Added GitHub Actions setup to build for other systems automatically
    - Many misc. refactorings
- Completely remade the build script into the `BuildTool` class and `setup.py` script
- Many changes for macOS and Linux building and running

## Bug fixes

- Fixed `FileNotFound` exception
    - Serious apologies for this... this version kept being delayed but I should have just made a minor version 🙇🏻‍♀️
- Fixed many outdated tests
- Uninstaller on Windows now removes settings file

## [0.7.0] - 2022-07-31
### Changes:

- Moved settings UI to Tk platform, substituting Qt
   - This change should be (mostly) invisible to the end-user, except for a slight different looking UI and massively reduced size - from 58 MB to 12 MB
   - The app is now compiled to multiple files in the installation folder instead of two executables containing all dependencies
-  Improved internal methods

### Bug fixes
- Fixed exceptions with the `process` module

## [0.6.2] - 2022-07-01
### Changes:

- Cover art will now be shown in Discord. Last.fm is a little spotty so some lesser known tracks will have no art available.

### Bug fixes:
- Fixed crashes related to attempting to connect to Discord while it is not ready
- Fixed obscure crashes which I don't even remember what caused them 💀

## [0.6.1] - 2022-04-28
### Changes

 - Fixed a few less common bugs
 - Improved code cleanliness
 - App closes when it isn't frozen (built) if username is invalid
 - Improved colored logo

## [0.6.0] - 2022-02-16
### Changes

- Many internal changes:
  - Moved some code to a general "manager" class
  - Organized some code
  - Improved logging with more debug and info messages, removed third-party packages' logs, and much prettier/clearer console output
  - Reduced misc. update cooldown to 15 seconds (was 30 seconds before)
  - Added more unit tests
- Changed default `max_logs` value to 5
- Logs above 512 KB will be split into multiple files, with a limit of 2 extra files (overall a 1.5 MB limit on individual log files)
- Debug builds will now produce logs files with the prefix `debug_`
- Tray icon options will be hidden, and the current status will be shown instead during startup or an update. Only the "Exit" button will be available.
- Limited installer to 64-bit systems since all builds are 64-bits only
- Made sure installer removes all files on uninstall
- Uninstaller now forcefully closes Discord.fm before uninstalling to prevent files being left in the system

#### Settings UI

 - Added debouncing to the username field
 - App will now detect when the username setting was changed and reload - A.K.A. changing your username does not require you to restart the app
   - This was previously implemented but pretty broken. Now it works much better
 - Version label on the bottom right will show "(debug)" if it is a debug build

### Bug fixes
 - #18 App would crash when Discord was running but not logged in
 - Invalid usernames set without using the settings UI would make the service crash. When this happens, the app instead opens settings and waits for a valid username.
 - Closing the app while a request was being made could freeze the service until the request completed and the timeouts finished before actually closing
 - Uncaught exceptions on the settings UI would inadvertently start the service and raise other exceptions while doing it

## [0.5.0] - 2022-02-10
This release brings mostly small end-user changes but many, many, many refactors and documentation inside the code, plus testing and better error handling.

### Changes
- Many organizational code changes
- Added code tests (no impact on final users, but certainly helps me!)
- Installer only installs to 64bit Windows versions
#### Settings UI
- Start/Stop Service button is now greyed out while the service is starting or stopping
- Added username checking
- Added status bar with current app version
- Added "update to pre-release versions" setting

### Bug fixes
- Improved error handling in general
- Fixed bugs with a slow or inconsistent connection making requests not time out or wait correctly
- Fixed crashing when LastFM username was empty
- #15 Fixed "Could not find Discord installed and running on this machine" exception
- #16 Fixed a bug where one character song names would throw an exception

## [0.4.0] - 2021-12-06
Hey everyone! Big changes in this version - we're getting closer to 1.0! Here's the list of them all:

### Changes

- The app will open the settings app automatically in the first run or if the username setting is missing
- Settings and logs on Windows are now stored in the Roaming AppData folder
- Settings UI will now alert the user if the inputted Last.fm username is incorrect
- Network problems are now handled properly - the app will wait for internet connection instead of bugging or crashing
- Automatic updates are FINALLY working properly!
- Due to a Windows thing, trying to connect to Discord when another user is logged on and has Discord open will cause an error and make the other user's Discord be updated instead. The app now shows a notification alerting the user of this and waits until the other user closes Discord or disconnects

### Bug fixes
- #6 PermissionError when connecting to Discord while another user is logged in on Windows
- Discord closing while app is open crashes the app
- Re-enabling "Enable Rich Presence" on tray icon doesn't do anything
- Exceptions when exiting the app

## [0.3.0] - 2021-09-29
Some nice changes on this version, getting a little closer to release! Here's all of them:

- Removed tray icon setting. Completely invisible background processes isn't that good of an idea for something like this.
- Opening a second instance of the `discord_fm` executable will open the settings interface instead
  - You can also use the CLI option `-o` to open settings from the main executable
- Discord.fm won't throw a fit when Discord isn't open. It will quietly wait until you open it to start doing its thing
- `process` and `install` utilities were much improved
  - It now looks for the executable in the working folder and app install path
  - Process checking now always ignores itself and the parent process
- `setup_logging` now clears all handler from Logging
- Changed Cooldown from a SpinBox to a Slider in settings UI
- Settings UI now alerts if it's not frozen
- Added `is_frozen()` and `arg_exists()` util methods
- Improved exception logging in some places
- Official Discord Canary support
- Removed now unused `RepeatedTimer` class
- Added run configurations for PyCharm
- macOS build support added. This version will not include a Mac release though, that'll be for 0.4.0
  - Build script was split between Windows and macOS since there was significant changes in how the macOS version is built
## [0.2.0] - 2021-09-15
  
Alright boys and girls, it's time for version 0.2.0. Plenty of changes to be had here! Including a full installer, so no setup is required. Just run and have fun.

### General
- Changed from Eel/Electron UI to Qt 6 (down from ~108 MB to 48 MB)
- Using .env file for keys secrets
- App now exits gracefully instead of crashing and burning horribly
- Fixed exception if the app ran while Discord was closed
- Slightly modified icon
  - Using new Discord logo color
  - Using a slightly different icon for the Settings UI
- Tray icon now runs on a separate thread
- Last.fm polling now uses `scheduler` module (much more reliable)
- Added installer for Windows and theoretical installer build support for macOS (not tested)

### UI/UX
- Tray and app icons now have dark and light versions, depending on Windows and macOS settings
  - Updated every 30 seconds, independent of Last.fm polling
- Tray icon has an "Open Settings" button
- "Enable Rich Presence" option now works properly
- UI starts and stops main process correctly (button always says "Start Service" though)

### Settings Module
- Better error handling when reading and writing settings file
- Added docstrings
- Changed back to a class
- Improved logging
- Added macOS support, including using system Logs folder instead of Application Support

### Logging
- Fixed exception when writing file if log message contained Unicode characters
- `log_setup` now handles `PermissionError`s when deleting old logs

+Some other changes i probably forgor 💀
 
## [0.1.0] - 2021-09-04
 
UI currently doesn't work fully, only Username, Cooldown and "Open Logs Folder" options are fully working. The "Running" or "Stopped" status on the button is random and doesn't reflect if the app is running.

Also, it's Windows only for now.