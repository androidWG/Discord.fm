import json
import os
import shutil
import urllib.request


def get_pypi_url(name: str, filename: str) -> str:
    url = 'https://pypi.org/pypi/{}/json'.format(name)
    print('Extracting download url for', name)
    with urllib.request.urlopen(url) as response:
        body = json.loads(response.read().decode('utf-8'))
        for release in body['releases'].values():
            for source in release:
                if source['filename'] == filename:
                    return source['url']
        raise Exception('Failed to extract url from {}'.format(url))


def get_tar_package_url_pypi(name: str, version: str) -> str:
    url = 'https://pypi.org/pypi/{}/{}/json'.format(name, version)
    with urllib.request.urlopen(url) as response:
        body = json.loads(response.read().decode('utf-8'))
        for ext in ['bz2', 'gz', 'xz', 'zip']:
            for source in body['urls']:
                if source['url'].endswith(ext):
                    return source['url']
        err = 'Failed to get {}-{} source from {}'.format(name, version, url)
        raise ValueError(err)


def download_tar_pypi(url: str, tempdir: str) -> None:
    with urllib.request.urlopen(url) as response:
        file_path = os.path.join(tempdir, url.split('/')[-1])
        with open(file_path, 'x+b') as tar_file:
            shutil.copyfileobj(response, tar_file)
