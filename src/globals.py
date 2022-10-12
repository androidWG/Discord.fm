from __future__ import annotations

import packaging.version

__VERSION = "0.8.0"
__DEBUG = True


def get_version(parsed: bool = False) -> packaging.version.Version | str:
    if parsed:
        return packaging.version.parse(__VERSION)
    else:
        return __VERSION


def get_debug() -> bool:
    return __DEBUG
