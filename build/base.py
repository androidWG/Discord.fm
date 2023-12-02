import os
import shutil
from typing import List

from packaging.version import Version


class BuildTool:
    """
    Base class for a standardized build system, divided in three steps: preparing files, building, making an
    installer, and cleaning up temporary files and folders.

    The `temp_paths` parameter holds the paths of any files or fodlers that should be deleted during cleanup. Using
    the `_temp` method, you can easily set a variable to a string and at the same time append it to the `temp_paths`
    parameter. Example::
        temp_file = _temp("path/to/file.txt")
        # Is equivalent to...
        temp_file = "path/to/file.txt"
        self.temp_paths.append("path/to/file.txt")

    `py_path` needs to be set to a valid path before `super().__init__()` is called.
    """

    icon_main = ""
    icon_settings = ""

    temp_paths: List[str | os.PathLike[str]] = []

    def __init__(self, py_path: str, version: Version):
        self.version = version
        self.py_path = py_path
        self.run_command = [f"{self.py_path} -O -m PyInstaller"]

    def _temp(self, value: str | os.PathLike[str]) -> str | os.PathLike[str]:
        self.temp_paths.append(os.path.abspath(value))
        return value

    def prepare_files(self):
        pass

    def build(self):
        pass

    def make_installer(self):
        pass

    def cleanup(self):
        """Removes temporary files."""
        for f in self.temp_paths:
            if os.path.isdir(f):
                try:
                    shutil.rmtree(f)
                except FileNotFoundError:
                    print(f'Folder "{f}" was not found!')
            elif os.path.isfile(f):
                try:
                    os.remove(f)
                except FileNotFoundError:
                    print(f'File "{f}" was not found!')
            else:
                raise ValueError("Not a valid path")
