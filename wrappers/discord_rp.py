import asyncio
import datetime
import logging
from os import environ

from dotenv import load_dotenv
from pypresence import Presence

from util import resource_path, track_info


class DiscordRP:
    def __init__(self):
        load_dotenv(resource_path(".env"))
        client_id = environ.get("discord_app_id")

        self.presence = Presence(client_id)
        self.last_track = None

    def connect(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.presence.connect()
        logging.debug("Connected to Discord")

    def disconnect(self):
        self.presence.clear()
        logging.debug("Cleared Discord status")

    def exit_rp(self):
        self.presence.clear()
        self.presence.close()
        logging.info("Closed Discord Rich Presence")

    def update_status(self, track: track_info.TrackInfo):
        if self.last_track == track:
            logging.debug(f"Track {track.name} is the same as last track {self.last_track.name}, not updating")
        else:
            logging.info("Now playing: " + track.name)

            start_time = datetime.datetime.now().timestamp()
            self.last_track = track
            time_remaining = (track.duration / 1000) + start_time

            name = track.name + " " if len(track.name) < 2 else track.name
            artist = track.artist + " " if len(track.artist) < 2 else track.artist
            try:
                if track.duration != 0:
                    self.presence.update(details=name, state=artist, end=int(time_remaining),
                                         large_image="lastfm", large_text="Discord.fm")
                else:
                    self.presence.update(details=name, state=artist,
                                         large_image="lastfm", large_text="Discord.fm")
            except RuntimeError:
                logging.warning("pypresence said update thread was already running")