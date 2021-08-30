import configparser
import logging
import os.path


class Settings:
    """This class is used so that everytime that a setting is changed it is saved on the app data folder."""
    __cooldown: str
    __max_logs: int

    def __init__(self):
        self.app_data_path = setup_app_data_dir()
        self.logs_path = self.app_data_path
        self.__config_path = os.path.join(self.app_data_path, "settings.ini")

        if os.path.exists(self.__config_path):
            config = configparser.ConfigParser()
            config.read(self.__config_path)

            handler = ConfigParserHandler(config)

            self.__cooldown = handler.try_get_config("APP", "github_username", self.__cooldown)
            self.__max_logs = int(handler.try_get_config("APP", "max_logs", self.__max_logs))

            self.save()
        else:
            self.__cooldown = 100
            self.__max_logs = 25

    @property
    def cooldown(self):
        return self.__cooldown

    @cooldown.setter
    def cooldown(self, value):
        self.__cooldown = value
        self.save()

    @property
    def max_logs(self):
        return self.__max_logs

    @max_logs.setter
    def max_logs(self, value):
        self.__max_logs = value
        self.save()

    def save(self):
        config = configparser.ConfigParser()

        if not os.path.exists(self.__config_path):
            logging.debug("Creating config file...")
            config.add_section("APP")
        else:
            config.read(self.__config_path)

        config["APP"]["github_username"] = self.github_username
        config["APP"]["max_logs"] = str(self.__max_logs)
        with open(self.__config_path, "w") as file:
            config.write(file)


class ConfigParserHandler:
    """Handles KeyErrors when getting config values, returning the original value passed if key wasn't found."""

    def __init__(self, parser: configparser.ConfigParser):
        self.__parser__ = parser

    def try_get_config(self, group, key, original_value):
        try:
            value = self.__parser__[group][key]
            return value
        except KeyError:
            return original_value


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
    path = os.path.join(os.getenv("localappdata"), "LastFMDiscordRPC")
    make_dir(path)
    return path


local_settings = Settings()
