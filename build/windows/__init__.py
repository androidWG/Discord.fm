import os.path
import subprocess
import time

import build.base
import process
import util


class WindowsBuildTool(build.base.PyInstallerBuildTool):
    def __init__(self, py_path, version):
        self.icon_main = r"src\resources\icon.ico"
        self.icon_settings = r"src\resources\settings.ico"

        super(WindowsBuildTool, self).__init__(py_path, version)

    def prepare_files(self):
        self.temp_ver_main_file = self._temp("file_version_main.temp")

        main_tags = [
            ("#VERSION#", self.version.base_version),
            (
                "#VERSION_TUPLE#",
                f"{self.version.major}, {self.version.minor}, {self.version.micro}, 0",
            ),
            ("#DESCRIPTION#", "Discord.fm Service Executable"),
            ("#FILENAME#", "discord_fm"),
        ]

        util.replace_instances(
            "build/windows/file_version.txt", main_tags, self.temp_ver_main_file
        )

        super().prepare_files()

    def make_installer(
        self, inno_install=r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    ):
        temp_setup_script = self._temp("inno_setup.temp")

        tags = [
            ("#VERSION#", self.version.base_version),
            ("#REPO#", os.getcwd()),
            ("#SUFFIX#", ""),
        ]
        util.replace_instances(
            "build/windows/setup.iss", tags, out_file=temp_setup_script
        )

        args = [inno_install, os.path.abspath(temp_setup_script)]

        print("Running command: ", end="")
        for arg in args:
            print(arg, end=" ")
        print("\n")

        inno = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while process.stream_process(inno):
            time.sleep(0.1)

        if inno.returncode != 0:
            raise RuntimeError("Failed to run Inno Setup")


def instance():
    return WindowsBuildTool
