import os.path
import subprocess
import time

import src.process as process
import util
from build.base import BuildTool


class LinuxBuildTool(BuildTool):
    def __init__(self, version, debug):
        self.py_path = os.path.abspath("venv/bin/python")

        self.icon_main = "resources/icon.png"
        self.icon_settings = "resources/settings.png"
        super(LinuxBuildTool, self).__init__(version, debug)

    def prepare_files(self):
        self.temp_spec_file = "build.spec"

        main_tags = [
            ("#VERSION#", self.version.base_version),
            (
                "#VERSION_TUPLE#",
                f"{self.version.major}, {self.version.minor}, {self.version.micro}, 0",
            ),
            ("#DESCRIPTION#", "Discord.fm Service Executable"),
            ("#FILENAME#", "discord_fm"),
        ]
        ui_tags = main_tags
        ui_tags[2] = ("#DESCRIPTION#", "Discord.fm Settings UI")
        ui_tags[3] = ("#FILENAME#", "settings_ui")

        spec_tags = [
            ("#VER_MAIN#", ""),
            ("#VER_UI#", ""),
            ("#ICON_MAIN#", self.icon_main),
            ("#ICON_UI#", self.icon_settings),
        ]

        util.replace_instances(
            "build/main.spec", spec_tags, self.temp_spec_file
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

    def make_installer(self):
        pass

    def cleanup(self):
        super().cleanup()
        os.remove(self.temp_spec_file)


def instance():
    return LinuxBuildTool
