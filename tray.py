import logging
import time
import pystray
import util
import util.log_setup
import util.updates
import wrappers
from globals import status
from loop import sc
from PIL import Image
from threading import Thread
from pypresence import InvalidID, InvalidPipe

rp = wrappers.DiscordRP()
rpc_state = True
waiting_for_discord = False


def close_app(icon=None, item=None):
    global status
    logging.info("Closing app...")

    try:
        rp.exit_rp()
    except (RuntimeError, AttributeError, AssertionError, InvalidID):
        pass

    tray_icon.stop()
    status = status.KILL

    if not sc.empty():
        logging.debug(f"Closing {len(sc.queue)} events...")
        for event in sc.queue:
            sc.cancel(event)


def toggle_rpc(icon, item):
    global rpc_state, status
    rpc_state = not item.checked

    if rpc_state:
        rp.connect()
        status = status.ENABLED
    else:
        rp.disconnect()
        status = status.DISABLED

    logging.info(f"Changed rpc_state to {rpc_state}")


def create_tray_icon():
    image_path = util.resource_path(
        "resources/white/icon.png" if util.check_dark_mode() else "resources/black/icon.png")
    icon = Image.open(image_path)

    menu = pystray.Menu(pystray.MenuItem("Enable Rich Presence", toggle_rpc,
                                         enabled=lambda i: not waiting_for_discord, checked=lambda i: rpc_state),
                        pystray.MenuItem("Open Settings", util.open_settings),
                        pystray.Menu.SEPARATOR,
                        pystray.MenuItem("Exit", close_app))

    icon = pystray.Icon("Discord.fm", icon=icon, title="Discord.fm", menu=menu)
    return icon


def start():
    tray_thread = Thread(target=tray_icon.run)
    tray_thread.start()


tray_icon = create_tray_icon()


def wait_for_discord():
    global status
    status = status.WAITING_FOR_DISCORD

    notification_called = False
    tray_icon.update_menu()

    while True:
        if util.process.check_process_running("Discord", "DiscordCanary"):
            try:
                rp.connect()
            except (FileNotFoundError, InvalidPipe):
                continue
            except PermissionError as e:
                if not notification_called:
                    logging.critical("Another user has Discord open, notifying user", exc_info=e)

                    title = "Another user has Discord open"
                    message = "Discord.fm will not update your Rich Presence or theirs. Please close the other " \
                              "instance before scrobbling on this account. "

                    util.basic_notification(title, message)

                    notification_called = True
                continue

            break
        else:
            time.sleep(10)

    status = status.ENABLED
    tray_icon.update_menu()
