import os

import yaml

from build.base import BuildTool
from build.flatpak import requirements
from build.flatpak.ordered_dumper import OrderedDumper


class FlatpakBuildTool(BuildTool):
    def prepare_files(self):
        if not os.path.isfile("build/linux/com.androidWG.Discordfm.yml"):
            output = self._temp("build/linux/dependencies.yaml")
            requirements.make_yaml(
                "/home/samuel/PycharmProjects/Discord.fm/requirements.txt",
                "/home/samuel/PycharmProjects/Discord.fm/build/linux/linux_requirements.txt",
                output,
            )

            with open(output, "r") as file:
                packages = yaml.load(file, yaml.Loader)
            with open("build/linux/base.yml", "r") as file:
                app = yaml.load(file, yaml.Loader)

            app["modules"][6]["build-commands"] = packages["build-commands"]
            app["modules"][6]["sources"] = packages["sources"]

            with open("build/flatpak/base.yaml", "w") as file:
                yaml.dump(app, file, OrderedDumper)


def instance():
    return FlatpakBuildTool
