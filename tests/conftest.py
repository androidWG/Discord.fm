from typing import Iterator
from unittest.mock import patch

import pytest


@pytest.fixture(scope="session", autouse=True)
def default_session_fixture() -> Iterator[None]:
    print("Patching pystray")
    with patch("pystray._xorg.Icon"):
        yield
    print("Patching complete. Unpatching")
