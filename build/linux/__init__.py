import os.path

import yaml

import build.base
from build.linux import flatpak
from build.linux.ordered_dumper import OrderedDumper


class LinuxBuildTool(build.base.BuildTool):
    def __init__(self, version):
        self.py_path = os.path.abspath("venv/bin/python")

        self.icon_main = "resources/icon.png"
        self.icon_settings = "resources/settings.png"
        super(LinuxBuildTool, self).__init__(version)

    def prepare_files(self):
        if not os.path.isfile("build/linux/com.androidWG.Discordfm.yml"):
            output = self._temp("build/linux/dependencies.yaml")
            flatpak.make_yaml(
                "/home/samuel/PycharmProjects/Discord.fm/requirements.txt",
                "/home/samuel/PycharmProjects/Discord.fm/build/linux/linux_requirements.txt",
                output,
            )

            with open(output, "r") as file:
                packages = yaml.load(file, yaml.Loader)
            with open("build/linux/base.yml", "r") as file:
                app = yaml.load(file, yaml.Loader)

            app["modules"][1]["build-commands"] = packages["build-commands"]
            app["modules"][1]["sources"] = packages["sources"]

            with open("build/linux/com.androidWG.Discordfm.yaml", "w") as file:
                yaml.dump(app, file, OrderedDumper)

    def build(self):
        # main_args = [
        #     self.temp_spec_file,
        #     "--workpath=pyinstaller_temp",
        #     "--upx-dir=upx/",
        #     "-y",
        # ]
        #
        # pyinstaller = subprocess.Popen(
        #     " ".join(self.run_command + main_args),
        #     shell=True,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.STDOUT,
        # )
        # while process.stream_process(pyinstaller):
        #     time.sleep(0.2)
        pass


def instance():
    return LinuxBuildTool
