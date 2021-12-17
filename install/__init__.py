import os
import platform
from install import windows
from install import macos


def get_install_folder(windows_exe_name: str, macos_app_name: str):
    if platform.system() == "Windows":
        path = windows.get_install_folder_and_version()[0]
        if path is None:
            return ""
        else:
            return [os.path.join(path, windows_exe_name)]
    elif platform.system() == "Darwin":
        return macos.get_app_folder_and_version(macos_app_name)[0]
    else:
        raise NotImplementedError
