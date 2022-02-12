import logging
import time
import util
import wrappers.last_fm_user
from PIL import Image
from sched import scheduler
from pypresence import InvalidID
from globals import current, Status
from settings import local_settings
from wrappers.system_tray_icon import SystemTrayIcon


class LoopHandler:
    def __init__(self, tray_icon: SystemTrayIcon):
        self._last_track = None
        self.tray = tray_icon
        self.user = wrappers.last_fm_user.LastFMUser(local_settings.get("username"))
        if not self.user.check_username():
            raise ValueError("Username is invalid")
        self.sc = scheduler(time.time)

        self.cooldown = local_settings.get("cooldown")
        self.misc_cooldown = 30

    def handle_update(self):
        self.sc.enter(self.cooldown, 1, self.lastfm_update, (self.sc,))
        self.sc.enter(self.misc_cooldown, 2, self.misc_update, (self.sc,))
        self.sc.run()

    # noinspection PyUnboundLocalVariable,PyShadowingNames
    def lastfm_update(self, scheduler):
        if current == Status.DISABLED or current == Status.WAITING_FOR_DISCORD:
            self.sc.enter(self.cooldown, 1, self.lastfm_update, (scheduler,))
            return
        elif current == Status.KILL:
            return

        try:
            track = self.user.now_playing()
        except KeyboardInterrupt:
            return

        if track is not None:
            try:
                self.tray.discord_rp.update_status(track)
                self._last_track = track
            except (BrokenPipeError, InvalidID):
                logging.info("Discord is being closed, will wait for it to open again")
                self.tray.wait_for_discord()
        else:
            logging.debug("Not playing anything")

        self.sc.enter(self.cooldown, 1, self.lastfm_update, (scheduler,))

    def misc_update(self, misc_scheduler):
        logging.debug("Running misc update")
        if current == Status.DISABLED:
            self.sc.enter(self.misc_cooldown, 2, self.misc_update, (misc_scheduler,))
            return
        elif current == Status.KILL:
            return

        self.cooldown = local_settings.get("cooldown")
        image_path = util.resource_path("resources/white/icon.png"
                                        if util.check_dark_mode() else "resources/black/icon.png")
        icon = Image.open(image_path)
        self.tray.tray_icon.icon = icon

        self.sc.enter(self.misc_cooldown, 2, self.misc_update, (misc_scheduler,))

    def reload_lastfm(self):
        username = local_settings.get("username")
        logging.debug(f"Reloading LastFMUser with username \"{username}\"")
        self.user = wrappers.last_fm_user.LastFMUser(username)
