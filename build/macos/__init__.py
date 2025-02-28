import subprocess
import time

import build.base
import src.process as process


class DarwinBuildTool(build.base.PyInstallerBuildTool):
    def __init__(self, py_path, version):
        self.temp_spec_file = None
        super(DarwinBuildTool, self).__init__(py_path, version)

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
