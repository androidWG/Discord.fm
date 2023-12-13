import logging
import os
import platform

import requests
from packaging import version
from packaging.version import Version

from util import request_handler

logger = logging.getLogger("discord_fm").getChild(__name__)


def get_newest_release_with_asset(manager) -> tuple[None, None] | tuple[Version, dict]:
    """Gets the newest release from GitHub, returned as a tuple of the version and a GitHub asset object for Windows."""
    logger.debug("Requesting newest release from GitHub")
    json_output = _get_release_json(manager)

    try:
        logger.info(
            f'Latest version is {json_output["tag_name"]}, published at {json_output["published_at"]} '
            f'{"(pre-release)" if json_output["prerelease"] == True else ""}'
        )
        latest_asset = _match_asset(json_output)

        if latest_asset is None:
            logger.warning(
                f"Unable to find applicable asset among release {json_output['tag_name']}"
            )
            return None, None
        else:
            return version.parse(json_output["tag_name"]), latest_asset
    except StopIteration:
        logger.error("Unexpectedly formatted GitHub release")
        return None, None


def download_asset(manager, asset: dict) -> Path:
    """Downloads a GitHub asset to the app's data folder and returns the full path of the file."""
    headers = {"Accept": "application/octet-stream", "User-Agent": "Discord.fm"}

    logger.debug(f'Requesting asset "{asset["name"]}" from GitHub')
    handler = request_handler.RequestHandler(manager, "GitHub download")
    request = handler.attempt_request(
        requests.get, timeout=3600, url=asset["url"], headers=headers
    )
    response_size = int(request.headers["content-length"])

    logger.info(f"Starting writing {response_size} bytes")
    downloaded_path = Path(manager.settings.app_data_path, asset["name"])
    with open(downloaded_path, "wb") as file:
        bytes_read = 0

        chunk_size = 512
        for chunk in request.iter_content(chunk_size):
            file.write(chunk)

            bytes_read += chunk_size

    logger.info(f"Successfully finished writing {asset['name']}")
    return downloaded_path


def _match_asset(json_output) -> dict | None:
    current_platform = platform.system()
    match current_platform:
        case "Windows":
            name = "setup-win"
        case "Linux":
            name = "linux"
        case "Darwin":
            raise NotImplementedError

    try:
        applicable_assets = (
            x
            for x in json_output["assets"]
            if "application/x-" in x["content_type"] and name in x["name"]
        )
    except StopIteration:
        logger.error("Unexpectedly formatted GitHub asset list")
        return None

    latest_asset = next(applicable_assets, None)
    return latest_asset


def _get_release_json(manager) -> dict | None:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Discord.fm",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    handler = request_handler.RequestHandler(manager, "GitHub request")
    base_url = "https://api.github.com/repos/AndroidWG/Discord.fm/releases"
    result = handler.attempt_request(
        requests.get,
        url=base_url + "/latest"
        if not manager.settings.get("pre_releases")
        else base_url,
        headers=headers,
    )
    json_output = result.json()
    if result.status_code == 403 and "rate limit" in json_output["message"]:
        logger.warning("Hit rate limit for GitHub API")
        return None

    if manager.settings.get("pre_releases"):
        json_output.sort(key=lambda x: version.parse(x["tag_name"]), reverse=True)
        return json_output[0]
    else:
        return json_output
