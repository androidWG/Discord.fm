import logging
import pylast
import util.request_handler
from os import environ
from typing import Callable
from dotenv import load_dotenv
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
            util.request_handler.attempt_request(
                self.user.get_now_playing,
                "username validity",
            )
            return True
        except pylast.WSError as e:
            if e.details == "User not found":
                return False
