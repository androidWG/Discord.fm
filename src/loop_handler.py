import logging
import time
from sched import scheduler

from PIL import Image
from pypresence import PipeClosed

import process
import util
import wrappers.last_fm_user
from util.status import Status
from wrappers.system_tray_icon import SystemTrayIcon
from wrappers.track_info import TrackInfo

logger = logging.getLogger("discord_fm").getChild(__name__)


class LoopHandler:
    def __init__(self, manager):
        self.m = manager
        self.tray: SystemTrayIcon = manager.tray_icon
        self.user = wrappers.last_fm_user.LastFMUser(manager)
        self.sc = scheduler(time.time)

        self._last_track = None

        self.cooldown = manager.settings.get("cooldown")
        self.misc_cooldown = 15

    def handle_update(self):
        self.sc.enter(self.cooldown, 1, self._lastfm_update, (self.sc,))
        self.sc.enter(self.misc_cooldown, 2, self._misc_update, (self.sc,))
        self.sc.run()

    def force_update(self):
        logger.info("Clearing scheduler queue and forcing update")
        for event in self.sc.queue:
            logger.debug(f"Cancelling event {event}")
            self.sc.cancel(event)

        self.sc.enter(0, 1, self._lastfm_update, (self.sc,))
        self.sc.enter(0, 2, self._misc_update, (self.sc,))
        logger.info("Running updates immediately")

    def _lastfm_update(self, scheduler_ref):
        if (
            self.m.status == Status.DISABLED
            or self.m.status == Status.WAITING_FOR_DISCORD
        ):
            self.sc.enter(self.cooldown, 1, self._lastfm_update, (scheduler_ref,))
            return
        elif self.m.status == Status.KILL:
            return

        self._check_discord_running()

        try:
            track = self.user.now_playing()
        except KeyboardInterrupt:
            return

        try:
            if track is not None:
                self.m.discord_rp.update_status(track)
                self._last_track = track
            else:
                logger.debug("Not playing anything")
                self.m.discord_rp.clear_presence()
        except (
            BrokenPipeError,
            PipeClosed,
            RuntimeError,
            AttributeError,
            AssertionError,
        ):
            self._check_discord_running()

        if not self.m.status == Status.KILL:
            self.sc.enter(self.cooldown, 1, self._lastfm_update, (scheduler_ref,))

    def _misc_update(self, misc_scheduler):
        logger.debug("Running misc update")
        if self.m.status == Status.DISABLED:
            self.sc.enter(self.misc_cooldown, 2, self._misc_update, (misc_scheduler,))
            return
        elif self.m.status == Status.KILL:
            return

        self.cooldown = self.m.settings.get("cooldown")
        image_path = util.resource_path(
            "resources", "white" if util.check_dark_mode() else "black", "icon.png"
        )
        icon = Image.open(image_path)
        self.tray.ti.icon = icon

        self.m.settings.load()
        # Reload if username has been changed
        if (
            self.user.user.name is not None
            and not self.m.settings.get("username") == self.user.user.name
        ):
            self.m.reload()

        if not self.m.status == Status.KILL:
            self.sc.enter(self.misc_cooldown, 2, self._misc_update, (misc_scheduler,))

    def _check_discord_running(self):
        if not process.check_process_running("Discord", "DiscordCanary"):
            logger.info("Discord was closed, waiting for reopen")
            self.m.wait_for_discord(Status.ENABLED)
            self.m.discord_rp.clear_last_track()

    def reload_lastfm(self):
        self.user = wrappers.last_fm_user.LastFMUser(self.m)

    def get_last_track(self) -> TrackInfo | None:
        return self._last_track
