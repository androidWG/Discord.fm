from unittest import TestCase, main
from unittest.mock import MagicMock, patch

import pylast


class TestTrackInfo(TestCase):
    title = "TestTitle"
    artist = "TestArtist"
    artist2 = "TestArtist2"
    duration = 2852

    data1 = pylast.Track(artist, title, None, "TestUsername")
    data2 = pylast.Track(artist2, title, None, "TestUsername")

    manager = MagicMock()

    @patch("pylast.Track.get_cover_image")
    @patch("util.request_handler.RequestHandler.attempt_request")
    def test_values(self, mock_request_handler: MagicMock, mock_cover: MagicMock):
        mock_request_handler.return_value = self.duration

        result = track_info.TrackInfo(self.manager, self.data1)

        self.assertEqual(result.name, self.title)
        self.assertEqual(result.artist, self.artist)
        self.assertEqual(result.duration, self.duration)

    @patch("pylast.Track.get_cover_image")
    @patch("util.request_handler.RequestHandler.attempt_request")
    def test_equal(self, mock_request_handler: MagicMock, mock_cover: MagicMock):
        mock_request_handler.return_value = self.duration

        info1 = track_info.TrackInfo(self.manager, self.data1)
        info2 = track_info.TrackInfo(self.manager, self.data1)
        info3 = track_info.TrackInfo(self.manager, self.data2)

        self.assertEqual(info1, info2, "Track info gathered is different!")
        self.assertNotEqual(info1, info3, "Track info gathered is not different!")

if __name__ == "__main__":
    main()
