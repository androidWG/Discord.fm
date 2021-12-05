import json
import os.path
from platform import system

__version = "0.4.0"


class Settings:
    def __init__(self, app_name, settings_filename="settings.json"):
        self.app_data_path = setup_app_data_dir(app_name)
        self.logs_path = setup_logs_dir(app_name)
        self.config_path = os.path.join(self.app_data_path, settings_filename)

        self.__settings_dict = {  # Put default setting values here
            "cooldown": 4,
            "username": "",
            "max_logs": 10,
            "auto_update": True
        }

        try:
            with open(self.config_path) as file:
                loaded_dict = json.load(file)
                for s in self.__settings_dict.keys():
                    if not loaded_dict.keys().__contains__(s):
                        loaded_dict[s] = self.__settings_dict[s]

                self.__settings_dict = loaded_dict

            self.first_load = False
        except (FileNotFoundError, json.decoder.JSONDecodeError,):
            self.save()
            self.first_load = True

    def save(self):
        """Saves the settings dictionary as a JSON in a file specified by config_path."""
        json_string = json.dumps(self.__settings_dict, indent=4)

        try:
            with open(self.config_path, "w") as f:
                f.write(json_string)
        except PermissionError as e:
            print("Permission denied while attempting to save settings file")

    def define(self, name: str, value: any):
        """Set a setting and save it to the settings file.

        :param name: Name of the key for the setting.
        :type name: str
        :param value: Value to set the setting to.
        :type value: any
        """
        if self.__settings_dict.keys().__contains__(name):
            print(f"Setting value of \"{name}\" setting to \"{value}\"")
            self.__settings_dict[name] = value
            self.save()
        else:
            raise KeyError(f"Key \"{name}\" not found in settings dictionary")

    def get(self, name: str) -> any:
        """Get a setting from it's key name.

        :param name: Name of key for the setting.
        :type name: str
        :return: The value of the setting. Return type is the same as the one in the parsed JSON file.
        :rtype: any
        """
        print(f"Getting {name} setting")
        return self.__settings_dict[name]

    @property
    def settings_dict(self):
        """Get settings dictionary with all settings.

        :return: Settings dictionary.
        :rtype: dict
        """
        return self.__settings_dict


def make_dir(path: str):
    """Creates a directory specified in path if it doesn't exist, ignoring it if it does.

    :param path: Path of the directory to be created.
    :type path: str
    """
    try:
        os.mkdir(path)
        print(f"Creating folder \"{path}\"")
    except FileExistsError:
        pass
    except PermissionError as e:
        print(f"Unable to create application dir \"{path}\"!")


def setup_app_data_dir(folder_name: str) -> str:
    """Gets the folder where to store log files.

    :param folder_name: Name of the folder to create inside the system's app data directory.
    :type folder_name: str
    :return: Path to logs folder.
    :rtype: str
    """
    current_platform = system()

    if current_platform == "Windows":
        path = os.path.join(os.getenv("appdata"), folder_name)
        make_dir(path)
        return path
    elif current_platform == "Darwin":
        path = os.path.join(os.path.expanduser("~/Library/Application Support"), folder_name)
        make_dir(path)
        return path
    else:
        raise NotImplementedError("Linux is currently unsupported")


def setup_logs_dir(folder_name: str) -> str:
    """Gets the folder where to store log files based on OS.

    :param folder_name: Name of the folder to create inside the system's logs directory (for Windows, it will be the
    same as app data directory)
    :type folder_name: str
    :return: Path to logs folder.
    :rtype: str
    """
    current_platform = system()

    if current_platform == "Windows":
        path = os.path.join(os.getenv("appdata"), folder_name)
        make_dir(path)
        return path
    elif current_platform == "Darwin":
        path = os.path.join(os.path.expanduser("~/Library/Logs"), folder_name)
        make_dir(path)
        return path
    else:
        raise NotImplementedError("Linux is currently unsupported")


local_settings = Settings("Discord.fm")
