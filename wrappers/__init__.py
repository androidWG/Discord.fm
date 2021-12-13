import time
import pylast
import util.request_handler
import asyncio
import logging
import datetime
from os import environ
from typing import Callable
from dotenv import load_dotenv
from pypresence import Presence, exceptions
from util import resource_path, track_info


class LastFMUser:
    _last_request: tuple[pylast.Track, track_info.TrackInfo] = (None, None)

    def __init__(self, username: str, inactive_func: Callable = None):
        if username == "":
            raise ValueError("Username is empty")

        load_dotenv(resource_path(".env"))

        api_key = environ.get("lastfm_key")
        api_secret = environ.get("lastfm_secret")
        network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret)

        self.username = username
        self.inactive_func = inactive_func
        self.user = network.get_user(username)

    def now_playing(self):
        request = util.request_handler.attempt_request(
            self.user.get_now_playing,
            "user's Now Playing",
            inactive_func=self.inactive_func
        )

        if request == self._last_request[0]:
            return self._last_request[1]
        elif request is not None:
            info = track_info.TrackInfo(request)
            self._last_request = (request, info)
            return info
        else:
            return None

    def check_username(self):
        try:
            self.user.get_now_playing()
            return True
        except pylast.WSError as e:
            if e.details == "User not found":
                return False
            else:
                logging.info("An exception occurred while checking username", exc_info=e)
                return None
        except (ConnectionError, pylast.NetworkError) as e:
            logging.warning("Unable to communicate with Last.fm servers, check your request_handler connection",
                            exc_info=e)
            return None


class DiscordRP:
    def __init__(self):
        load_dotenv(resource_path(".env"))
        client_id = environ.get("discord_app_id")

        while True:
            try:
                self.presence = Presence(client_id)
                break
            except exceptions.DiscordNotFound:
                time.sleep(1)
                continue
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
