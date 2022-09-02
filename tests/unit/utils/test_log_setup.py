import os.path
import random
import tempfile
import unittest
from unittest.mock import patch

import util.log_setup


class LogSetupTests(unittest.TestCase):
    temp_dir = tempfile.TemporaryDirectory()

    @patch("local_settings.logs_path", temp_dir.name)
    @patch("settings.Settings.get")
    def test_delete_old_logs(self, mock_get):
        mock_get.return_value = 10

        rand_files = create_random_files(
            random.randint(2, 12), self.temp_dir.name, extension=".txt"
        )

        log_files = create_random_files(10, self.temp_dir.name, "test-")
        util.log_setup.delete_old_logs("test")
        self.assertEqual(len(self._check_files_contains(log_files)), 10)
        self.assertTrue(self._check_files_remain(rand_files))

        self._delete_all_logs()

        log_files = create_random_files(25, self.temp_dir.name, "test-")
        self.assertEqual(len(self._check_files_contains(log_files)), 10)
        self.assertTrue(self._check_files_remain(rand_files))

        self._delete_all_logs()

        log_files = create_random_files(5, self.temp_dir.name, "test-")
        self.assertEqual(len(self._check_files_contains(log_files)), 5)
        self.assertTrue(self._check_files_remain(rand_files))

    def _delete_all_logs(self):
        for file in os.listdir(self.temp_dir.name):
            if file.__contains__(".log"):
                os.remove(os.path.join(self.temp_dir.name, file))

    def _check_files_contains(self, files: list) -> list:
        contains = []

        for file in os.listdir(self.temp_dir.name):
            filepath = os.path.join(self.temp_dir.name, file)
            if files.__contains__(filepath):
                contains.append(filepath)

        return contains

    def _check_files_remain(self, files: list):
        temp_files = [
            os.path.join(self.temp_dir.name, f) for f in os.listdir(self.temp_dir.name)
        ]
        for file in files:
            if file in temp_files:
                return False

        return True


def create_random_files(
    file_count: int, temp_dir: str, filename: str = "", extension: str = ".log"
):
    files = []
    for x in range(file_count):
        text_name = filename + str(random.randint(100, 999)) + extension
        path = os.path.join(temp_dir, text_name)
        files.append(path)

        with open(path, "wb") as file:
            file.write(random.randbytes(4096))

    return files


if __name__ == "__main__":
    unittest.main()
