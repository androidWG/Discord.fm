import os
from platform import system


def make_dir(path: str):
    """Creates a directory specified in path if it doesn't exist, ignoring it if it does.

    :param path: Path of the directory to be created.
    :type path: str
    """
    try:
        os.mkdir(path)
        print(f'Created folder "{path}"')
    except FileExistsError:
        print(f'Folder "{path}" already exists')


def clear_executables(app_data_path: str):
    """Removes all executable files leftover from previous updates.

    :param app_data_path: Path of the app data directory containing the files
    :type app_data_path: str
    """
    for file in os.listdir(app_data_path):
        if file.endswith(".exe"):
            print(f"Removing leftover update file {file}")
            os.remove(os.path.join(app_data_path, file))


def setup_app_data_dir(folder_name: str) -> str:
    """Gets the folder where to store log files.

    :param folder_name: Name of the folder to create inside the system's app data directory.
    :type folder_name: str
    :return: Path to logs folder.
    :rtype: str
    """
    current_platform = system()

    if current_platform == "Windows":
        # Here it's AppData NOT LocalAppData, since settings should always be present for the user
        path = os.path.join(os.getenv("appdata"), folder_name)
    elif current_platform == "Darwin":
        path = os.path.join(
            os.path.expanduser("~/Library/Application Support"), folder_name
        )
    else:
        path = os.path.expanduser(f"~/.{folder_name.replace('.', '_').lower()}")

    make_dir(path)
    clear_executables(path)
    return path


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
        # And here it's LocalAppData NOT AppData, since logs can occupy a lot of space and are not needed by the app
        path = os.path.join(os.getenv("localappdata"), folder_name)
    elif current_platform == "Darwin":
        path = os.path.join(os.path.expanduser("~/Library/Logs"), folder_name)
    else:
        path = os.path.expanduser(f"~/.{folder_name.replace('.', '_').lower()}")

    make_dir(path)
    return path
