import pylast
import last_fm
from unittest import TestCase, main
from unittest.mock import patch, MagicMock


@patch("pylast.User.get_now_playing")
class TestLastFm(TestCase):
    data = pylast.Track("TestArtist", "TestTitle", None, "TestUsername")
    error = pylast.WSError(None, None, "User not found")
    usernames = {
        "test": True,
        "TEST01": False,
        "andodide": True,
        "androidWG": False}

    def test_username(self, mock_now_playing):
        mock_now_playing.side_effect = [
            self.data,
            self.error,
            self.data,
            self.error]

        for name in self.usernames.keys():
            user = last_fm.LastFMUser(name)

            result = user.check_username()
            self.assertEqual(result, self.usernames[name])

        with self.assertRaises(ValueError):
            last_fm.LastFMUser("")


if __name__ == '__main__':
    main()
