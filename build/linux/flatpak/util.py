import hashlib


def get_package_name(filename: str) -> str:
    if filename.endswith(('bz2', 'gz', 'xz', 'zip')):
        segments = filename.split('-')
        if len(segments) == 2:
            return segments[0]
        return '-'.join(segments[:len(segments) - 1])
    elif filename.endswith('whl'):
        segments = filename.split('-')
        if len(segments) == 5:
            return segments[0]
        candidate = segments[:len(segments) - 4]
        # Some packages list the version number twice
        # e.g. PyQt5-5.15.0-5.15.0-cp35.cp36.cp37.cp38-abi3-manylinux2014_x86_64.whl
        if candidate[-1] == segments[len(segments) - 4]:
            return '-'.join(candidate[:-1])
        return '-'.join(candidate)
    else:
        raise Exception(
            'Downloaded filename: {} does not end with bz2, gz, xz, zip, or whl'.format(filename)
        )


def get_file_version(filename: str) -> str:
    name = get_package_name(filename)
    segments = filename.split(name + '-')
    version = segments[1].split('-')[0]
    for ext in ['tar.gz', 'whl', 'tar.xz', 'tar.gz', 'tar.bz2', 'zip']:
        version = version.replace('.' + ext, '')
    return version


def get_file_hash(filename: str) -> str:
    sha = hashlib.sha256()
    print('Generating hash for', filename.split('/')[-1])
    with open(filename, 'rb') as f:
        while True:
            data = f.read(1024 * 1024 * 32)
            if not data:
                break
            sha.update(data)
        return sha.hexdigest()


def fprint(string: str) -> None:
    separator = '=' * 72  # Same as `flatpak-builder`
    print(separator)
    print(string)
    print(separator)


def parse_continuation_lines(fin):
    for line in fin:
        line = line.rstrip('\n')
        while line.endswith('\\'):
            try:
                line = line[:-1] + next(fin).rstrip('\n')
            except StopIteration:
                exit('Requirements have a wrong number of line continuation characters "\\"')
        yield line
