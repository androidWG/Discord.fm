import atexit
import logging
import os
import sys
import time
import pystray
import last_fm
import discord_rich_presence as discord_rp
from PIL import Image
from platform import system
from sched import scheduler
from threading import Thread
from plyer import notification
from settings import local_settings
from pypresence import InvalidPipe, InvalidID
from util import open_settings, process, is_frozen, resource_path, check_dark_mode, log_setup, updates


# From https://stackoverflow.com/a/16993115/8286014
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt) or issubclass(exc_type, SystemExit):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

user = last_fm.LastFMUser(local_settings.get("username"))
tray_icon = None
rpc_state = True
enable = True
waiting_for_discord = False


def toggle_rpc(icon, item):
    global rpc_state, enable
    rpc_state = not item.checked

    if rpc_state:
        discord_rp.connect()
        enable = True
        logging.info("Started update thread again")
    else:
        discord_rp.disconnect()
        enable = False
        logging.info("Sent kill signal to thread")


def close_app(icon=None, item=None):
    global enable
    logging.info("Closing app...")

    try:
        discord_rp.exit_rp()
    except (RuntimeError, AttributeError, AssertionError, InvalidID):
        pass

    if tray_icon is not None:
        tray_icon.stop()
    enable = False

    sys.exit()


def create_tray_icon():
    global tray_icon

    image_path = resource_path("resources/white/icon.png" if check_dark_mode() else "resources/black/icon.png")
    icon = Image.open(image_path)

    menu = pystray.Menu(pystray.MenuItem("Enable Rich Presence", toggle_rpc,
                                         enabled=lambda i: not waiting_for_discord, checked=lambda i: rpc_state),
                        pystray.MenuItem("Open Settings", open_settings),
                        pystray.Menu.SEPARATOR,
                        pystray.MenuItem("Exit", close_app))
    tray_icon = pystray.Icon("Discord.fm", icon=icon,
                             title="Discord.fm", menu=menu)

    tray_icon.run()


def handle_update():
    cooldown = local_settings.get("cooldown")
    misc_cooldown = 30
    sc = scheduler(time.time)

    # noinspection PyUnboundLocalVariable,PyShadowingNames
    def lastfm_update(scheduler):
        if not enable:
            sc.enter(cooldown, 1, lastfm_update, (scheduler,))
            return

        try:
            track = user.now_playing()
        except KeyboardInterrupt:
            return

        if track is not None:
            try:
                discord_rp.update_status(track)
            except (BrokenPipeError, InvalidID):
                logging.info("Discord is being closed, will wait for it to open again")
                wait_for_discord()
        else:
            logging.debug("Not playing anything")

        sc.enter(cooldown, 1, lastfm_update, (scheduler,))

    def misc_update(misc_scheduler):
        logging.debug("Running misc update")

        if not enable:
            sc.enter(misc_cooldown, 2, misc_update, (misc_scheduler,))
            return

        nonlocal cooldown
        cooldown = local_settings.get("cooldown")

        if tray_icon is not None:
            image_path = resource_path("resources/white/icon.png"
                                       if check_dark_mode() else "resources/black/icon.png")
            icon = Image.open(image_path)
            tray_icon.icon = icon

        sc.enter(misc_cooldown, 2, misc_update, (misc_scheduler,))

    sc.enter(cooldown, 1, lastfm_update, (sc,))
    sc.enter(misc_cooldown, 2, misc_update, (sc,))
    sc.run()


def wait_for_discord():
    global enable, waiting_for_discord
    enable = False
    notification_called = False
    waiting_for_discord = True
    tray_icon.update_menu()

    while True:
        if process.check_process_running("Discord", "DiscordCanary"):
            try:
                discord_rp.connect()
            except (FileNotFoundError, InvalidPipe):
                continue
            except PermissionError as e:
                if not notification_called:
                    logging.critical("Another user has Discord open, notifying user", exc_info=e)

                    title = "Another user has Discord open"
                    message = "Discord.fm will not update your Rich Presence or theirs. Please close the other " \
                              "instance before scrobbling on this account. "
                    icon = resource_path(
                        "resources/white/icon.png" if check_dark_mode() else "resources/black/icon.png")

                    if system() == "Windows":
                        notification.notify(
                            title=title,
                            message=message,
                            app_name="Discord.fm",
                        )
                    else:
                        notification.notify(
                            title=title,
                            message=message,
                            app_name="Discord.fm",
                            app_icon=icon
                        )

                    notification_called = True
                continue

            break
        else:
            time.sleep(10)

    waiting_for_discord = False
    enable = True
    tray_icon.update_menu()


if __name__ == "__main__":
    log_setup.setup_logging("main")
    atexit.register(close_app)

    if updates.check_version_and_download():
        logging.info("Quitting to allow installation of newer version")
        close_app()

    if not os.path.isfile(resource_path(".env")):
        logging.critical(".env file not found, unable to get API keys and data!")
        close_app()

    no_username = local_settings.get("username") == ""
    if local_settings.first_load or no_username and is_frozen():
        logging.info("First load, opening settings UI and waiting for it to be closed...")
        open_settings()

        while not process.check_process_running("settings_ui"):
            pass

        while process.check_process_running("settings_ui"):
            time.sleep(1.5)
    elif no_username and not is_frozen():
        logging.critical("No username found - please add a username to settings and restart the app")
        close_app()

    if process.check_process_running("discord_fm"):
        logging.info("Discord.fm is already running, opening settings")

        open_settings()
        close_app()

    if sys.argv.__contains__("-o"):
        logging.info("\"-o\" argument was found, opening settings")
        open_settings()

    tray_thread = Thread(target=create_tray_icon)
    tray_thread.start()

    while tray_icon is None:
        pass

    wait_for_discord()

    try:
        handle_update()
    except (KeyboardInterrupt, SystemExit):
        close_app()
