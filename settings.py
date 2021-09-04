import json
import logging
import os.path


def make_dir(path: str):
    print(f"Path chosen for app data: {path}")
    try:
        os.mkdir(path)
        print("Created dir")
    except FileExistsError:
        pass


def setup_app_data_dir() -> str:
    """Gets the folder where to store log files.

    :return: Path to logs folder.
    :rtype: str
    """
    path = os.path.join(os.getenv("localappdata"), "Discord.fm")
    make_dir(path)
    return path


def save():
    json_string = json.dumps(__settings_dict, indent=4)

    with open(config_path, "w") as file:
        file.write(json_string)


app_data_path = setup_app_data_dir()
logs_path = app_data_path
config_path = os.path.join(app_data_path, "settings.json")

__settings_dict = {  # Put default setting values here
        "cooldown": 2,
        "username": "andodide",
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
except FileNotFoundError:
    save()


def get(name):
    logging.debug(f"Getting {name} setting")
    return __settings_dict[name]


def get_dict():
    return __settings_dict


def define(name, value):
    if __settings_dict.keys().__contains__(name):
        logging.debug(f"Setting value of {name} setting to {value}")
        __settings_dict[name] = value
        save()
    else:
        raise KeyError("Key not found in settings dictionary")
