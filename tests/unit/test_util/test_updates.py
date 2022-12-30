import unittest
from unittest.mock import MagicMock, patch

from packaging import version

from util import updates


class TestUpdates(unittest.TestCase):
    asset = {
        "name": "discordfm-setup-win.exe",
        "content_type": "application/x-msdownload",
    }
    asset2 = {"name": "test2.txt", "content_type": "test"}
    asset3 = {"name": "test3", "content_type": "test/test"}

    get_newest_tuple = (version.parse("1.2.3"), asset)

    @patch("util.request_handler.RequestHandler.attempt_request")
    def test_newest_release(self, mock_request: MagicMock):
        manager = MagicMock()
        manager.settings.get.return_value = False
        mock_request.return_value.json.return_value = {
            "prerelease": True,
            "published_at": "2002-06-01",
            "tag_name": "v1.2.3",
            "assets": [self.asset, self.asset2, self.asset3],
        }

        self.assertEqual(updates.get_newest_release(manager), self.get_newest_tuple)

        manager.settings.get.return_value = True
        mock_request.return_value.json.return_value = [
            {
                "prerelease": False,
                "published_at": "2002-06-01",
                "tag_name": "v0.8.0",
                "assets": [self.asset2],
            },
            {
                "prerelease": False,
                "published_at": "2002-06-01",
                "tag_name": "v1.1.1",
                "assets": [self.asset, self.asset2],
            },
            {
                "prerelease": False,
                "published_at": "2002-06-01",
                "tag_name": "v1.2.3",
                "assets": [self.asset, self.asset2, self.asset3],
            },
        ]

        self.assertEqual(updates.get_newest_release(manager), self.get_newest_tuple)


if __name__ == "__main__":
    unittest.main()
