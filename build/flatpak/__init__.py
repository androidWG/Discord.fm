import json
import subprocess
import sys

from build.base import BuildTool
from build.flatpak import requirements


class FlatpakBuildTool(BuildTool):
    def prepare_files(self):
        output = self._temp("build/flatpak/dependencies.json")
        requirements.make_yaml("build/flatpak/requirements.txt", output)

        with open(output, "r") as file:
            packages = json.load(file)
        with open("build/flatpak/base.json", "r") as file:
            app = json.load(file)

        app["modules"][0]["build-commands"] = packages["build-commands"]
        app["modules"][0]["sources"] = packages["sources"]

        with open("build/flatpak/output.json", "w") as file:
            json.dump(app, file, indent=2)

    # def build(self):
    #     commands = [
    #         "flatpak-builder",
    #         "dist/flatpak",
    #         "build/flatpak/output.json",
    #         "--force-clean",
    #     ]
    #     subprocess.run(commands, stdout=sys.stdout, stderr=sys.stderr)


def instance():
    return FlatpakBuildTool
