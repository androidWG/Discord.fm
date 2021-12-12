import logging
import time
import tray
import util
import wrappers
from PIL import Image
from sched import scheduler
from pypresence import InvalidID
from globals import status
from settings import local_settings

user = wrappers.LastFMUser(local_settings.get("username"))
sc = scheduler(time.time)


def handle_update():
    cooldown = local_settings.get("cooldown")
    misc_cooldown = 30

    # noinspection PyUnboundLocalVariable,PyShadowingNames
    def lastfm_update(scheduler):
        if status == status.DISABLED or status == status.WAITING_FOR_DISCORD:
            sc.enter(cooldown, 1, lastfm_update, (scheduler,))
            return
        elif status == status.KILL:
            return

        try:
            track = user.now_playing()
        except KeyboardInterrupt:
            return

        if track is not None:
            try:
                tray.rp.update_status(track)
            except (BrokenPipeError, InvalidID):
                logging.info("Discord is being closed, will wait for it to open again")
                tray.wait_for_discord()
        else:
            logging.debug("Not playing anything")

        sc.enter(cooldown, 1, lastfm_update, (scheduler,))

    def misc_update(misc_scheduler):
        logging.debug("Running misc update")
        if status == status.DISABLED:
            sc.enter(misc_cooldown, 2, misc_update, (misc_scheduler,))
            return
        elif status == status.KILL:
            return

        nonlocal cooldown
        cooldown = local_settings.get("cooldown")

        if tray.tray_icon is not None:
            image_path = util.resource_path("resources/white/icon.png"
                                            if util.check_dark_mode() else "resources/black/icon.png")
            icon = Image.open(image_path)
            tray.tray_icon.icon = icon

        sc.enter(misc_cooldown, 2, misc_update, (misc_scheduler,))

    sc.enter(cooldown, 1, lastfm_update, (sc,))
    sc.enter(misc_cooldown, 2, misc_update, (sc,))
    sc.run()
