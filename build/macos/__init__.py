import os.path
import subprocess
import time

import build.base
import src.process as process
import util


class DarwinBuildTool(build.base.BuildTool):
    def __init__(self, version):
        self.py_path = os.path.abspath(r"venv/bin/python")
        self.temp_spec_file = self._temp("temp_spec.spec")
        super(DarwinBuildTool, self).__init__(version)

    def prepare_files(self):
        tags = [("#VERSION#", f"'{self.version.base_version}'")]

        util.replace_instances(
            "build/macos/mac.spec", tags, out_file=self.temp_spec_file
        )

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


def instance():
    return DarwinBuildTool
