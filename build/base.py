import os
import shutil

from packaging.version import Version


class BuildTool:
    py_path = ""

    icon_main = ""
    icon_settings = ""

    temp_files = []

    def __init__(self, version: Version, debug: bool):
        self.version = version
        self.debug = debug
        self.run_command = [f"{self.py_path} -O -m PyInstaller"]

    def prepare_files(self):
        pass

    def build(self):
        pass

    def make_installer(self):
        pass

    def cleanup(self):
        """Removes temporary files."""
        try:
            shutil.rmtree("pyinstaller_temp")
        except FileNotFoundError:
            print("Temp pyinstaller dir doesn't exist")

        for f in self.temp_files:
            try:
                os.remove(f)
            except FileNotFoundError:
                print(f'Temp file set to be deleted named "{f}" not found!')
