"""Load the cgotopypoc CGO shared library and assert every compatible return type."""

from __future__ import annotations

import ctypes
import os
import platform
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any


class CPyComplex64(ctypes.Structure):
    _fields_ = [("real", ctypes.c_float), ("imag", ctypes.c_float)]


class CPyComplex128(ctypes.Structure):
    _fields_ = [("real", ctypes.c_double), ("imag", ctypes.c_double)]


def library_filename() -> str:
    system = platform.system()
    if system == "Darwin":
        return "libcgotopypoc.dylib"
    if system == "Windows":
        return "libcgotopypoc.dll"
    return "libcgotopypoc.so"


def find_source_dir() -> Path:
    env = os.environ.get("CGOTOPYPOC_DIR")
    if env:
        path = Path(env)
        if (path / "go.mod").is_file():
            return path

    candidates: list[Path] = []
    for start in (Path.cwd(), Path(__file__).resolve().parent):
        for parent in (start, *start.parents):
            candidates.append(parent / "cgotopypoc")
            if parent.name == "cgotopypoc":
                candidates.append(parent)
    candidates.append(Path("/app/cgotopypoc"))

    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if (resolved / "go.mod").is_file():
            return resolved

    raise FileNotFoundError("could not find cgotopypoc/go.mod")


def build_library(source_dir: Path | None = None) -> Path:
    source_dir = source_dir or find_source_dir()
    output = source_dir / library_filename()
    env = os.environ.copy()
    env["CGO_ENABLED"] = "1"
    subprocess.run(
        ["go", "build", "-buildmode=c-shared", "-o", str(output), "."],
        cwd=source_dir,
        check=True,
        env=env,
    )
    return output


def _bind(lib: ctypes.CDLL) -> None:
    lib.ReturnNone.restype = ctypes.c_void_p
    lib.ReturnBoolTrue.restype = ctypes.c_uint8
    lib.ReturnBoolFalse.restype = ctypes.c_uint8
    lib.ReturnInt8.restype = ctypes.c_int8
    lib.ReturnInt16.restype = ctypes.c_int16
    lib.ReturnInt32.restype = ctypes.c_int32
    lib.ReturnInt64.restype = ctypes.c_int64
    lib.ReturnUint8.restype = ctypes.c_uint8
    lib.ReturnUint16.restype = ctypes.c_uint16
    lib.ReturnUint32.restype = ctypes.c_uint32
    lib.ReturnUint64.restype = ctypes.c_uint64
    lib.ReturnFloat32.restype = ctypes.c_float
    lib.ReturnFloat64.restype = ctypes.c_double
    lib.ReturnComplex64.restype = CPyComplex64
    lib.ReturnComplex128.restype = CPyComplex128
    lib.ReturnString.restype = ctypes.c_void_p
    lib.ReturnEmptyString.restype = ctypes.c_void_p
    lib.ReturnUnicodeString.restype = ctypes.c_void_p
    lib.ReturnBytes.argtypes = [ctypes.POINTER(ctypes.c_int)]
    lib.ReturnBytes.restype = ctypes.c_void_p
    lib.FreeCString.argtypes = [ctypes.c_void_p]
    lib.FreeCString.restype = None


def load_library(source_dir: Path | None = None) -> ctypes.CDLL:
    output = build_library(source_dir)
    lib = ctypes.CDLL(str(output))
    _bind(lib)
    return lib


def _take_string(lib: ctypes.CDLL, fn: Callable[[], int | None]) -> str:
    ptr = fn()
    assert ptr, "Go string return was a NULL pointer"
    try:
        return ctypes.string_at(ptr).decode("utf-8")
    finally:
        lib.FreeCString(ptr)


def _take_bytes(lib: ctypes.CDLL) -> bytes:
    length = ctypes.c_int()
    ptr = lib.ReturnBytes(ctypes.byref(length))
    assert ptr, "Go bytes return was a NULL pointer"
    try:
        return ctypes.string_at(ptr, length.value)
    finally:
        lib.FreeCString(ptr)


def assert_returns(lib: ctypes.CDLL | None = None) -> list[tuple[str, Any, type]]:
    """Import the compiled Go library and assert each compatible Python return type."""
    lib = lib or load_library()
    results: list[tuple[str, Any, type]] = []

    none_value = lib.ReturnNone()
    assert none_value is None
    results.append(("ReturnNone", none_value, type(None)))

    true_value = bool(lib.ReturnBoolTrue())
    assert type(true_value) is bool
    assert true_value is True
    results.append(("ReturnBoolTrue", true_value, bool))

    false_value = bool(lib.ReturnBoolFalse())
    assert type(false_value) is bool
    assert false_value is False
    results.append(("ReturnBoolFalse", false_value, bool))

    integers = (
        ("ReturnInt8", lib.ReturnInt8, -128),
        ("ReturnInt16", lib.ReturnInt16, -32768),
        ("ReturnInt32", lib.ReturnInt32, -2147483648),
        ("ReturnInt64", lib.ReturnInt64, -9223372036854775808),
        ("ReturnUint8", lib.ReturnUint8, 255),
        ("ReturnUint16", lib.ReturnUint16, 65535),
        ("ReturnUint32", lib.ReturnUint32, 4294967295),
        ("ReturnUint64", lib.ReturnUint64, 18446744073709551615),
    )
    for name, fn, expected in integers:
        value = fn()
        assert type(value) is int, f"{name} returned {type(value).__name__}"
        assert value == expected, f"{name} returned {value!r}, expected {expected!r}"
        results.append((name, value, int))

    float32_value = lib.ReturnFloat32()
    assert type(float32_value) is float
    assert float32_value == 1.5
    results.append(("ReturnFloat32", float32_value, float))

    float64_value = lib.ReturnFloat64()
    assert type(float64_value) is float
    assert float64_value == 2.718281828459045
    results.append(("ReturnFloat64", float64_value, float))

    complex64_raw = lib.ReturnComplex64()
    complex64_value = complex(complex64_raw.real, complex64_raw.imag)
    assert type(complex64_value) is complex
    assert complex64_value == 1.5 - 2.5j
    results.append(("ReturnComplex64", complex64_value, complex))

    complex128_raw = lib.ReturnComplex128()
    complex128_value = complex(complex128_raw.real, complex128_raw.imag)
    assert type(complex128_value) is complex
    assert complex128_value == 1.25 - 2.5j
    results.append(("ReturnComplex128", complex128_value, complex))

    string_value = _take_string(lib, lib.ReturnString)
    assert type(string_value) is str
    assert string_value == "hello from go"
    results.append(("ReturnString", string_value, str))

    empty_string = _take_string(lib, lib.ReturnEmptyString)
    assert type(empty_string) is str
    assert empty_string == ""
    results.append(("ReturnEmptyString", empty_string, str))

    unicode_string = _take_string(lib, lib.ReturnUnicodeString)
    assert type(unicode_string) is str
    assert unicode_string == "बंदरजी"
    results.append(("ReturnUnicodeString", unicode_string, str))

    bytes_value = _take_bytes(lib)
    assert type(bytes_value) is bytes
    assert bytes_value == b"\x00\x7f\x80\xff"
    results.append(("ReturnBytes", bytes_value, bytes))

    return results
