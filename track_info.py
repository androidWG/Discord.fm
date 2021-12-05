import pylast
from util import request_handler


class TrackInfo:
    name: str
    artist: str
    album: str
    duration: int

    def __init__(self, lastfm_track: pylast.Track):
        self.name = lastfm_track.title
        self.artist = lastfm_track.artist.name

        album_request = request_handler.attempt_request(
            lastfm_track.get_album,
            f"album for track \"{self.name}\"")
        duration_request = request_handler.attempt_request(
            lastfm_track.get_duration,
            f"album for track \"{self.name}\"")

        self.album = album_request
        self.duration = duration_request

    def __eq__(self, other):
        if not isinstance(other, TrackInfo):
            # don't attempt to compare against unrelated types
            return NotImplemented

        is_equal = self.name == other.name and self.artist == other.artist and self.album == other.album
        return is_equal
