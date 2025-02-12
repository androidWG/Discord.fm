import subprocess
import time

import build.base
import src.process as process
import util


class DarwinBuildTool(build.base.BuildTool):
    def __init__(self, py_path, version):
        self.temp_spec_file = None
        super(DarwinBuildTool, self).__init__(py_path, version)

    def prepare_files(self):
        self.temp_spec_file = self._temp("temp_spec.spec")
        tags = [("#VER_MAIN#", f"'{self.version.base_version}'")]

        util.replace_instances("build/main.spec", tags, out_file=self.temp_spec_file)

    def build(self):
        temp_folder = "pyinstaller_temp"
        self._temp(f"{temp_folder}/")

        main_args = [
            self.temp_spec_file,
            f"--workpath={temp_folder}",
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

    def package(self):
        command = [
            "appdmg",
            "build/macos/appdmg_specs.json",
            f"dist/discord.fm-macos-{self.version.base_version}.dmg",
        ]

        appdmg = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        while process.stream_process(appdmg):
            time.sleep(0.2)


def instance():
    return DarwinBuildTool
