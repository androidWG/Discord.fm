import logging
import datetime
from os import environ
from pypresence import Presence
from dotenv import load_dotenv

load_dotenv()

client_id = environ.get("discord_app_id")
discord_presence = Presence(client_id)
start_time = None
last_track = None


def connect():
    discord_presence.connect()
    logging.debug("Connected to Discord")


def disconnect():
    discord_presence.clear()
    logging.debug('Disconnected from Discord')


def exit_rp():
    discord_presence.clear()
    discord_presence.close()
    logging.info("Closed Discord Rich Presence")


def update_status(track):
    global start_time, last_track
    if last_track == track:
        logging.debug(f"Track {track.name} is the same as last track {last_track.name}, not updating")
    else:
        logging.info("Now playing: " + track.name)

        start_time = datetime.datetime.now().timestamp()
        last_track = track
        time_remaining = (track.duration / 1000) + start_time
        try:
            if track.duration != 0:
                discord_presence.update(details=track.name, state=track.artist, end=time_remaining,
                                        large_image="lastfm", large_text="Discord.fm")
            else:
                discord_presence.update(details=track.name, state=track.artist,
                                        large_image="lastfm", large_text="Discord.fm")
        except RuntimeError:
            logging.warning("pypresence said update thread was already running")
