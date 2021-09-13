# This script is based on https://github.com/KosalaHerath/macos-installer-builder
import os
import shutil
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util import replace_instances


class PackageInfo:
    __name: str
    __version: str
    __package: str
    __install_location: str

    def __init__(self, name: str, version: str, package: str, install_location: str):
        """Holds information about a package in read-only string type attributes.

        :param name: Package name
        :type name: str
        :param version: Version of the package formatted like 0.0.0
        :type version: str
        :param package: Inverted domain name of package
        :type package: str
        :param install_location: Location that the package will be installed in
        :type install_location: str
        """
        self.__name = name
        self.__version = version
        self.__package = package
        self.__install_location = install_location

    @property
    def name(self):
        return self.__name

    @property
    def version(self):
        return self.__version

    @property
    def package(self):
        return self.__package

    @property
    def install_location(self):
        return self.__install_location


def create_package(info: PackageInfo, files: list, temp_dir: str) -> str:
    """Creates a component package inside the package folder and returns its location as a string.

    :param info: PackageInfo object
    :type info: PackageInfo
    :param files: Paths for all files that will be included in the package as a list
    :type files: list
    :param temp_dir: Temporary directory to be used
    :type temp_dir: str
    :return: Path of created package
    :rtype: str
    """
    package_path = os.path.join(temp_dir, f"package/{info.name}.pkg")

    bundles_dir = os.path.join(temp_dir, "bundles")
    os.mkdir(bundles_dir)
    for f in files:
        shutil.copy(f, os.path.join(bundles_dir, os.path.basename(f)))

    pkgbuild_args = [
        "pkgbuild",
        "--root", bundles_dir,
        "--identifier", info.package,
        "--version", info.version,
        "--scripts", os.path.join(temp_dir, "darwin/scripts"),
        "--install-location", info.install_location,
        package_path
    ]

    print("Running command: ", end="")
    for arg in pkgbuild_args:
        print(arg, end=" ")
    print("\n")

    pkgbuild = subprocess.Popen(pkgbuild_args, stdout=subprocess.PIPE)
    pkgbuild.wait()

    return package_path


def create_product_installer(info: PackageInfo, distribution: str, resources: str, packages: str, temp_dir: str) -> str:
    """Creates product installer using productbuild.

    :param info: PackageInfo object
    :type info: PackageInfo
    :param distribution: Distribution to use
    :type distribution: str
    :param resources: Path to resources folder to be packed in installer
    :type resources: str
    :param packages: Path to packages folder that the installer will install
    :type packages: str
    :param temp_dir: Temporary directory to be used
    :type temp_dir: str
    :return: Path of created installer
    :rtype: str
    """
    product_path = f"dist/{info.name.lower()}-macos-x64-{info.version}.pkg"

    productbuild_args = [
        "productbuild",
        "--distribution", distribution,
        "--resources", resources,
        "--package-path", packages,
        product_path
    ]

    print("Running command: ", end="")
    for arg in productbuild_args:
        print(arg, end=" ")
    print("\n")

    productbuild = subprocess.Popen(productbuild_args, stdout=subprocess.PIPE)
    productbuild.wait()

    return product_path


def copy_darwin_directory(info: PackageInfo, temp_dir: str):
    """Prepares build directory, copying from [repo_root]/build/darwin to a temp folder.

        :param info: PackageInfo object
        :type info: PackageInfo
        :param temp_dir: Temporary directory to be used
        :type temp_dir: str
        """
    shutil.copytree("build/darwin", os.path.join(temp_dir, "darwin"))

    tags = [
        ("#NAME#", info.name),
        ("#VERSION#", info.version),
        ("#PACKAGE#", info.package),
        ("#LOCATION#", info.install_location)
    ]

    # TODO: Add a list to PackageInfo with filenames/file paths with tags to replace
    print("Replacing tags") 
    replace_instances(os.path.join(temp_dir, "darwin/scripts/postinstall"), tags)
    replace_instances(os.path.join(temp_dir, "darwin/resources/uninstall.sh"), tags)
    replace_instances(os.path.join(temp_dir, "darwin/distribution.plist"), tags)
    replace_instances(os.path.join(temp_dir, "darwin/resources/com.androidwg.corkscrew.plist"), tags)

    print("Creating folder for package output")
    os.mkdir(os.path.join(temp_dir, "package"))

    # We need to set permissions to 755 for everything or else the installer refuses to install anything
    # without showing any errors during build. This was very fun to debug 😃
    chmod = subprocess.Popen(["chmod", "-R", "755", temp_dir], stdout=subprocess.PIPE)
    chmod.wait()
    print("Setted permissions recursively")
