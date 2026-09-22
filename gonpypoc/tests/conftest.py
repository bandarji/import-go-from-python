import ctypes

import pytest

from gonpypoc.cgotopypoc import load_library


@pytest.fixture(scope="session")
def lib() -> ctypes.CDLL:
    return load_library()
