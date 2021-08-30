import logging
from pypresence import Presence
import datetime

client_id = '702984897496875072'
discord_presence = Presence(client_id)
already_enabled = False
already_disabled = True
start_time = None
LastTrack = None


def connect():
    discord_presence.connect()
    logging.debug("Connected to Discord")


def disconnect():
    discord_presence.clear()
    discord_presence.close()
    print('Disconnected from Discord')


def update_status(track):
    global start_time, LastTrack
    if LastTrack == track:
        pass
    else:
        logging.info("Now Playing: " + track)

        start_time = datetime.datetime.now().timestamp()
        LastTrack = track
        time_remaining = float(str(track.duration)[0:3]) + start_time
        if time_remaining != '0':
            discord_presence.update(details=track.name, state=track.album, end=time_remaining,
                                    large_image='icon', large_text='Last.fm Discord Rich Presence')
        else:
            discord_presence.update(details=track.name, state=track.album,
                                    large_image='icon', large_text='Last.fm Discord Rich Presence')


def disable_RPC():
    discord_presence.clear()
    discord_presence.close()
    print('Disconnected from Discord due to inactivity on Last.fm')
