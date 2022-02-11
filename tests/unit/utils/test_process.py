import random
import unittest
import psutil
from unittest.mock import MagicMock, patch
from util import process


class TestProcess(unittest.TestCase):
    data_list = [MagicMock(pid=x) for x in range(0, 128)]

    @patch("sys.exit")
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
        mock_proc.return_value.children.return_value[random_proc].side_effect = psutil.NoSuchProcess

        process.kill_process("process")

        mock_proc.return_value.children.assert_called_with(recursive=True)
        mock_proc.return_value.kill.assert_called()

    @patch("util.process.check_process_running")
    @patch("util.process.kill_process")
    @patch("subprocess.Popen")
    def test_start_stop(self, mock_open: MagicMock, mock_kill: MagicMock, mock_running: MagicMock):
        mock_running.return_value = False
        process.start_stop_process(MagicMock(path="test"))
        mock_open.assert_called_once_with("test")

        mock_running.return_value = True
        mock = MagicMock()
        mock.name = "test"
        process.start_stop_process(mock)
        mock_kill.assert_called_once_with("test")


if __name__ == '__main__':
    unittest.main()
