import random
import unittest
from unittest.mock import MagicMock, patch

import psutil

import process


class TestProcess(unittest.TestCase):
    data_list = [MagicMock(pid=x) for x in range(0, 128)]

    @patch("app_manager.AppManager.close")
    @patch("psutil.process_iter")
    def test_iter_exception(self, mock_iter: MagicMock, mock_exit: MagicMock):
        mock_iter.side_effect = psutil.AccessDenied(1234, "test", "testtest")
        process.get_external_process("process")
        mock_exit.assert_called_once()

    @patch("psutil.process_iter")
    def test_access_denied(self, mock_iter: MagicMock):
        mock_iter.return_value = self.data_list

        random_proc = random.randint(0, 128)
        mock_iter.return_value[random_proc].name.side_effect = psutil.AccessDenied()

        process.get_external_process("process")

        for m in mock_iter.return_value:
            m.name.assert_called()

    @patch("util.process.get_external_process")
    @patch("psutil.Process")
    def test_kill_process(self, mock_proc: MagicMock, mock_processes: MagicMock):
        mock_processes.return_value = [MagicMock(pid=1234)]
        mock_proc.return_value.children.return_value = self.data_list

        random_proc = random.randint(0, 128)
        mock_proc.return_value.children.return_value[
            random_proc
        ].side_effect = psutil.NoSuchProcess

        process.kill_process("process")

        mock_proc.return_value.children.assert_called_with(recursive=True)
        mock_proc.return_value.kill.assert_called()


if __name__ == "__main__":
    unittest.main()
