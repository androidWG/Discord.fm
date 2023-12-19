import atexit
import hashlib
import json
import os
import random
import shutil
from pathlib import Path
from stat import S_IREAD, S_IWRITE
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

from filelock import FileLock

import settings
import settings.util

__TEMP = os.path.abspath("temp")


def remove_temp():
    print("Removing temp folder...")
    try:
        shutil.rmtree(__TEMP)
    except FileNotFoundError:
        print("temp folder doesn't exist, ignoring")


def create_temp_dir():
    if os.path.exists(__TEMP):
        shutil.rmtree(__TEMP)

    os.mkdir(__TEMP)
    temp_dir = os.path.abspath(__TEMP)
    for resource in os.listdir("tests/unit/fixtures"):
        shutil.copy(os.path.join("tests/unit/fixtures", resource), temp_dir)

    atexit.register(remove_temp)
    return temp_dir


@patch("settings.setup_logs_dir")
@patch("settings.setup_app_data_dir")
class SettingsClassTests(TestCase):
    temp_dir = create_temp_dir()

    not_json = "not_json.txt"
    invalid_json = "invalid_json.json"
    valid_json = "valid_json.json"
    locked_json = "locked_json.json"
    an_image = "image.gif"

    def test_read(self, mock_app_data: MagicMock, mock_logs: MagicMock):
        mock_app_data.return_value = self.temp_dir

        settings.Settings("Test")
        settings.Settings("Test", self.not_json)
        settings.Settings("Test", self.invalid_json)
        settings.Settings("Test", self.valid_json)
        settings.Settings("Test", self.an_image)

    def test_write(self, mock_app_data: MagicMock, mock_logs: MagicMock):
        mock_app_data.return_value = self.temp_dir
        path = os.path.join(self.temp_dir, self.locked_json)
        initial_md5 = get_md5(path)

        result1 = settings.Settings("Test")
        result1.save()
        self.assertEqual(initial_md5, get_md5(path))

        result2 = settings.Settings("Test", self.locked_json)

        os.chmod(result2.config_file_path, S_IREAD)

        result2.save()
        self.assertEqual(initial_md5, get_md5(path))

        os.chmod(result2.config_file_path, S_IWRITE)

    def test_dictionary(self, mock_app_data: MagicMock, mock_logs: MagicMock):
        mock_app_data.return_value = self.temp_dir
        with open(os.path.join(self.temp_dir, self.valid_json)) as file:
            data: dict = json.load(file)
            test = settings.Settings("Test", self.valid_json)

            self.assertEqual(test.get("cooldown"), data["cooldown"])
            self.assertEqual(test.get("username"), data["username"])
            self.assertEqual(test.get("max_logs"), data["max_logs"])
            self.assertEqual(test.get("auto_update"), data["auto_update"])
            self.assertEqual(test.get("testing"), data["testing"])

            self.assertEqual(test.settings_dict, data)

    def test_define_and_save(self, mock_app_data: MagicMock, mock_logs: MagicMock):
        mock_app_data.return_value = self.temp_dir
        test = settings.Settings("Test", self.valid_json)

        new_cooldown = 25
        new_name = "シュレック-史瑞克-شریک"
        new_update = False
        test.define("cooldown", new_cooldown)
        test.define("username", new_name)
        test.define("auto_update", new_update)

        self.assertEqual(test.get("cooldown"), new_cooldown)
        self.assertEqual(test.get("username"), new_name)
        self.assertEqual(test.get("auto_update"), new_update)

    def test_invalid_key(self, mock_app_data: MagicMock, mock_logs: MagicMock):
        mock_app_data.return_value = self.temp_dir
        test = settings.Settings("Test")

        with self.assertRaises(KeyError):
            test.define("bruh", True)
            test.get("bruh")


@patch("settings.setup_app_data_dir")
class UtilsTest(TestCase):
    temp_dir = create_temp_dir()

    def test_make_dir(self, mock_app_data):
        mock_app_data.return_value = self.temp_dir

        data1 = Path(self.temp_dir, "test1")
        data2 = Path(self.temp_dir, "test2")
        data3 = Path(self.temp_dir, "test3")
        os.mkdir(data2)

        settings.util._make_dir(data1)
        settings.util._make_dir(data2)

        with self.assertRaises(PermissionError) and FileLock(data3):
            settings.util._make_dir(data3)

    def test_executables(self, mock_app_data):
        mock_app_data.return_value = self.temp_dir

        exe_list = []
        download_directory = os.path.join(self.temp_dir, "updated_version")
        os.mkdir(download_directory)
        for i in range(10):
            path = os.path.join(download_directory, f"executable{i}.exe")
            with open(path, "wb") as file:
                file.write(random.randbytes(4096))
                exe_list.append(file.name)

        settings.util._clear_executables(Path(self.temp_dir))

        for exe in exe_list:
            path = os.path.join(self.temp_dir, exe)
            self.assertFalse(os.path.isfile(path))


def get_md5(path) -> str:
    with open(path, "rb") as file:
        md5 = hashlib.md5(file.read()).hexdigest()
        return md5


if __name__ == "__main__":
    main()
