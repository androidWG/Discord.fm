import asyncio
import logging
import datetime
import track_info
from os import environ
from util import resource_path
from dotenv import load_dotenv
from pypresence import Presence


load_dotenv(resource_path(".env"))

client_id = environ.get("discord_app_id")
discord_presence = Presence(client_id)
last_track = None


def connect():
    asyncio.set_event_loop(asyncio.new_event_loop())
    discord_presence.connect()
    logging.debug("Connected to Discord")


def disconnect():
    discord_presence.clear()
    logging.debug("Cleared Discord status")


def exit_rp():
    discord_presence.clear()
    discord_presence.close()
    logging.info("Closed Discord Rich Presence")


def update_status(track: track_info.TrackInfo):
    global last_track
    if last_track == track:
        logging.debug(f"Track {track.name} is the same as last track {last_track.name}, not updating")
    else:
        logging.info("Now playing: " + track.name)

        start_time = datetime.datetime.now().timestamp()
        last_track = track
        time_remaining = (track.duration / 1000) + start_time
        try:
            if track.duration != 0:
                discord_presence.update(details=track.name, state=track.artist, end=int(time_remaining),
                                        large_image="lastfm", large_text="Discord.fm")
            else:
                discord_presence.update(details=track.name, state=track.artist,
                                        large_image="lastfm", large_text="Discord.fm")
        except RuntimeError:
            logging.warning("pypresence said update thread was already running")
