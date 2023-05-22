import os.path
import shutil
import subprocess
import tarfile
import time

import yaml

import build.base
import process
import util

# from build.linux import flatpak
# from build.linux.flatpak.ordered_dumper import OrderedDumper


class LinuxBuildTool(build.base.BuildTool):
    def __init__(self, py_path, version):
        self.py_path = os.path.abspath("venv/bin/python")

        self.icon_main = "resources/icon.png"
        self.icon_settings = "resources/settings.png"

        self.temp_spec_file = self._temp("build.spec")
        super(LinuxBuildTool, self).__init__(py_path, version)

    def prepare_files(self):
        # if not os.path.isfile("build/linux/com.androidWG.Discordfm.yml"):
        #     output = self._temp("build/linux/dependencies.yaml")
        #     flatpak.make_yaml(
        #         "/home/samuel/PycharmProjects/Discord.fm/requirements.txt",
        #         "/home/samuel/PycharmProjects/Discord.fm/build/linux/linux_requirements.txt",
        #         output,
        #     )
        #
        #     with open(output, "r") as file:
        #         packages = yaml.load(file, yaml.Loader)
        #     with open("build/linux/base.yml", "r") as file:
        #         app = yaml.load(file, yaml.Loader)
        #
        #     app["modules"][6]["build-commands"] = packages["build-commands"]
        #     app["modules"][6]["sources"] = packages["sources"]
        #
        #     with open("build/linux/com.androidWG.Discordfm.yaml", "w") as file:
        #         yaml.dump(app, file, OrderedDumper)

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
        filename = f"dist/discord.fm-generic-linux64-{self.version}.tar.gz"

        print("Creating tar.gz archive")
        with tarfile.open(filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.sep)


def instance():
    return LinuxBuildTool
