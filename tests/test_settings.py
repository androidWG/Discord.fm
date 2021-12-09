import atexit
import hashlib
import json
import os
import random
import shutil
import settings
from filelock import FileLock
from unittest import TestCase, main
from unittest.mock import patch


def remove_temp():
    print("Removing temp folder...")
    try:
        shutil.rmtree("temp")
    except FileNotFoundError:
        pass


def create_temp_dir():
    if os.path.exists("temp"):
        shutil.rmtree("temp")

    os.mkdir("temp")
    temp_dir = os.path.abspath("temp")
    for resource in os.listdir("resources"):
        shutil.copy(os.path.join("resources", resource), temp_dir)

    atexit.register(remove_temp)
    return temp_dir


@patch("settings.setup_app_data_dir")
class SettingsClassTests(TestCase):
    temp_dir = create_temp_dir()

    not_json = "not_json.txt"
    invalid_json = "invalid_json.json"
    valid_json = "valid_json.json"
    locked_json = "locked_json.json"
    an_image = "image.gif"

    def test_read(self, mock_app_data):
        mock_app_data.return_value = self.temp_dir

        settings.Settings("Test")
        settings.Settings("Test", self.not_json)
        settings.Settings("Test", self.invalid_json)
        settings.Settings("Test", self.valid_json)
        settings.Settings("Test", self.an_image)

    def test_write(self, mock_app_data):
        mock_app_data.return_value = self.temp_dir

        path = os.path.join(self.temp_dir, self.locked_json)
        initial_md5 = get_md5(path)

        test = settings.Settings("Test")
        test.save()

        result = settings.Settings("Test", self.locked_json)
        with FileLock(self.locked_json):
            result.save()

        self.assertEqual(initial_md5, get_md5(path))

    def test_dictionary(self, mock_app_data):
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

            new_cooldown = 25
            new_username = "シュレック-史瑞克-شریک"
            new_update = False
            test.define("cooldown", new_cooldown)
            test.define("username", new_username)
            test.define("auto_update", new_update)

            self.assertEqual(test.get("cooldown"), new_cooldown)
            self.assertEqual(test.get("username"), new_username)
            self.assertEqual(test.get("auto_update"), new_update)


@patch("settings.setup_app_data_dir")
class UtilsTest(TestCase):
    temp_dir = create_temp_dir()

    def test_make_dir(self, mock_app_data):
        mock_app_data.return_value = self.temp_dir

        data1 = os.path.join(self.temp_dir, "test1")
        data2 = os.path.join(self.temp_dir, "test2")
        data3 = os.path.join(self.temp_dir, "test3")
        os.mkdir(data2)

        settings.make_dir(data1)
        settings.make_dir(data2)

        with self.assertRaises(PermissionError) and FileLock(data3):
            settings.make_dir(data3)

    def test_executables(self, mock_app_data):
        mock_app_data.return_value = self.temp_dir

        exe_list = []
        for i in range(10):
            path = os.path.join(self.temp_dir, f"executable{i}.exe")
            with open(path, "wb") as file:
                file.write(random.randbytes(4096))
                exe_list.append(file.name)

        settings.clear_executables(self.temp_dir)

        for exe in exe_list:
            path = os.path.join(self.temp_dir, exe)
            self.assertFalse(os.path.isfile(path))


def get_md5(path) -> str:
    file = open(path, "rb")
    md5 = hashlib.md5(file.read()).hexdigest()
    file.close()
    return md5


if __name__ == '__main__':
    main()
