import ctypes

import pytest

from gonpypoc.cgotopypoc import _take_bytes, _take_string


def test_return_none(lib: ctypes.CDLL) -> None:
    assert lib.ReturnNone() is None


def test_return_bool_true(lib: ctypes.CDLL) -> None:
    value = bool(lib.ReturnBoolTrue())
    assert type(value) is bool
    assert value is True


def test_return_bool_false(lib: ctypes.CDLL) -> None:
    value = bool(lib.ReturnBoolFalse())
    assert type(value) is bool
    assert value is False


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("ReturnInt8", -128),
        ("ReturnInt16", -32768),
        ("ReturnInt32", -2147483648),
        ("ReturnInt64", -9223372036854775808),
        ("ReturnUint8", 255),
        ("ReturnUint16", 65535),
        ("ReturnUint32", 4294967295),
        ("ReturnUint64", 18446744073709551615),
    ],
)
def test_return_integers(lib: ctypes.CDLL, name: str, expected: int) -> None:
    value = getattr(lib, name)()
    assert type(value) is int
    assert value == expected


def test_return_float32(lib: ctypes.CDLL) -> None:
    value = lib.ReturnFloat32()
    assert type(value) is float
    assert value == 1.5


def test_return_float64(lib: ctypes.CDLL) -> None:
    value = lib.ReturnFloat64()
    assert type(value) is float
    assert value == 2.718281828459045


def test_return_complex64(lib: ctypes.CDLL) -> None:
    raw = lib.ReturnComplex64()
    value = complex(raw.real, raw.imag)
    assert type(value) is complex
    assert value == 1.5 - 2.5j


def test_return_complex128(lib: ctypes.CDLL) -> None:
    raw = lib.ReturnComplex128()
    value = complex(raw.real, raw.imag)
    assert type(value) is complex
    assert value == 1.25 - 2.5j


def test_return_string(lib: ctypes.CDLL) -> None:
    value = _take_string(lib, lib.ReturnString)
    assert type(value) is str
    assert value == "hello from go"


def test_return_empty_string(lib: ctypes.CDLL) -> None:
    value = _take_string(lib, lib.ReturnEmptyString)
    assert type(value) is str
    assert value == ""


def test_return_unicode_string(lib: ctypes.CDLL) -> None:
    value = _take_string(lib, lib.ReturnUnicodeString)
    assert type(value) is str
    assert value == "बंदरजी"


def test_return_bytes(lib: ctypes.CDLL) -> None:
    value = _take_bytes(lib)
    assert type(value) is bytes
    assert value == b"\x00\x7f\x80\xff"


def test_free_cstring(lib: ctypes.CDLL) -> None:
    ptr = lib.ReturnString()
    assert ptr
    lib.FreeCString(ptr)
