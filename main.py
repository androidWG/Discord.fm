import logging
import discord_rich_presence
from PIL import Image
from pystray import Icon, Menu, MenuItem as item

import util
from last_fm import LastFMUser
from util import log_setup, settings
from util.repeated_timer import RepeatedTimer

user = LastFMUser("andodide")
check_track_timer = None
rpc_state = True


def toggle_rpc(icon, item):
    global rpc_state
    rpc_state = not item.checked

    if rpc_state:
        check_track_timer.start()

        discord_rich_presence.connect()
        update()

        logging.info("Started Discord Rich Presence")
    else:
        check_track_timer.stop()
        discord_rich_presence.disconnect()
        logging.info("Stopped Discord Rich Presence")


def update():
    track = user.now_playing()

    if track is None:
        logging.info("No song playing")
    else:
        discord_rich_presence.update_status(track)


def main():
    global check_track_timer
    log_setup.setup_logging("main")

    discord_rich_presence.connect()

    cooldown = settings.local_settings.cooldown
    update()
    update()
    check_track_timer = RepeatedTimer(cooldown, update, )

    image_path = util.resource_path("assets/icon.png")
    icon = Image.open(image_path)

    menu_icon = Menu(item('Enable Rich Presence', toggle_rpc, checked=lambda item: rpc_state), Menu.SEPARATOR,
                     item('Exit', exit))
    tray_icon = Icon('Last.fm Discord Rich Presence', icon=icon,
                     title="Last.fm Discord Rich Presence", menu=menu_icon)

    tray_icon.run()


if __name__ == "__main__":
    main()
