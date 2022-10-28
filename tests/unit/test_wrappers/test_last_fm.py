from unittest import TestCase, main
from unittest.mock import MagicMock, patch

import pylast

from wrappers.last_fm_user import LastFMUser


class TestLastFm(TestCase):
    data = pylast.Track("TestArtist", "TestTitle", None, "TestUsername")
    error = pylast.WSError(None, None, "User not found")
    usernames = {"test": True, "TEST01": False, "andodide": True, "androidWG": False}

    def test_invalid_username(self):
        manager = MagicMock()
        manager.settings.get.return_value = ""

        with self.assertRaises(ValueError):
            LastFMUser(manager)

    @patch("os.environ.get")
    @patch("util.request_handler.RequestHandler.attempt_request")
    def test_check_username(self, mock_request_handler: MagicMock, *mock):
        """Test if the check_username function is correctly handling exceptions from pylast"""
        mock_request_handler.side_effect = [
            self.data,
            self.error,
            self.data,
            self.error,
        ]

        for name in self.usernames.keys():
            manager = MagicMock()
            manager.settings.get.return_value(name)
            user = LastFMUser(manager)

            result = user.check_username()
            print(result)
            self.assertEqual(result, self.usernames[name])

    @patch("util.request_handler.RequestHandler.attempt_request")
    @patch("wrappers.track_info.TrackInfo")
    def test_now_playing(
        self, mock_track_info: MagicMock, mock_request_handler: MagicMock
    ):
        """Test if now_playing properly handles None objects and"""
        mock = MagicMock(name="TestTitle", artist="TestArtist", duration=2852)
        mock_track_info.return_value = mock
        mock_request_handler.side_effect = [None, self.data, self.data]

        manager = MagicMock()
        manager.settings.get.return_value(list(self.usernames)[0])

        user = LastFMUser(manager)

        result1 = user.now_playing()
        result2 = user.now_playing()
        result3 = user.now_playing()

        self.assertIsNone(result1)
        self.assertEqual(result2, mock)
        self.assertEqual(result3, mock)
        mock_track_info.assert_called_once()


if __name__ == "__main__":
    main()
