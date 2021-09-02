import logging
import discord_rich_presence as discord_rp
import util
import settings
from PIL import Image
from pystray import Icon, Menu, MenuItem as item
from last_fm import LastFMUser
from util import log_setup
from util.repeated_timer import RepeatedTimer

__version = "0.0.1"

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


def close_from_tray(Icon, item):
    tray_icon.stop()
    discord_rp.exit_rp()


def update():
    global no_song_counter
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
    log_setup.setup_logging("main")

    discord_rp.connect()

    cooldown = settings.get("cooldown")
    update()
    check_track_timer = RepeatedTimer(cooldown, update, )

    image_path = util.resource_path("resources/tray_icon.png")
    icon = Image.open(image_path)

    menu_icon = Menu(item('Enable Rich Presence', toggle_rpc, checked=lambda item: rpc_state), Menu.SEPARATOR,
                     item('Exit', close_from_tray))
    tray_icon = Icon('Last.fm Discord Rich Presence', icon=icon,
                     title="Last.fm Discord Rich Presence", menu=menu_icon)

    tray_icon.run()


if __name__ == "__main__":
    main()
