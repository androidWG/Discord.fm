import logging

import pylast
import track_info
from util import settings

API_KEY = "0484c201554ae2b4fd440de08a0466b3"
API_SECRET = "1da2fb7fa90a7f9238d0441b39f0002d"

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET)


class LastFMUser:
    def __init__(self, username):
        self.username = username
        self.user = network.get_user(username)

    def now_playing(self):
        try:
            current_track = self.user.get_now_playing()
            if current_track is not None:
                track = track_info.TrackInfo(current_track)
                return track
        except pylast.WSError:
            logging.info(f"Connection problem at web service, retrying connection in {settings.get('cooldown')} seconds")
        except pylast.NetworkError:
            logging.warning("Unable to communicate with last.fm servers, check your internet connection!")
        except pylast.MalformedResponseError:
            logging.info("Last.fm internal server error, retrying connection")

        return None
