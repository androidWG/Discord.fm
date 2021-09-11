import asyncio
import logging
import os
import sched
import sys
import time
import discord_rich_presence as discord_rp
import settings
from threading import Thread
from PIL import Image
from pystray import Icon, Menu, MenuItem
from last_fm import LastFMUser
from util import log_setup, resource_path

__version = "0.2.0"


# From https://stackoverflow.com/a/16993115/8286014
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt) or issubclass(exc_type, SystemExit):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

user = LastFMUser(settings.get("username"))
no_song_counter = 0
tray_icon = None
rpc_state = True
enable = True


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
    except RuntimeError:
        logging.debug("Got RuntimeError")
    except AttributeError:
        logging.debug("Got AttributeError")

    if tray_icon is not None:
        tray_icon.stop()
    enable = False

    if os.path.isfile(pidfile):
        os.remove(pidfile)
    sys.exit()


def create_tray_icon():
    global tray_icon
    image_path = resource_path("resources/tray_icon.png")
    icon = Image.open(image_path)

    menu_icon = Menu(MenuItem("Enable Rich Presence", toggle_rpc, checked=lambda item: rpc_state), Menu.SEPARATOR,
                     MenuItem("Exit", close_app))
    tray_icon = Icon("Discord.fm", icon=icon,
                     title="Discord.fm", menu=menu_icon)

    tray_icon.run()


def handle_update():
    cooldown = settings.get("cooldown")
    sc = sched.scheduler(time.time, time.sleep)

    def update(scheduler):
        global no_song_counter, enable
        if enable:
            track = user.now_playing()
            if track is None:
                logging.debug("No song playing")
                no_song_counter += 1

                if no_song_counter == 5:  # Last.fm takes a while to update on song change, make sure user is
                    # listening to nothing to clear RP
                    discord_rp.disconnect()
            else:
                no_song_counter = 0
                discord_rp.update_status(track)

        sc.enterabs(cooldown, 1, update, (scheduler,))

    sc.enterabs(cooldown, 1, update, (sc,))
    sc.run()


if __name__ == "__main__":
    log_setup.setup_logging("main")
    pidfile = "discord_fm.pid"

    if os.path.isfile(pidfile):
        print(f"{pidfile} already exists, exiting")
        sys.exit()
    open(pidfile, "w").write(str(os.getpid()))

    discord_rp.connect()

    tray_thread = Thread(target=create_tray_icon)
    tray_thread.start()

    try:
        handle_update()
    except KeyboardInterrupt or SystemExit:
        close_app()
