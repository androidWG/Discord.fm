import os.path
import subprocess
import time

import util
import process
import base


class WindowsBuildTool(base.BuildTool):
    def __init__(self, version, debug):
        self.py_path = os.path.abspath(r"venv\Scripts\python.exe")

        self.icon_main = r"src\resources\icon.ico"
        self.icon_settings = r"src\resources\settings.ico"
        super(WindowsBuildTool, self).__init__(version, debug)

    def prepare_files(self):
        self.temp_ver_main_file = "file_version_main.temp"
        self.temp_ver_ui_file = "file_version_ui.temp"
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
            ("#VER_MAIN#", os.path.abspath(self.temp_ver_main_file)),
            ("#VER_UI#", os.path.abspath(self.temp_ver_ui_file)),
            ("#ICON_MAIN#", os.path.abspath(self.icon_main)),
            ("#ICON_UI#", os.path.abspath(self.icon_settings)),
        ]

        util.replace_instances(
            "build/windows/file_version.txt", main_tags, self.temp_ver_ui_file
        )
        util.replace_instances(
            "build/windows/file_version.txt", ui_tags, self.temp_ver_main_file
        )
        util.replace_instances("build/main.spec", spec_tags, self.temp_spec_file)

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

        if pyinstaller.returncode != 0:
            raise RuntimeError("Failed to run Pyinstaller")

    def make_installer(
        self, inno_install=r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    ):
        temp_setup_script = "inno_setup.temp"
        self.temp_files.append(temp_setup_script)

        tags = [
            ("#VERSION#", self.version.base_version),
            ("#REPO#", os.getcwd()),
            ("#SUFFIX#", "-debug" if self.debug else ""),
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

    def cleanup(self):
        super().cleanup()
        os.remove(self.temp_spec_file)
        os.remove(self.temp_ver_ui_file)
        os.remove(self.temp_ver_main_file)


def instance():
    return WindowsBuildTool
