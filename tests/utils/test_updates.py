import unittest
import util.updates
from unittest.mock import MagicMock, patch


class TestUpdates(unittest.TestCase):
    @patch("install.windows.do_silent_install")
    @patch.object(util.updates, "download_asset")
    @patch("settings.Settings.get")
    @patch.object(util.updates, "get_newest_release")
    def test_check(self, mock_newest: MagicMock, mock_get: MagicMock, mock_download: MagicMock, *mocks):
        mock_get.return_value = False
        # Should return false and get_newest_release shouldn't be called because auto-updates are disabled
        self.assertFalse(util.updates.check_version_and_download())

        mock_get.return_value = True
        mock_newest.return_value = None
        # Should return false since get_newest_returned an error
        self.assertFalse(util.updates.check_version_and_download())

        mock_newest.return_value = MagicMock()
        # Should return true since an update was found, and download_asset should be called
        self.assertTrue(util.updates.check_version_and_download())

        self.assertEqual(mock_newest.call_count, 2)
        self.assertEqual(mock_download.call_count, 1)


if __name__ == '__main__':
    unittest.main()
