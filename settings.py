import json
import logging
import os.path
from platform import system


def make_dir(path: str):
    print(f"Path chosen for app data: {path}")
    try:
        os.mkdir(path)
        print("Created dir")
    except FileExistsError:
        pass
    except PermissionError as e:
        logging.error(f"Unable to create application dir \"{path}\"!", exc_info=e)


def setup_app_data_dir() -> str:
    """Gets the folder where to store log files.

    :return: Path to logs folder.
    :rtype: str
    """
    current_platform = system()

    if current_platform == "Windows":
        path = os.path.join(os.getenv("localappdata"), "Corkscrew")
        make_dir(path)
        return path
    elif current_platform == "Darwin":
        path = os.path.join(os.path.expanduser("~/Library/Application Support"), "Corkscrew")
        make_dir(path)
        return path
    else:
        raise NotImplementedError("Linux is currently unsupported")


def setup_logs_dir() -> str:
    """Gets the folder where to store log files based on OS.

    :return: Path to logs folder.
    :rtype: str
    """
    current_platform = system()

    if current_platform == "Windows":
        path = os.path.join(os.getenv("localappdata"), "Corkscrew")
        make_dir(path)
        return path
    elif current_platform == "Darwin":
        path = os.path.join(os.path.expanduser("~/Library/Logs"), "Corkscrew")
        make_dir(path)
        return path
    else:
        raise NotImplementedError("Linux is currently unsupported")


def save(path):
    """Saves the settings dictionary as a JSON in a file specified by config_path.

    :type path: str
    """
    json_string = json.dumps(__settings_dict, indent=4)

    try:
        with open(path, "w") as f:
            f.write(json_string)
    except PermissionError as e:
        logging.error("Permission denied while attempting to save settings file!", exc_info=e)


app_data_path = setup_app_data_dir()
logs_path = setup_logs_dir()
config_path = os.path.join(app_data_path, "settings.json")

__settings_dict = {  # Put default setting values here
    "cooldown": 2,
    "username": "",
    "max_logs": 10,
    "tray_icon": True,
    "auto_update": True
}

try:
    with open(config_path) as file:
        loaded_dict = json.load(file)
        for s in __settings_dict.keys():
            if not loaded_dict.keys().__contains__(s):
                loaded_dict[s] = __settings_dict[s]

        __settings_dict = loaded_dict
except (FileNotFoundError, json.decoder.JSONDecodeError,):
    save(config_path)


def get(name):
    logging.debug(f"Getting {name} setting")
    return __settings_dict[name]


def get_dict():
    return __settings_dict


def define(name, value):
    if __settings_dict.keys().__contains__(name):
        logging.debug(f"Setting value of {name} setting to {value}")
        __settings_dict[name] = value
        save(config_path)
    else:
        raise KeyError("Key not found in settings dictionary")
