import pylast


class TrackInfo:
    name: str
    artist: str
    album: str
    duration: int

    def __init__(self, lastfm_track):
        try:
            self.name = lastfm_track.title
            self.artist = lastfm_track.artist.name
            self.album = lastfm_track.get_album()
            self.duration = lastfm_track.get_duration()
        except pylast.WSError:
            pass  # TODO
        except pylast.NetworkError:
            print("The app couldn't communicate with last.fm servers, check your internet connection!")

    def __eq__(self, other):
        if not isinstance(other, TrackInfo):
            # don't attempt to compare against unrelated types
            return NotImplemented

        is_equal = self.name == other.name and self.artist == other.artist and self.album == other.album
        return is_equal
