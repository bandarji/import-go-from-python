# import-go-from-python

Proof of concept work for importing Go code in Python programs.

The Python side of this work lives in the `gonpypoc` package. It is a [uv](https://docs.astral.sh/uv/) project: uv manages the Python version, virtual environment, dependencies, and lockfile.

## Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.12 or later
- [Go](https://go.dev/doc/install) 1.26 or later, with a C compiler (`gcc` / Xcode CLT) for CGO
- Git (this repository is already a git repo)

uv will download a managed CPython interpreter if a matching one is not already available.

## Project setup (executed)

These commands created the `gonpypoc` package from the repository root.

Initialize a uv **package** project in a subdirectory. `--vcs none` avoids nesting a second git repo. `--no-workspace` creates a standalone project instead of attaching to a uv workspace.

```bash
uv init gonpypoc \
  --name gonpypoc \
  --package \
  --vcs none \
  --description "Proof of concept for importing Go code in Python programs" \
  --no-workspace
```

Create the virtual environment, resolve dependencies, and install the package in editable mode:

```bash
cd gonpypoc
uv sync
```

That produced:

- CPython 3.14.7 (from `.python-version`)
- a local `.venv` under `gonpypoc/`
- `uv.lock`
- an editable install of `gonpypoc==0.1.0`

## Layout

```
cgotopypoc/
  go.mod              # Go module
  returns.go          # CGO exports for each compatible Python return type
gonpypoc/
  pyproject.toml      # project metadata and build backend
  uv.lock             # locked dependency set
  .python-version     # pinned interpreter (3.14)
  README.md
  src/gonpypoc/
    __init__.py       # package entry; runs the CGO assertions
    cgotopypoc.py     # builds, loads, and asserts the shared library
  tests/
    conftest.py       # shared pytest fixture that loads the CGO library
    test_cgotopypoc.py
    test_go_returns.py
```

`.venv` is created by `uv sync` and is gitignored. The CGO shared library (`libcgotopypoc.so` / `.dylib`) and generated `libcgotopypoc.h` are also gitignored.

## Daily commands

Run all of these from `gonpypoc/`.

```bash
# Run the console script (gonpypoc:main)
uv run gonpypoc

# Recreate or update the environment from the lockfile
uv sync

# Add a runtime dependency (updates pyproject.toml and uv.lock)
uv add <package>

# Add a development dependency
uv add --dev <package>

# Remove a dependency
uv remove <package>

# Run an arbitrary command in the project environment
uv run python -c "import gonpypoc; gonpypoc.main()"

# Run the pytest suite
uv run pytest
```

`uv run` uses the project environment automatically. You do not need to activate `.venv` first.

## `pyproject.toml` notes

- **Package layout:** `src/gonpypoc` via `--package`
- **Build backend:** `uv_build`
- **Console script:** `gonpypoc = "gonpypoc:main"`
- **Python:** `requires-python = ">=3.14"`
- **Authors:** filled from git (`Sean Jain Ellis <sellis@bandarji.com>`)

## Unit tests (pytest)

`pytest` is a development dependency. Tests cover every Python helper in `gonpypoc.cgotopypoc`, `main()`, and every CGO export.

```bash
cd gonpypoc
uv add --dev pytest
uv run pytest
```

Executed output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/sellis/src/bandarji/import-go-from-python/gonpypoc
configfile: pyproject.toml
testpaths: tests
collected 38 items

tests/test_cgotopypoc.py ..................                              [ 47%]
tests/test_go_returns.py ....................                            [100%]

============================== 38 passed in 0.61s ==============================
```

See the [uv project guide](https://docs.astral.sh/uv/concepts/projects/) and [`uv init`](https://docs.astral.sh/uv/reference/cli/#uv-init) for more on this layout.

## CGO shared library (`cgotopypoc`)

`cgotopypoc` is a Go `package main` built with [`-buildmode=c-shared`](https://pkg.go.dev/cmd/go#hdr-Build_modes). Each `//export` function returns a C-compatible value that Python can import through [`ctypes`](https://docs.python.org/3/library/ctypes.html).

Python built-in types that can cross this C ABI:

| Python type | CGO return | Function |
| --- | --- | --- |
| `None` | `NULL` `void*` | `ReturnNone` |
| `bool` | `GoUint8` | `ReturnBoolTrue`, `ReturnBoolFalse` |
| `int` | `int8`–`int64`, `uint8`–`uint64` | `ReturnInt8` … `ReturnUint64` |
| `float` | `float32`, `float64` | `ReturnFloat32`, `ReturnFloat64` |
| `complex` | `CPyComplex64`, `CPyComplex128` | `ReturnComplex64`, `ReturnComplex128` |
| `str` | `char*` (UTF-8) | `ReturnString`, `ReturnEmptyString`, `ReturnUnicodeString` |
| `bytes` | `char*` + length | `ReturnBytes` |

Lists, tuples, and dicts are not C-ABI types, so they are not exported. `C.CString` / `C.CBytes` allocations are released with `FreeCString`.

### Executed commands

Create the Go module (from the repository root):

```bash
mkdir -p cgotopypoc
cd cgotopypoc
go mod init cgotopypoc
```

`go.mod` pins `go 1.26` so the module builds with the local toolchain (1.26.5) and the Docker toolchain (1.27.1).

Build the shared library. macOS produces a `.dylib`; Linux produces a `.so`:

```bash
# macOS (executed locally)
cd cgotopypoc
CGO_ENABLED=1 go build -buildmode=c-shared -o libcgotopypoc.dylib .

# Linux (executed in Docker)
cd cgotopypoc
CGO_ENABLED=1 go build -buildmode=c-shared -o libcgotopypoc.so .
```

`gonpypoc` rebuilds that library if needed, loads it, and asserts type plus value for every export:

```bash
cd gonpypoc
uv run gonpypoc
```

Executed output:

```
cgotopypoc: all compatible Python return types validated
  ReturnNone: None (NoneType)
  ReturnBoolTrue: True (bool)
  ReturnBoolFalse: False (bool)
  ReturnInt8: -128 (int)
  ReturnInt16: -32768 (int)
  ReturnInt32: -2147483648 (int)
  ReturnInt64: -9223372036854775808 (int)
  ReturnUint8: 255 (int)
  ReturnUint16: 65535 (int)
  ReturnUint32: 4294967295 (int)
  ReturnUint64: 18446744073709551615 (int)
  ReturnFloat32: 1.5 (float)
  ReturnFloat64: 2.718281828459045 (float)
  ReturnComplex64: (1.5-2.5j) (complex)
  ReturnComplex128: (1.25-2.5j) (complex)
  ReturnString: 'hello from go' (str)
  ReturnEmptyString: '' (str)
  ReturnUnicodeString: 'बंदरजी' (str)
  ReturnBytes: b'\x00\x7f\x80\xff' (bytes)
```

See [Command cgo](https://pkg.go.dev/cmd/cgo) and [Calling Go from Python via C](https://pkg.go.dev/cmd/cgo#hdr-C_references_to_Go).

## Docker

The `Dockerfile` builds a Linux image with the latest stable Python and Go, plus uv, the `gonpypoc` package, and a prebuilt `cgotopypoc` shared library.

| Tool | Version | Source |
| --- | --- | --- |
| Python | 3.14.7 | [`python:3.14.7-slim-trixie`](https://hub.docker.com/_/python) |
| Go | 1.27.1 | copied from [`golang:1.27.1-trixie`](https://hub.docker.com/_/golang) |
| uv | latest | copied from [`ghcr.io/astral-sh/uv:latest`](https://docs.astral.sh/uv/guides/integration/docker/) |

`build-essential` is installed so CGO can compile the shared library. The image copies `cgotopypoc/`, runs `go build -buildmode=c-shared -o libcgotopypoc.so .`, and sets `CGOTOPYPOC_DIR=/app/cgotopypoc`.

Build and run from the repository root:

```bash
docker build -t gonpypoc .
docker run --rm gonpypoc
```

The container builds (if needed) and imports the `.so`, then runs the same assertions as `uv run gonpypoc`. Executed output matches the local run above.

Confirm the toolchains in the image:

```bash
docker run --rm --entrypoint bash gonpypoc -c \
  'python --version && go version && uv --version && gcc --version | head -1'
```

Verified output:

```
Python 3.14.7
go version go1.27.1 linux/arm64
uv 0.12.17 (aarch64-unknown-linux-musl)
gcc (Debian 14.2.0-19) 14.2.0
```

The image is built with `UV_NO_DEV=1`, so pytest is not installed. Open a shell with dev dependencies enabled, then sync and run the suite. The shell starts in `/app/gonpypoc`:

```bash
docker run --rm -it -e UV_NO_DEV=0 --entrypoint bash gonpypoc
```

```bash
uv sync --locked --no-editable
uv run pytest
```

See the [uv Docker guide](https://docs.astral.sh/uv/guides/integration/docker/) for more on this layout.
