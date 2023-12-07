import json
import subprocess
import sys
import xml.etree.ElementTree
from datetime import datetime

from build.base import BuildTool
from build.flatpak import requirements

APP_ID = "net.androidwg.discord_fm"


class FlatpakBuildTool(BuildTool):
    def prepare_files(self):
        dependencies = self._temp("build/flatpak/dependencies.json")
        requirements.make_yaml("build/flatpak/requirements.txt", dependencies)

        with open(dependencies, "r") as file:
            packages = json.load(file)
        with open(f"build/flatpak/{APP_ID}.json", "r") as file:
            app = json.load(file)

        app["modules"][0]["build-commands"] = packages["build-commands"]
        app["modules"][0]["sources"] = packages["sources"]

        manifest = self._temp("build/flatpak/output.json")
        with open(manifest, "w") as file:
            json.dump(app, file, indent=2)

        et = xml.etree.ElementTree.parse(f"build/flatpak/metainfo.xml")
        releases = et.find("releases").find("release")
        releases.set("version", self.version.base_version)
        releases.set("date", datetime.today().strftime("%Y-%m-%d"))

        metainfo = self._temp(f"build/flatpak/{APP_ID}.metainfo.xml")
        et.write(metainfo)

    def build(self):
        commands = [
            "flatpak-builder",
            "dist/flatpak",
            "build/flatpak/output.json",
            "--force-clean",
            "--user",
            "--install",
        ]  # TODO: Change out of --user --install and add exporting to repo
        subprocess.run(commands, stdout=sys.stdout, stderr=sys.stderr)


def instance():
    return FlatpakBuildTool
