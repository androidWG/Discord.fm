import os
import subprocess
import sys
import tempfile
from collections import OrderedDict

import requirements
import yaml

from . import pypi
from . import util

# Python3 packages that come as part of org.freedesktop.Sdk.
SYSTEM_PACKAGES = [
    "cython",
    "easy_install",
    "mako",
    "markdown",
    "meson",
    "pip",
    "pygments",
    "setuptools",
]
FLATPACK_CMD = ["pip3"]

output_package = "discord_fm"
output_filename = output_package + ".yaml"

pypi_module = {
    "name": output_package,
    "buildsystem": "simple",
    "build-commands": [],
    "sources": [],
}
sources = {}


def make_yaml(requirements_path: str):
    requirements_file = os.path.expanduser(requirements_path)
    with open(requirements_file, "r") as req_file:
        reqs = util.parse_continuation_lines(req_file)
        reqs_as_str = "\n".join([r.split("--hash")[0] for r in reqs])
        packages = list(requirements.parse(reqs_as_str))
        use_hash = "--hash=" in req_file.read()

    with tempfile.TemporaryDirectory() as tempdir:
        pip_download = FLATPACK_CMD + [
            "download",
            "--exists-action=i",
            "--dest",
            tempdir,
            "-r",
            requirements_file,
        ]
        if use_hash:
            pip_download.append("--require-hashes")

        download_sources(pip_download, requirements_file)

        download_packages(packages, tempdir)

        generate_dependencies(packages)

        write_output_file()


def download_sources(pip_download, requirements_file):
    util.fprint("Downloading sources")
    cmd = " ".join(pip_download)
    print('Running: "{}"'.format(cmd))
    try:
        subprocess.run(pip_download, check=True)
    except subprocess.CalledProcessError:
        print("Failed to download")
        print("Please fix the module manually in the generated file")
    try:
        os.remove(requirements_file)
    except FileNotFoundError:
        pass


def download_packages(packages, tempdir):
    util.fprint("Downloading arch independent packages")
    for filename in os.listdir(tempdir):
        if not filename.endswith(("bz2", "any.whl", "gz", "xz", "zip")):
            version = util.get_file_version(filename)
            name = util.get_package_name(filename)
            try:
                url = pypi.get_tar_package_url_pypi(name, version)
            except ValueError:
                continue
            print("Deleting", filename)
            try:
                os.remove(os.path.join(tempdir, filename))
            except FileNotFoundError:
                pass
            print("Downloading {}".format(url))
            pypi.download_tar_pypi(url, tempdir)
    files = {util.get_package_name(f): [] for f in os.listdir(tempdir)}
    for filename in os.listdir(tempdir):
        name = util.get_package_name(filename)
        files[name].append(filename)

        # Delete redundant sources, for vcs sources
        for name in files:
            if len(files[name]) > 1:
                zip_source = False
                for f in files[name]:
                    if f.endswith(".zip"):
                        zip_source = True
                if zip_source:
                    for f in files[name]:
                        if not f.endswith(".zip"):
                            try:
                                os.remove(os.path.join(tempdir, f))
                            except FileNotFoundError:
                                pass

        vcs_packages = {
            x.name: {"vcs": x.vcs, "revision": x.revision, "uri": x.uri}
            for x in packages
            if x.vcs
        }

        util.fprint("Obtaining hashes and urls")
        for filename in os.listdir(tempdir):
            name = util.get_package_name(filename)
            sha256 = util.get_file_hash(os.path.join(tempdir, filename))

            if name in vcs_packages:
                uri = vcs_packages[name]["uri"]
                revision = vcs_packages[name]["revision"]
                vcs = vcs_packages[name]["vcs"]
                url = "https://" + uri.split("://", 1)[1]
                s = "commit"
                if vcs == "svn":
                    s = "revision"
                source = OrderedDict(
                    [
                        ("type", vcs),
                        ("url", url),
                        (s, revision),
                    ]
                )
                is_vcs = True
            else:
                url = pypi.get_pypi_url(name, filename)
                source = OrderedDict(
                    [("type", "file"), ("url", url), ("sha256", sha256)]
                )
                is_vcs = False
            sources[name] = {"source": source, "vcs": is_vcs}


def generate_dependencies(packages):
    util.fprint("Generating dependencies")
    for package in packages:
        if package.name is None:
            print(
                f"Warning: skipping invalid requirement specification {package.line} because it is missing a name",
                file=sys.stderr,
            )
            print(
                "Append #egg=<pkgname> to the end of the requirement line to fix",
                file=sys.stderr,
            )
            continue
        elif package.name.casefold() in SYSTEM_PACKAGES:
            continue

        if len(package.extras) > 0:
            extras = "[" + ",".join(extra for extra in package.extras) + "]"
        else:
            extras = ""

        version_list = [x[0] + x[1] for x in package.specs]
        version = ",".join(version_list)

        if package.vcs:
            revision = ""
            if package.revision:
                revision = "@" + package.revision
            pkg = package.uri + revision + "#egg=" + package.name
        else:
            pkg = package.name + extras + version

        dependencies = []
        # Downloads the package again to list dependencies

        tempdir_prefix = "pip-generator-{}".format(package.name)
        with tempfile.TemporaryDirectory(
                prefix="{}-{}".format(tempdir_prefix, package.name)
        ) as tempdir:
            pip_download = FLATPACK_CMD + [
                "download",
                "--exists-action=i",
                "--dest",
                tempdir,
            ]
            try:
                print("Generating dependencies for {}".format(package.name))
                subprocess.run(
                    pip_download + [pkg], check=True, stdout=subprocess.DEVNULL
                )
                for filename in os.listdir(tempdir):
                    dep_name = util.get_package_name(filename)
                    if dep_name.casefold() in SYSTEM_PACKAGES:
                        continue
                    dependencies.append(dep_name)

            except subprocess.CalledProcessError:
                print("Failed to download {}".format(package.name))

        is_vcs = True if package.vcs else False
        package_sources = []
        for dependency in dependencies:
            if dependency in sources:
                source = sources[dependency]
            elif dependency.replace("_", "-") in sources:
                source = sources[dependency.replace("_", "-")]
            else:
                continue

            if not (not source["vcs"] or is_vcs):
                continue

            package_sources.append(source["source"])

        if package.vcs:
            name_for_pip = "."
        else:
            name_for_pip = pkg

        pip_command = [
            "venv/bin/python",
            "-m",
            "pip",
            "install",
            "--verbose",
            "--exists-action=i",
            "--no-index",
            '--find-links="file://${PWD}"',
            "--prefix=${FLATPAK_DEST}",
            f'"{name_for_pip}"',
        ]

        pypi_module["build-commands"].append(" ".join(pip_command))
        pypi_module["sources"] += package_sources


def write_output_file():
    with open(output_filename, "w") as output:
        class OrderedDumper(yaml.Dumper):
            def increase_indent(self, flow=False, indentless=False):
                return super(OrderedDumper, self).increase_indent(flow, False)

        def dict_representer(dumper, data):
            return dumper.represent_dict(data.items())

        OrderedDumper.add_representer(OrderedDict, dict_representer)

        yaml.dump(pypi_module, output, Dumper=OrderedDumper)
        print("Output saved to {}".format(output_filename))
