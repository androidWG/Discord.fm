import unittest
from packaging import version
from unittest.mock import MagicMock, patch
from util import updates


class TestUpdates(unittest.TestCase):
    asset = {"name": "discordfm-setup-win.exe", "content_type": "application/x-msdownload"}
    asset2 = {"name": "test2.txt", "content_type": "test"}
    asset3 = {"name": "test3", "content_type": "test/test"}

    get_newest_tuple = (version.parse("1.2.3"), asset)

    @patch("util.install.windows.do_silent_install")
    @patch.object(updates, "download_asset")
    @patch("settings.Settings.get")
    @patch.object(updates, "get_newest_release")
    def test_check(self, mock_newest: MagicMock, mock_get: MagicMock, mock_download: MagicMock, *mocks):
        mock_get.return_value = False
        # Should return false and get_newest_release shouldn't be called because auto-updates are disabled
        self.assertFalse(updates.check_version_and_download())

        mock_get.return_value = True
        mock_newest.return_value = None, None
        # Should return false since get_newest_returned an error
        self.assertFalse(updates.check_version_and_download())

        mock_newest.return_value = self.get_newest_tuple
        # Should return true since an update was found, and download_asset should be called
        self.assertTrue(updates.check_version_and_download())

        self.assertEqual(mock_newest.call_count, 2)
        self.assertEqual(mock_download.call_count, 1)

    @patch("settings.Settings.get")
    @patch("util.request_handler.RequestHandler.attempt_request")
    def test_newest_release(self, mock_request: MagicMock, mock_get: MagicMock):
        mock_get.return_value = False
        mock_request.return_value.json.return_value = {
            "tag_name": "v1.2.3",
            "assets": [self.asset, self.asset2, self.asset3]}

        self.assertEqual(updates.get_newest_release(), self.get_newest_tuple)

        mock_get.return_value = True
        mock_request.return_value.json.return_value = [
            {"tag_name": "v0.8.0",
             "assets": [self.asset2]},
            {"tag_name": "v1.1.1",
             "assets": [self.asset, self.asset2]},
            {"tag_name": "v1.2.3",
             "assets": [self.asset, self.asset2, self.asset3]},
        ]

        self.assertEqual(updates.get_newest_release(), self.get_newest_tuple)


if __name__ == '__main__':
    unittest.main()
