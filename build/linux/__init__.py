import os.path
import shutil
import subprocess
import tarfile
import time
from pathlib import Path

import build.base
import process
import util


class LinuxGenericBuildTool(build.base.BuildTool):
    def __init__(self, py_path, version):
        self.temp_spec_file = None
        self.icon_main = "resources/icon.png"
        self.icon_settings = "resources/settings.png"

        super(LinuxGenericBuildTool, self).__init__(py_path, version)

    def prepare_files(self):
        self.temp_spec_file = self._temp("build.spec")

        spec_tags = [
            ("#VER_MAIN#", "/usr"),
            ("#ICON_MAIN#", os.path.abspath(self.icon_main)),
        ]

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

        # Remove unnecessary data to decrease bloat
        shutil.rmtree("dist/discord_fm/share/icons", ignore_errors=True)

    def package(self):
        source_dir = "dist/discord_fm"
        filename = Path(f"dist/discord.fm-generic-linux64-{self.version}.tar.gz")

        print("Copying additional files")
        shutil.copy("build/linux/install.sh", source_dir)
        shutil.copy("build/linux/uninstall.sh", source_dir)
        shutil.copy("build/linux/discord_fm.desktop", source_dir)
        shutil.copy("build/linux/discord_fm.svg", source_dir)

        print("Creating tar.gz archive")
        filename.unlink(True)
        with tarfile.open(filename, "w:gz") as tar:
            print(f"Adding {source_dir}")
            tar.add(source_dir, arcname=os.path.sep)


def instance():
    return LinuxGenericBuildTool
