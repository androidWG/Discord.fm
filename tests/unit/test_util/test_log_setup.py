import os.path
import random
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import util.log_setup

MAX_LOGS = 10


class LogSetupTests(unittest.TestCase):
    temp_dir = tempfile.TemporaryDirectory()

    def test_delete_old_logs(self):
        rand_files = create_random_files(
            random.randint(2, 12), self.temp_dir.name, extension=".txt"
        )

        log_files = create_random_files(MAX_LOGS, self.temp_dir.name, "test-")
        manager = MagicMock()
        manager.name = "test"
        manager.settings.logs_path = self.temp_dir.name
        manager.settings.get.return_value = MAX_LOGS
        util.log_setup.delete_old_logs(manager)

        self.assertEqual(MAX_LOGS, len(self._check_files_contains(log_files)))
        self.assertTrue(self._check_files_remain(rand_files))

        self._delete_all_logs()

        log_files = create_random_files(25, self.temp_dir.name, "test-")
        util.log_setup.delete_old_logs(manager)
        self.assertEqual(MAX_LOGS, len(self._check_files_contains(log_files)))
        self.assertTrue(self._check_files_remain(rand_files))

        self._delete_all_logs()

        log_files = create_random_files(5, self.temp_dir.name, "test-")
        util.log_setup.delete_old_logs(manager)
        self.assertEqual(5, len(self._check_files_contains(log_files)))
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
                return True

        return False


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
