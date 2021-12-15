import unittest
import util.updates
from unittest.mock import MagicMock, patch


class TestUpdates(unittest.TestCase):
    @patch("install.windows.do_silent_install")
    @patch.object(util.updates, "download_asset")
    @patch("settings.Settings.get")
    @patch.object(util.updates, "get_newest_release")
    def test_check(self, mock_newest: MagicMock, mock_get: MagicMock, *mocks):
        mock_get.return_value = False
        self.assertFalse(util.updates.check_version_and_download())

        mock_get.return_value = True
        mock_newest.return_value = None
        self.assertFalse(util.updates.check_version_and_download())

        mock_newest.return_value = MagicMock()
        self.assertTrue(util.updates.check_version_and_download())

        self.assertEqual(mock_newest.call_count, 2)


if __name__ == '__main__':
    unittest.main()
