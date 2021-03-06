import os
import platform
import subprocess
import tempfile
import package_build
import sys
from time import sleep
from util.process import stream_process

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import util
from settings import get_version, get_debug


def make_windows_installer(version: str):
    """Runs ISCC located at ``C:\\Program Files (x86)\\Inno Setup 6`` to build Windows installer, based on the .iss
    file located inside the build folder.

    :param version: Version of the package formatted like 0.0.0
    :type version: str
    """
    print("\nStarted building Windows installer")
    temp_setup_script = "inno_setup.temp"

    tags = [
        ("#VERSION#", version),
        ("#REPO#", os.getcwd()),
        ("#SUFFIX#", "-debug" if get_debug() else "")
    ]
    util.replace_instances("build/setup.iss", tags, out_file=temp_setup_script)

    args = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        temp_setup_script
    ]

    print("Running command: ", end="")
    for arg in args:
        print(arg, end=" ")
    print("\n")

    inno = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while stream_process(inno):
        sleep(0.1)
    print(f"ISCC finished with return code {inno.returncode}")

    os.remove(temp_setup_script)
    print("Removed temp files")


def make_macos_installer(version: str):
    """Uses `package_build` to make a package installer for macOS, using resource files from the `darwin` folder inside
    the build folder.

    :param version: Version of the package formatted like 0.0.0
    :type version: str
    """
    print("\nStarted building macOS installer")

    info = package_build.PackageInfo(
        name="Discord.fm",
        version=version,
        package="com.androidwg.Discord_fm",
        install_location="/Library/Discord.fm"
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        package_build.copy_darwin_directory(info, temp_dir)

        files = [
            "dist/Corkscrew",
            os.path.join(temp_dir, "darwin/resources/com.androidwg.corkscrew.plist"),
            os.path.join(temp_dir, "darwin/resources/uninstall.sh")
        ]

        distribution = os.path.join(temp_dir, "darwin/distribution.plist")
        resources_path = os.path.join(temp_dir, "darwin/resources")
        packages_path = os.path.join(temp_dir, "package")

        package_build.create_package(info, files, temp_dir)
        package_build.create_product_installer(info, distribution, resources_path, packages_path, temp_dir)


if __name__ == "__main__":
    if platform.system() == "Windows":
        make_windows_installer(get_version())
        sys.exit()
    elif platform.system() == "Darwin":
        make_macos_installer(get_version())
        sys.exit()
