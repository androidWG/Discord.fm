import logging
import os.path
import zipfile
import plistlib
import stat
import util.timeout
from shutil import copytree


def get_app_version(app_path: str) -> tuple:
    """Gets the version and install path of Discord.fm with the provided .app path.

    :param app_path: Path to .app of Discord.fm
    :type app_path: str
    :return: Tuple with installation path an version string respectively. If an installation is not found, a tuple of
    None and None are returned.
    :rtype: tuple
    """
    if os.path.exists(app_path):
        with open(os.path.join(app_path, "Contents/Info.plist"), "rb") as file:
            plist = plistlib.load(file)
            # Returns app_path back to fit with Windows' "get_install_folder_and_version()"
            return app_path, plist["CFBundleShortVersionString"]
    else:
        logging.warning("Discord.fm installation not found")
        return None, None


@util.timeout.exit_after(180)
def copy_to_applications(temp_dir: str, installer_path: str):
    """Copies the .app folder from the downloaded Zip to the /Applications folder.

    :param temp_dir: Temporary directory to be used
    :type temp_dir: str
    :param installer_path: Path where the .zip containing the .app folder is located
    :type installer_path: str
    """
    logging.info("Installing for macOS...")

    zip_path = os.path.join(temp_dir, installer_path)
    with zipfile.ZipFile(zip_path, "r") as downloaded_zip:
        downloaded_zip.extractall(temp_dir)
        logging.debug("Extracted Discord.fm.app")

        # For some reason zipfile extracts the main executable inside the .app as a
        # non-executable file, so we need to manually do that
        main_executable = os.path.join(temp_dir, "Discord.fm.app/Contents/MacOS/Discord.fm")
        st = os.stat(main_executable)
        os.chmod(main_executable, st.st_mode | stat.S_IEXEC)
        logging.debug("Made Discord.fm file executable")

        copytree(os.path.join(temp_dir, "Discord.fm.app"), "/Applications/Discord.fm.app", symlinks=True)
        logging.debug("Copied to Applications")
