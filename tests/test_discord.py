import unittest
import discord_rich_presence
from unittest.mock import MagicMock, patch


class StatusUpdateTest(unittest.TestCase):
    title = "TestTitle"
    artist = "TestArtist"
    artist2 = "TestArtist2"

    data1 = MagicMock(name=title, artist=artist2, duration=5005)
    data2 = MagicMock(name=title, artist=artist, duration=2852)

    @patch("pypresence.Presence.update")
    def test_update_status(self, mock_update: MagicMock):
        """Test if status updates function correctly with TrackInfo objects"""
        mock_update.return_value = True

        discord_rich_presence.update_status(self.data1)
        discord_rich_presence.update_status(self.data2)
        discord_rich_presence.update_status(self.data2)

        with self.assertRaises(AttributeError):
            discord_rich_presence.update_status(None)


if __name__ == '__main__':
    unittest.main()
