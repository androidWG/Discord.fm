import pylast
from unittest import TestCase, main
from unittest.mock import patch, MagicMock
import wrappers.discord_rp
import wrappers.last_fm_user


class TestLastFm(TestCase):
    data = pylast.Track("TestArtist", "TestTitle", None, "TestUsername")
    error = pylast.WSError(None, None, "User not found")
    usernames = {
        "test": True,
        "TEST01": False,
        "andodide": True,
        "androidWG": False}

    def test_invalid_username(self):
        with self.assertRaises(ValueError):
            wrappers.last_fm_user.LastFMUser("")

    @patch("dotenv.load_dotenv")
    @patch("os.environ.get")
    @patch("pylast.User.get_now_playing")
    def test_check_username(self, mock_now_playing: MagicMock, *mock):
        """Test if the check_username function is correctly handling exceptions from pylast"""
        mock_now_playing.side_effect = [
            self.data,
            self.error,
            self.data,
            self.error]

        for name in self.usernames.keys():
            user = wrappers.last_fm_user.LastFMUser(name)

            result = user.check_username()
            self.assertEqual(result, self.usernames[name])

    @patch("util.request_handler.attempt_request")
    @patch("util.track_info.TrackInfo")
    def test_now_playing(self, mock_track_info: MagicMock, mock_request_handler: MagicMock):
        """Test if now_playing properly handles None objects and """
        mock = MagicMock(name="TestTitle", artist="TestArtist", duration=2852)
        mock_track_info.return_value = mock
        mock_request_handler.side_effect = [None, self.data, self.data]

        user = wrappers.last_fm_user.LastFMUser(list(self.usernames)[0])

        result1 = user.now_playing()
        result2 = user.now_playing()
        result3 = user.now_playing()

        self.assertIsNone(result1)
        self.assertEqual(result2, mock)
        self.assertEqual(result3, mock)
        mock_track_info.assert_called_once()


class TestDiscordRP(TestCase):
    title = "TestTitle"
    artist = "TestArtist"
    artist2 = "TestArtist2"

    data1 = MagicMock(name=title, artist=artist2, duration=5005)
    data2 = MagicMock(name=title, artist=artist, duration=2852)

    rp = wrappers.discord_rp.DiscordRP()

    @patch("pypresence.Presence.update")
    def test_update_status(self, mock_update: MagicMock):
        """Test if status updates function correctly with TrackInfo objects"""
        mock_update.return_value = True

        self.rp.update_status(self.data1)
        self.rp.update_status(self.data2)
        self.rp.update_status(self.data2)

        with self.assertRaises(AttributeError):
            self.rp.update_status(None)


if __name__ == '__main__':
    main()
