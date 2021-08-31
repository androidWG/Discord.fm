import logging
from pypresence import Presence
import datetime

client_id = "881950079240536135"
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
        pass
    else:
        logging.info("Now playing: " + track.name)

        start_time = datetime.datetime.now().timestamp()
        last_track = track
        time_remaining = float(track.duration / 1000) + start_time
        if track.duration != 0:
            discord_presence.update(details=track.name, state=track.artist, end=time_remaining,
                                    large_image='lastfm', large_text='Last.fm Discord Rich Presence')
        else:
            discord_presence.update(details=track.name, state=track.artist,
                                    large_image='lastfm', large_text='Last.fm Discord Rich Presence')
