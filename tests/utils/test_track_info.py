import pylast
from util import track_info
from unittest import TestCase, main
from unittest.mock import MagicMock, patch


class TestTrackInfo(TestCase):
    title = "TestTitle"
    artist = "TestArtist"
    artist2 = "TestArtist2"
    duration = 2852

    data1 = pylast.Track(artist, title, None, "TestUsername")
    data2 = pylast.Track(artist2, title, None, "TestUsername")

    @patch("util.request_handler.attempt_request")
    def test_values(self, mock_request_handler: MagicMock):
        mock_request_handler.return_value = self.duration

        result = track_info.TrackInfo(self.data1)

        self.assertEqual(result.name, self.title)
        self.assertEqual(result.artist, self.artist)
        self.assertEqual(result.duration, self.duration)

    @patch("util.request_handler.attempt_request")
    def test_equal(self, mock_request_handler: MagicMock):
        mock_request_handler.return_value = self.duration

        info1 = track_info.TrackInfo(self.data1)
        info2 = track_info.TrackInfo(self.data1)
        info3 = track_info.TrackInfo(self.data2)

        self.assertTrue(info1 == info2)
        self.assertFalse(info1 == info3)


if __name__ == '__main__':
    main()
