import os.path
import shutil
import tarfile
from pathlib import Path

import build.base
import util


class LinuxGenericBuildTool(build.base.PyInstallerBuildTool):
    def __init__(self, py_path, version):
        self.temp_desktop_file = None
        self.icon_main = "resources/icon.png"
        self.icon_settings = "resources/settings.png"

        super(LinuxGenericBuildTool, self).__init__(py_path, version)

    def prepare_files(self):
        super().prepare_files()

        self.temp_desktop_file = self._temp("discord_fm.desktop")
        desktop_tags = [("#VERSION#", self.version.base_version)]
        util.replace_instances(
            "build/linux/discord_fm.desktop", desktop_tags, self.temp_desktop_file
        )

    def build(self):
        super().build()

        # Remove unnecessary data to decrease bloat
        shutil.rmtree("dist/discord_fm/share/icons", ignore_errors=True)

    def package(self):
        source_dir = "dist/discord_fm"
        filename = Path(f"dist/discord.fm-generic-linux64-{self.version}.tar.gz")

        print("Copying additional files")
        shutil.copy("build/linux/install.sh", source_dir)
        shutil.copy("build/linux/uninstall.sh", source_dir)
        shutil.copy(self.temp_desktop_file, source_dir)
        shutil.copy("build/linux/discord_fm.svg", source_dir)

        print("Creating tar.gz archive")
        filename.unlink(True)
        with tarfile.open(filename, "w:gz") as tar:
            print(f"Adding {source_dir}")
            tar.add(source_dir, arcname=os.path.sep)


def instance():
    return LinuxGenericBuildTool
