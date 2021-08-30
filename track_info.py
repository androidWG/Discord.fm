import pylast

class TrackInfo:
    name: str
    artist: str
    album: str
    duration: str

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
            pass
