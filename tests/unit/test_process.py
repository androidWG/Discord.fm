import random
import unittest
from unittest.mock import MagicMock, patch

import psutil

import process


class TestProcess(unittest.TestCase):
    proc_with_pid_list = [MagicMock(pid=x) for x in range(0, 128)]
    proc_list = [
        "test",
        "process",
        "program",
        "app",
        "testtest",
        "test.exe",
        "os.exe.test",
    ]

    @patch("globals.manager")
    @patch("psutil.process_iter")
    def test_iter_exception(self, mock_iter: MagicMock, mock_manager: MagicMock):
        mock_iter.side_effect = psutil.AccessDenied(1234, "test", "testtest")
        process.get_external_process("x")
        mock_manager.close.assert_called_once()

    @patch("process.get_external_process")
    def test_check_running(self, mock_proc: MagicMock):
        mock_proc.return_value = [1, 2, 3]
        self.assertTrue(process.check_process_running("x"))

        mock_proc.return_value = [1]
        self.assertTrue(process.check_process_running("x"))

        mock_proc.return_value = []
        self.assertFalse(process.check_process_running("x"))

        mock_proc.return_value = None
        with self.assertRaises(TypeError):
            process.check_process_running("x")

    @patch("process.get_external_process")
    @patch("psutil.Process")
    def test_kill_process(self, mock_proc: MagicMock, mock_processes: MagicMock):
        mock_processes.return_value = [MagicMock(pid=1234)]
        mock_proc.return_value.children.return_value = self.proc_with_pid_list

        random_proc = random.randint(0, 128)
        mock_proc.return_value.children.return_value[
            random_proc
        ].side_effect = psutil.NoSuchProcess

        process.kill_process("process")

        mock_proc.return_value.children.assert_called()
        mock_proc.return_value.kill.assert_called()


if __name__ == "__main__":
    unittest.main()
