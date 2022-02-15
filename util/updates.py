import os
import requests
import logging
from typing import Optional
from packaging import version
from settings import local_settings
from util import request_handler

logger = logging.getLogger("discord_fm").getChild(__name__)


def get_newest_release() -> Optional[tuple[version.Version, dict]]:
    """Gets the newest release from GitHub, returned as a tuple of the version and a GitHub asset object for Windows."""
    headers = {"Accept": "application/vnd.github.v3+json",
               "User-Agent": "Discord.fm"}

    handler = request_handler.RequestHandler("GitHub request")
    if local_settings.get("pre_releases"):
        request = handler.attempt_request(
            requests.get,
            url="https://api.github.com/repos/AndroidWG/Discord.fm/releases",
            headers=headers)
        release_list = request.json()
        release_list.sort(key=lambda x: version.parse(x["tag_name"]), reverse=True)
        latest = release_list[0]
    else:
        request = handler.attempt_request(
            requests.get,
            url="https://api.github.com/repos/AndroidWG/Discord.fm/releases/latest",
            headers=headers)
        latest = request.json()

    try:
        return version.parse(latest["tag_name"]), \
               next(x for x in latest["assets"]
                    if x["content_type"] == "application/x-msdownload" and "setup-win" in x["name"])
    except StopIteration:
        logger.error("Newest release doesn't include a Windows executable download")
        return None


def download_asset(asset: dict) -> str:
    """Downloads a GitHub asset to the app's data folder and returns the full path of the file."""
    headers = {"Accept": "application/octet-stream",
               "User-Agent": "Discord.fm"}

    logger.info(f'Requesting asset "{asset["name"]}" from GitHub')
    handler = request_handler.RequestHandler("GitHub download")
    request = handler.attempt_request(
        requests.get,
        timeout=1200,
        url=asset["url"],
        headers=headers)
    response_size = int(request.headers['content-length'])

    logger.info(f"Starting writing {response_size} bytes")
    downloaded_path = os.path.join(local_settings.app_data_path, asset["name"])
    with open(downloaded_path, "wb") as file:
        bytes_read = 0

        chunk_size = 512
        for chunk in request.iter_content(chunk_size):
            file.write(chunk)

            bytes_read += chunk_size

    logger.info(f"Successfully finished writing {asset['name']}")
    return downloaded_path
