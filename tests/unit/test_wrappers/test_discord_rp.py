from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from wrappers import discord_rp


class TestDiscordRP(TestCase):
    title = "TestTitle"
    artist = "TestArtist"
    artist2 = "TestArtist2"

    data1 = MagicMock(name=title, artist=artist2, duration=5005)
    data2 = MagicMock(name=title, artist=artist, duration=2852)

    @patch.object(discord_rp, "logger")
    @patch("pypresence.utils")
    def test_update_status(self, *mocks):
        """Test if status updates function correctly with TrackInfo objects"""
        rp = discord_rp.DiscordRP()

        rp.presence = MagicMock()

        rp.update_status(self.data1)
        rp.update_status(self.data2)
        rp.update_status(self.data2)

        with self.assertRaises(AttributeError):
            rp.update_status(None)

    @patch("asyncio.get_event_loop")
    def test_connect_disconnect(self, *mocks):
        rp = discord_rp.DiscordRP()
        rp.presence = MagicMock()

        rp.connect()
        rp.disconnect()

        rp.presence = None
        rp.connect()
        self.assertIsNotNone(rp.presence)

    @patch("asyncio.get_event_loop")
    def test_exit(self, *mocks):
        rp = discord_rp.DiscordRP()
        rp.presence = MagicMock()

        rp.exit_rp()
        rp.presence.clear.assert_called()
        rp.presence.close.assert_called()


if __name__ == "__main__":
    main()
