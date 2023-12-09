import packaging.version

__VERSION = "0.10.2"


def get_version(parsed: bool = False) -> packaging.version.Version | str:
    if parsed:
        return packaging.version.parse(__VERSION)
    else:
        return __VERSION
