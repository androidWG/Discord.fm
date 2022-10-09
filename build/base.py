import os
import shutil
from typing import List

from packaging.version import Version


class BuildTool:
    py_path = ""

    icon_main = ""
    icon_settings = ""

    temp_paths: List[str | os.PathLike[str]] = []

    def __init__(self, version: Version, debug: bool):
        self.version = version
        self.debug = debug
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
