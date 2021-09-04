import logging
import sys
import discord_rich_presence as discord_rp
import settings
from PIL import Image
from pystray import Icon, Menu, MenuItem
from last_fm import LastFMUser
from util import log_setup, resource_path
from util.repeated_timer import RepeatedTimer

__version = "0.1.0"

log_setup.setup_logging("main")


# From https://stackoverflow.com/a/16993115/8286014
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

user = LastFMUser(settings.get("username"))
no_song_counter = 0
check_track_timer = None
tray_icon = None
rpc_state = True


def toggle_rpc(icon, item):
    global rpc_state
    rpc_state = not item.checked

    if rpc_state:
        check_track_timer.start()

        discord_rp.connect()
        update()

        logging.info("Started Discord Rich Presence")
    else:
        check_track_timer.stop()
        discord_rp.disconnect()

        logging.info("Stopped Discord Rich Presence")


def close_from_tray(icon, item):
    global check_track_timer
    icon.visible = False
    icon.stop()
    discord_rp.exit_rp()
    check_track_timer.stop()

    sys.exit()


def update():
    global no_song_counter, user
    track = user.now_playing()

    if track is None:
        logging.debug("No song playing")
        no_song_counter += 1

        if no_song_counter == 5:  # Last.fm takes a while to update on song change, make sure user is listening to
            # nothing to clear RP
            discord_rp.disconnect()
    else:
        no_song_counter = 0
        discord_rp.update_status(track)


def main():
    global check_track_timer, tray_icon
    sys.excepthook = handle_exception

    discord_rp.connect()

    cooldown = settings.get("cooldown")
    update()
    check_track_timer = RepeatedTimer(cooldown, update, )

    image_path = resource_path("resources/tray_icon.png")
    icon = Image.open(image_path)

    menu_icon = Menu(MenuItem("Enable Rich Presence", toggle_rpc, checked=lambda item: rpc_state), Menu.SEPARATOR,
                     MenuItem("Exit", close_from_tray))
    tray_icon = Icon("Discord.fm", icon=icon,
                     title="Discord.fm", menu=menu_icon)

    tray_icon.run()


if __name__ == "__main__":
    main()
