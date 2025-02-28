import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import List

from packaging.version import Version

import process
import util


class BuildTool:
    """
    Base class for a standardized build system, divided in four steps: preparing files, building, making an
    installer, and cleaning up temporary files and folders.

    The `temp_paths` parameter holds the paths of any files or folders that should be deleted during cleanup. Using
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

    temp_folder = "build_temp"
    temp_paths: List[Path] = [Path(temp_folder).absolute()]

    # TODO: Add support for custom runner instead of Popen (such as setup.py's _run command)
    def __init__(self, py_path: str, version: Version):
        self.version = version
        self.py_path = py_path
        self.run_command = [f"{self.py_path} -O -m PyInstaller"]

    def _temp(self, value: str, no_subfolder: bool = False) -> str:
        if no_subfolder:
            path = Path(value)
            self.temp_paths.append(path)
        else:
            path = Path(self.temp_folder, value)
            path.parent.mkdir(parents=True, exist_ok=True)
        return str(path.absolute())

    def prepare_files(self):
        pass

    def build(self):
        pass

    def package(self):
        pass

    def make_installer(self):
        pass

    def cleanup(self):
        """Removes temporary files."""
        for p in self.temp_paths:
            if p.is_dir():
                try:
                    shutil.rmtree(p)
                except FileNotFoundError:
                    print(f'Folder "{p}" was not found!')
            elif p.is_file():
                try:
                    p.unlink()
                except FileNotFoundError:
                    print(f'File "{p}" was not found!')
            else:
                raise ValueError("Not a valid path")


class PyInstallerBuildTool(BuildTool):
    """
    Generic class for PyInstaller based build tools.
    """

    def __init__(self, py_path: str, version: Version):
        super().__init__(py_path, version)
        self.temp_ver_main_file = None
        self.temp_spec_file = None

    def prepare_files(self):
        self.temp_spec_file = self._temp("build.spec", no_subfolder=True)

        spec_tags = [
            (
                "#VERSION_FILE#",
                (
                    os.path.abspath(self.temp_ver_main_file)
                    if self.temp_ver_main_file
                    else ""
                ),
            ),
            ("#VERSION#", self.version.base_version),
            ("#ICON_MAIN#", os.path.abspath(self.icon_main)),
        ]

        util.replace_instances("build/main.spec", spec_tags, self.temp_spec_file)

    def build(self):
        work_path = "pyinstaller_temp"
        self._temp(work_path)

        main_args = [
            self.temp_spec_file,
            f"--workpath={work_path}",
            "--upx-dir=upx/",
            "-y",
        ]

        pyinstaller = subprocess.Popen(
            " ".join(self.run_command + main_args),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        while process.stream_process(pyinstaller):
            time.sleep(0.2)

        if pyinstaller.returncode != 0:
            raise RuntimeError("Failed to run Pyinstaller")
