import logging
import os
import subprocess
import tarfile
import time
from pathlib import Path

import util
from util.install import BaseInstall

SERVICE_ABS_PATH = (
    Path("~/.config/systemd/user/discord_fm.service").expanduser().absolute()
)
APP_ID = "net.androidwg.discord_fm"

logger = logging.getLogger("discord_fm").getChild(__name__)


class LinuxInstall(BaseInstall):
    def get_executable_path(self) -> str | None:
        logger.debug("Attempting to find Windows install...")

        if util.is_running_in_flatpak():
            raise NotImplementedError
        else:
            install_path = Path("~/.local").expanduser()

        exe_path = Path(install_path, "bin/discord_fm")
        return str(exe_path) if exe_path.is_file() else None

    def get_startup(self):
        if util.is_running_in_flatpak():
            raise NotImplementedError

        result = subprocess.run(
            ["systemctl", "--user", "is-enabled", SERVICE_ABS_PATH.name],
            stdout=subprocess.PIPE,
        )
        return SERVICE_ABS_PATH.is_file() and "enabled" in result.stdout.decode("utf-8")

    def set_startup(self, new_value: bool, exe_path: str) -> bool:
        if util.is_running_in_flatpak():
            raise NotImplementedError

        shortcut_exists = self.get_startup()
        if shortcut_exists and not new_value:
            subprocess.run(["systemctl", "--user", "disable", SERVICE_ABS_PATH.name])
            os.remove(SERVICE_ABS_PATH)
            return False
        elif not shortcut_exists and new_value:
            service_path = util.resource_path("resources", "discord_fm.service")
            try:
                util.replace_instances(
                    service_path,
                    [("#EXECUTABLE_PATH#", self.get_executable_path())],
                    str(SERVICE_ABS_PATH),
                )
            except (FileNotFoundError, PermissionError) as e:
                logging.error(
                    "Received error when trying to copy service file", exc_info=e
                )

            subprocess.run(["systemctl", "--user", "enable", SERVICE_ABS_PATH.name])
            return True
        else:
            return new_value

    def install(self, installer_path: Path):
        logger.info("Installing for Linux...")

        if util.is_running_in_flatpak():
            raise NotImplementedError

        installer_folder = installer_path.parent
        tarball = tarfile.open(installer_path)
        extract_dest = installer_folder.joinpath("updated_version")

        logging.info(f'Extracting downloaded file "{tarball}"')
        tarball.extractall(extract_dest)
        tarball.close()

        install_sh_path = extract_dest.joinpath("install.sh")
        logger.debug(f"Running install.sh")
        subprocess.Popen(["sh", install_sh_path, "--self-start"], cwd=extract_dest)
        time.sleep(0.4)  # Give the installation script some time to start


def instance():
    return LinuxInstall
