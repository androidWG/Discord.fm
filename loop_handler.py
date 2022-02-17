import logging
import time
import util
import globals as g
import wrappers.last_fm_user
from PIL import Image
from sched import scheduler
from pypresence import InvalidID
from settings import local_settings
from wrappers.system_tray_icon import SystemTrayIcon

logger = logging.getLogger("discord_fm").getChild(__name__)


class LoopHandler:
    def __init__(self, tray_icon: SystemTrayIcon):
        self._last_track = None
        self.tray = tray_icon
        self.user = wrappers.last_fm_user.LastFMUser(local_settings.get("username"))
        if not self.user.check_username():
            raise ValueError("Username is invalid")
        self.sc = scheduler(time.time)

        self.cooldown = local_settings.get("cooldown")
        self.misc_cooldown = 15

    def handle_update(self):
        self.sc.enter(self.cooldown, 1, self._lastfm_update, (self.sc,))
        self.sc.enter(self.misc_cooldown, 2, self._misc_update, (self.sc,))
        self.sc.run()

    # noinspection PyUnboundLocalVariable,PyShadowingNames
    def _lastfm_update(self, scheduler):
        if g.current == g.Status.DISABLED or g.current == g.Status.WAITING_FOR_DISCORD:
            self.sc.enter(self.cooldown, 1, self._lastfm_update, (scheduler,))
            return
        elif g.current == g.Status.KILL:
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
                logger.info("Discord is being closed, will wait for it to open again")
                self.tray.wait_for_discord()
        else:
            logger.debug("Not playing anything")

        if not g.current == g.Status.KILL:
            self.sc.enter(self.cooldown, 1, self._lastfm_update, (scheduler,))

    def _misc_update(self, misc_scheduler):
        logger.debug("Running misc update")
        if g.current == g.Status.DISABLED:
            self.sc.enter(self.misc_cooldown, 2, self._misc_update, (misc_scheduler,))
            return
        elif g.current == g.Status.KILL:
            return

        self.cooldown = local_settings.get("cooldown")
        image_path = util.resource_path("resources/white/icon.png"
                                        if util.check_dark_mode() else "resources/black/icon.png")
        icon = Image.open(image_path)
        self.tray.ti.icon = icon

        local_settings.load()
        # Reload if username has been changed
        if self.user.user.name is not None and not local_settings.get("username") == self.user.user.name:
            g.manager.reload()

        if not g.current == g.Status.KILL:
            self.sc.enter(self.misc_cooldown, 2, self._misc_update, (misc_scheduler,))

    def reload_lastfm(self):
        username = local_settings.get("username")
        logger.debug(f"Reloading LastFMUser with username \"{username}\"")
        self.user = wrappers.last_fm_user.LastFMUser(username)
