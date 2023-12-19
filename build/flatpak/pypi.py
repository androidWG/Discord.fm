import json
import os
import shutil
import urllib.request

# TODO: Make cache for data collected


def get_pypi_url(name: str, filename: str) -> str:
    url = f"https://pypi.org/pypi/{name}/json"
    print("Extracting download url for", name)
    with urllib.request.urlopen(url) as response:
        body = json.loads(response.read().decode("utf-8"))
        for release in body["releases"].values():
            for source in release:
                if source["filename"] == filename:
                    return source["url"]
        raise Exception(f"Failed to extract url from {url}")


def get_tar_package_url_pypi(name: str, version: str) -> str:
    url = f"https://pypi.org/pypi/{name}/{version}/json"
    with urllib.request.urlopen(url) as response:
        body = json.loads(response.read().decode("utf-8"))
        for ext in ["bz2", "gz", "xz", "zip"]:
            for source in body["urls"]:
                if source["url"].endswith(ext):
                    return source["url"]
        err = f"Failed to get {name}-{version} source from {url}"
        raise ValueError(err)


def download_tar_pypi(url: str, tempdir: str) -> None:
    file_path = os.path.join(tempdir, url.split("/")[-1])

    if os.path.isfile(file_path):
        return

    with urllib.request.urlopen(url) as response:
        with open(file_path, "x+b") as tar_file:
            shutil.copyfileobj(response, tar_file)
