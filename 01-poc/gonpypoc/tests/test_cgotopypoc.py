import ctypes
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from gonpypoc import main
from gonpypoc.cgotopypoc import (
    CPyComplex64,
    CPyComplex128,
    CRecord,
    Record,
    _as_record,
    _bind,
    _take_bytes,
    _take_string,
    assert_returns,
    build_library,
    find_source_dir,
    library_filename,
    load_library,
)


def test_library_filename_darwin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("gonpypoc.cgotopypoc.platform.system", lambda: "Darwin")
    assert library_filename() == "libcgotopypoc.dylib"


def test_library_filename_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("gonpypoc.cgotopypoc.platform.system", lambda: "Windows")
    assert library_filename() == "libcgotopypoc.dll"


def test_library_filename_linux(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("gonpypoc.cgotopypoc.platform.system", lambda: "Linux")
    assert library_filename() == "libcgotopypoc.so"


def test_find_source_dir_uses_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "cgotopypoc"
    source.mkdir()
    (source / "go.mod").write_text("module cgotopypoc\n")
    monkeypatch.setenv("CGOTOPYPOC_DIR", str(source))
    assert find_source_dir() == source


def test_find_source_dir_skips_env_without_go_mod(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    missing = tmp_path / "empty"
    missing.mkdir()
    real = tmp_path / "cgotopypoc"
    real.mkdir()
    (real / "go.mod").write_text("module cgotopypoc\n")
    monkeypatch.setenv("CGOTOPYPOC_DIR", str(missing))
    monkeypatch.chdir(tmp_path)
    assert find_source_dir() == real


def test_find_source_dir_discovers_repo() -> None:
    source = find_source_dir()
    assert source.name == "cgotopypoc"
    assert (source / "go.mod").is_file()
    assert (source / "returns.go").is_file()
    assert (source / "record.go").is_file()


def test_find_source_dir_raises_when_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("CGOTOPYPOC_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("gonpypoc.cgotopypoc.__file__", str(tmp_path / "cgotopypoc.py"))
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    with pytest.raises(FileNotFoundError, match="could not find cgotopypoc/go.mod"):
        find_source_dir()


def test_build_library_invokes_go(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    recorded: dict[str, object] = {}

    def fake_run(cmd, cwd, check, env):  # noqa: ANN001
        recorded["cmd"] = cmd
        recorded["cwd"] = cwd
        recorded["check"] = check
        recorded["cgo"] = env["CGO_ENABLED"]
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr("gonpypoc.cgotopypoc.library_filename", lambda: "libcgotopypoc.so")
    monkeypatch.setattr("gonpypoc.cgotopypoc.subprocess.run", fake_run)

    output = build_library(tmp_path)

    assert output == tmp_path / "libcgotopypoc.so"
    assert recorded["cmd"] == [
        "go",
        "build",
        "-buildmode=c-shared",
        "-o",
        str(output),
        ".",
    ]
    assert recorded["cwd"] == tmp_path
    assert recorded["check"] is True
    assert recorded["cgo"] == "1"


def test_build_library_defaults_to_find_source_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("gonpypoc.cgotopypoc.find_source_dir", lambda: tmp_path)
    monkeypatch.setattr("gonpypoc.cgotopypoc.library_filename", lambda: "libcgotopypoc.so")
    monkeypatch.setattr(
        "gonpypoc.cgotopypoc.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0),
    )
    assert build_library() == tmp_path / "libcgotopypoc.so"


def test_bind_sets_ctypes_signatures() -> None:
    names = (
        "ReturnNone",
        "ReturnBoolTrue",
        "ReturnBoolFalse",
        "ReturnInt8",
        "ReturnInt16",
        "ReturnInt32",
        "ReturnInt64",
        "ReturnUint8",
        "ReturnUint16",
        "ReturnUint32",
        "ReturnUint64",
        "ReturnFloat32",
        "ReturnFloat64",
        "ReturnComplex64",
        "ReturnComplex128",
        "ReturnRecord",
        "EchoRecord",
        "RecordScore",
        "RecordSize",
        "ReturnString",
        "ReturnEmptyString",
        "ReturnUnicodeString",
        "ReturnBytes",
        "FreeCString",
    )
    lib = SimpleNamespace(**{name: Mock() for name in names})

    _bind(lib)  # type: ignore[arg-type]

    assert lib.ReturnNone.restype is ctypes.c_void_p
    assert lib.ReturnBoolTrue.restype is ctypes.c_uint8
    assert lib.ReturnBoolFalse.restype is ctypes.c_uint8
    assert lib.ReturnInt8.restype is ctypes.c_int8
    assert lib.ReturnInt16.restype is ctypes.c_int16
    assert lib.ReturnInt32.restype is ctypes.c_int32
    assert lib.ReturnInt64.restype is ctypes.c_int64
    assert lib.ReturnUint8.restype is ctypes.c_uint8
    assert lib.ReturnUint16.restype is ctypes.c_uint16
    assert lib.ReturnUint32.restype is ctypes.c_uint32
    assert lib.ReturnUint64.restype is ctypes.c_uint64
    assert lib.ReturnFloat32.restype is ctypes.c_float
    assert lib.ReturnFloat64.restype is ctypes.c_double
    assert lib.ReturnComplex64.restype is CPyComplex64
    assert lib.ReturnComplex128.restype is CPyComplex128
    assert lib.ReturnRecord.restype is CRecord
    assert lib.EchoRecord.argtypes == [CRecord]
    assert lib.EchoRecord.restype is CRecord
    assert lib.RecordScore.argtypes == [CRecord]
    assert lib.RecordScore.restype is ctypes.c_double
    assert lib.RecordSize.restype is ctypes.c_int64
    assert lib.ReturnString.restype is ctypes.c_void_p
    assert lib.ReturnEmptyString.restype is ctypes.c_void_p
    assert lib.ReturnUnicodeString.restype is ctypes.c_void_p
    assert lib.ReturnBytes.argtypes == [ctypes.POINTER(ctypes.c_int)]
    assert lib.ReturnBytes.restype is ctypes.c_void_p
    assert lib.FreeCString.argtypes == [ctypes.c_void_p]
    assert lib.FreeCString.restype is None


def test_load_library_builds_and_binds(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    artifact = tmp_path / "libcgotopypoc.so"
    fake_lib = object()
    bound: list[object] = []

    monkeypatch.setattr("gonpypoc.cgotopypoc.build_library", lambda source_dir=None: artifact)
    monkeypatch.setattr("gonpypoc.cgotopypoc.ctypes.CDLL", lambda path: fake_lib)
    monkeypatch.setattr("gonpypoc.cgotopypoc._bind", bound.append)

    loaded = load_library(tmp_path)

    assert loaded is fake_lib
    assert bound == [fake_lib]


def test_take_string_decodes_and_frees(monkeypatch: pytest.MonkeyPatch) -> None:
    ptr = 0x1000
    lib = Mock()
    monkeypatch.setattr("ctypes.string_at", lambda value: b"[Go] Hello, World!")
    assert _take_string(lib, lambda: ptr) == "[Go] Hello, World!"
    lib.FreeCString.assert_called_once_with(ptr)


def test_take_string_rejects_null_pointer() -> None:
    lib = Mock()
    with pytest.raises(AssertionError, match="NULL pointer"):
        _take_string(lib, lambda: None)


def test_take_bytes_copies_and_frees(monkeypatch: pytest.MonkeyPatch) -> None:
    ptr = 0x2000
    lib = Mock()
    lib.ReturnBytes.return_value = ptr

    def fake_string_at(value: int, length: int | None = None) -> bytes:
        assert value == ptr
        assert length == 4
        return b"\x00\x7f\x80\xff"

    monkeypatch.setattr("ctypes.string_at", fake_string_at)
    monkeypatch.setattr(
        "gonpypoc.cgotopypoc.ctypes.byref",
        lambda length: setattr(length, "value", 4) or length,
    )

    assert _take_bytes(lib) == b"\x00\x7f\x80\xff"
    lib.FreeCString.assert_called_once_with(ptr)


def test_take_bytes_rejects_null_pointer() -> None:
    lib = Mock()
    lib.ReturnBytes.return_value = None
    with pytest.raises(AssertionError, match="NULL pointer"):
        _take_bytes(lib)


def test_assert_returns_uses_existing_library(lib: ctypes.CDLL) -> None:
    results = assert_returns(lib)
    by_name = {name: (value, py_type) for name, value, py_type in results}
    assert by_name["ReturnNone"] == (None, type(None))
    assert by_name["ReturnBoolTrue"] == (True, bool)
    assert by_name["ReturnString"] == ("[Go] Hello, World!", str)
    assert by_name["ReturnBytes"] == (b"\x00\x7f\x80\xff", bytes)
    assert [name for name, _, _ in results] == [
        "ReturnNone",
        "ReturnBoolTrue",
        "ReturnBoolFalse",
        "ReturnInt8",
        "ReturnInt16",
        "ReturnInt32",
        "ReturnInt64",
        "ReturnUint8",
        "ReturnUint16",
        "ReturnUint32",
        "ReturnUint64",
        "ReturnFloat32",
        "ReturnFloat64",
        "ReturnComplex64",
        "ReturnComplex128",
        "ReturnString",
        "ReturnEmptyString",
        "ReturnUnicodeString",
        "ReturnBytes",
        "ReturnRecord",
        "EchoRecord",
        "RecordScore",
        "RecordSize",
    ]
    assert by_name["ReturnRecord"] == (Record(-7, 2.5, True), Record)
    assert by_name["EchoRecord"] == (Record(11, -1.25, False), Record)
    assert by_name["RecordScore"] == (-6.0, float)
    assert by_name["RecordSize"] == (ctypes.sizeof(CRecord), int)


def test_main_prints_validated_returns(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        "gonpypoc.assert_returns",
        lambda: [("ReturnNone", None, type(None)), ("ReturnInt8", -128, int)],
    )
    main()
    output = capsys.readouterr().out
    assert "cgotopypoc: all compatible Python return types validated" in output
    assert "ReturnNone: None (NoneType)" in output
    assert "ReturnInt8: -128 (int)" in output


def test_complex_struct_fields() -> None:
    assert CPyComplex64._fields_ == [("real", ctypes.c_float), ("imag", ctypes.c_float)]
    assert CPyComplex128._fields_ == [("real", ctypes.c_double), ("imag", ctypes.c_double)]


def test_record_struct_fields() -> None:
    assert CRecord._fields_ == [
        ("count", ctypes.c_int64),
        ("ratio", ctypes.c_double),
        ("ready", ctypes.c_uint8),
    ]


def test_as_record_converts_ready_flag() -> None:
    assert _as_record(CRecord(-7, 2.5, 1)) == Record(-7, 2.5, True)
    assert _as_record(CRecord(0, 0.0, 0)) == Record(0, 0.0, False)
    ready = _as_record(CRecord(1, 1.0, 2))
    assert ready.ready is True
