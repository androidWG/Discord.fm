import asyncio
import datetime
import logging

from pypresence import Presence

from wrappers import track_info

logger = logging.getLogger("discord_fm").getChild(__name__)


class DiscordRP:
    def __init__(self):
        self.presence = None
        self.last_track = None

    def start(self):
        self.presence = Presence("881950079240536135")

    def connect(self):
        if self.presence is None:
            self.start()

        asyncio.set_event_loop(asyncio.new_event_loop())
        self.presence.connect()
        logger.info("Connected to Discord")

    def disconnect(self):
        self.presence.clear()
        logger.info("Cleared Discord status")

    def exit_rp(self):
        self.presence.clear()
        self.presence.close()
        logger.info("Closed Discord Rich Presence")

    def update_status(self, track: track_info.TrackInfo):
        if self.last_track == track:
            logger.debug(
                f"Track {track.name} is the same as last track {self.last_track.name}, not updating"
            )
        else:
            logger.info("Now playing: " + track.name)

            start_time = datetime.datetime.now().timestamp()
            self.last_track = track
            time_remaining = (track.duration / 1000) + start_time

            name = track.name + " " if len(track.name) < 2 else track.name
            artist = track.artist + " " if len(track.artist) < 2 else track.artist
            try:
                if track.duration != 0:
                    self.presence.update(
                        details=name,
                        state=artist,
                        end=int(time_remaining),
                        large_image=track.cover,
                        large_text="Discord.fm",
                    )
                else:
                    self.presence.update(
                        details=name,
                        state=artist,
                        large_image=track.cover,
                        large_text="Discord.fm",
                    )
            except RuntimeError:
                logger.warning("pypresence said update thread was already running")
