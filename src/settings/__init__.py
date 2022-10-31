import json
import logging
import os
import urllib.parse

from settings.util import setup_app_data_dir, setup_logs_dir


logger = logging.getLogger("discord_fm").getChild(__name__)


class Settings:
    def __init__(self, app_name, settings_filename="settings.json"):
        self.app_data_path = setup_app_data_dir(app_name)
        self.logs_path = setup_logs_dir(app_name)
        self.config_file_path = os.path.join(self.app_data_path, settings_filename)

        self.__settings_dict = {}
        self.load()

    def load(self):
        self.__settings_dict = {  # Put default setting values here
            "debug": False,
            "cooldown": 4,
            "username": "",
            "max_logs": 5,
            "start_with_system": True,
            "auto_update": True,
            "pre_releases": False,
        }

        try:
            with open(self.config_file_path) as file:
                loaded_dict = json.load(file)
                for s in self.__settings_dict.keys():
                    if not loaded_dict.keys().__contains__(s):
                        loaded_dict[s] = self.__settings_dict[s]

                self.__settings_dict = loaded_dict
        except (FileNotFoundError, json.decoder.JSONDecodeError, UnicodeDecodeError):
            self.save()

    def save(self):
        """Saves the settings dictionary as a JSON in a file specified by config_path."""
        json_string = json.dumps(self.__settings_dict, indent=4)

        try:
            with open(self.config_file_path, "w") as f:
                f.write(json_string)
        except PermissionError as e:
            logger.error("Permission denied while attempting to save settings file", exc_info=e)

    def define(self, name: str, value: any):
        """Set a setting and save it to the settings file.

        :param name: Name of the key for the setting.
        :type name: str
        :param value: Value to set the setting to.
        :type value: any
        """
        if self.__settings_dict.keys().__contains__(name):
            logger.debug(
                f'Setting value of "{name}" setting to "{urllib.parse.quote(str(value).encode("utf-8"))}"'
            )
            self.__settings_dict[name] = value
            self.save()
        else:
            raise KeyError(f'Key "{name}" not found in settings dictionary')

    def get(self, name: str) -> any:
        """Get a setting from its key name.

        :param name: Name of key for the setting.
        :type name: str
        :return: The value of the setting. Return type is the same as the one in the parsed JSON file.
        :rtype: any
        """
        logger.debug(f"Getting {name} setting")
        return self.__settings_dict[name]

    @property
    def settings_dict(self):
        """Get settings dictionary with all settings.

        :return: Settings dictionary.
        :rtype: dict
        """
        return self.__settings_dict
