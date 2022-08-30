import os.path
import subprocess
import time

import util
import src.process as process
from build.base import BuildTool


class DarwinBuildTool(BuildTool):
    def __init__(self, version, debug):
        self.py_path = os.path.abspath(r"venv/bin/python")
        super(DarwinBuildTool, self).__init__(version, debug)

    def prepare_files(self):
        self.temp_spec_file = "temp_spec.spec"
        tags = [
            ("#VERSION#", f"'{self.version.base_version}'")
        ]

        util.replace_instances("build/macos/mac.spec", tags, out_file=self.temp_spec_file)

    def build(self):
        main_args = [
            self.temp_spec_file,
            "--workpath=pyinstaller_temp",
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

    def make_installer(
            self, inno_install=r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    ):
        pass

    def cleanup(self):
        super().cleanup()
        os.remove(self.temp_spec_file)


def instance():
    return DarwinBuildTool
