import asyncio
import datetime
import logging

from pypresence import Presence, InvalidID

from wrappers import track_info

logger = logging.getLogger("discord_fm").getChild(__name__)


class DiscordRP:
    def __init__(self):
        self.presence = None
        self.last_track = None
        self.connected = False

    def start(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.presence = Presence("881950079240536135")

    def connect(self):
        if self.presence is None:
            self.start()

        self.presence.connect()
        self.connected = True
        logger.info("Connected to Discord")

    def clear_presence(self):
        self.presence.clear()

    def exit_rp(self):
        if self.presence is None:
            return

        try:
            self.presence.clear()
            self.presence.close()
        except InvalidID as e:
            logger.debug(
                "Caught InvalidID exception while closing presence, Discord was likely closed"
            )

        self.connected = False
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
