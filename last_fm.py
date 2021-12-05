import logging
import pylast
import track_info
import util.request_handler
import discord_rich_presence as discord_rp
from os import environ
from dotenv import load_dotenv
from util import resource_path

load_dotenv(resource_path(".env"))

API_KEY = environ.get("lastfm_key")
API_SECRET = environ.get("lastfm_secret")

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)


class LastFMUser:
    def __init__(self, username):
        self.username = username
        self.user = network.get_user(username)

    def now_playing(self):
        request = util.request_handler.attempt_request(
            self.user.get_now_playing,
            "user's Now Playing",
            timeout_func=discord_rp.disconnect
        )

        if request is not None:
            info = track_info.TrackInfo(request)
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
            logging.warning("Unable to communicate with Last.fm servers, check your internet connection", exc_info=e)
            return None
