class Track:
    name: str
    artist: str
    album: str
    duration: str

    def __init__(self, lastfm_track):
        self.name = lastfm_track.title
        self.artist = lastfm_track.artist.name
        self.album = lastfm_track.get_album()
        self.duration = lastfm_track.get_duration()
