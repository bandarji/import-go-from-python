# Call Go Functions From Python

Or, `import go` into Python. Proof of concept efforts comprise the source
code and documentation in this repository. Further, the content here exists
for demonstration purposes only, primarily constructed for a [/dev/reno][dr]
lightning talk.

If you have contributions, issues or questions, please submit those to this
repository. As a guide more than a guru, I want to learn with the help of
others.

## Requirements

- [uv][wwwuv] v0.12 used for virtual environment and package management
- [Go][wwwgo] v1.26 used for Go compilation
- [Git][wwwgit] v2.54.0 used for revision control
- [Docker][wwwdocker] v29.6.2 used for Linux execution and testing

Technically, execution and testing does not require Docker. This repository
employs Docker to best ensure this code executes in the same manner when
done from my laptop or from yours.

## Initial Project Setup (Already Done)

These commands created the `gonpypoc` Python package from the repository root.

Initialized a uv **package** project in a subdirectory. `--vcs none` avoided
nesting a second git repo. `--no-workspace` created a standalone project
instead of attaching to a uv workspace.

```bash
uv init gonpypoc \
  --name gonpypoc \
  --package \
  --vcs none \
  --description "Proof of concept for importing Go code in Python programs" \
  --no-workspace
```

These commands created the virtual environment, resolved dependencies and
installed the package in editable mode.

```bash
cd gonpypoc
uv sync
```

**Result**

- Python v3.14.7 (from `.python-version`)
- a local `.venv` under `gonpypoc/`
- `uv.lock` frozen dependencies
- Editable installation of `gonpypoc==0.1.0`

## Layout

```
cgotopypoc/
  go.mod                # Go module
  returns.go            # CGO exports for each compatible Python return type
  record.go             # Go Record struct and its CGO exports
gonpypoc/
  pyproject.toml        # project metadata and build backend
  uv.lock               # locked dependency set
  .python-version       # pinned interpreter (v3.14)
  src/gonpypoc/
    __init__.py         # package entry; runs the CGO assertions
    cgotopypoc.py       # builds, loads and asserts the shared library
  tests/
    conftest.py         # shared pytest fixture that loads the CGO library
    test_cgotopypoc.py  # Unit tests (pytest)
    test_go_returns.py  # Unit tests (pytest)
```

The `.gitignore` file will not save superfluous files to the repository.

## Testing

This repository uses [`pytest`][wwwpytest] to validate Go functions responses
from Python invocations. The `uv` tool installs `pytest` as a development
dependency. The following steps installed the test tooling and executed tests.

```bash
cd gonpypoc
uv add --dev pytest
uv run pytest
```

## CGO Shared Library

The Go package `cgtopypoc` contains functions built into a
[shared library][cgobm]. Each exported function returns a C-compatible value
that Python imports through [`ctypes`][ctypes].

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


### Go Structures

`record.go` defines a Go struct with three distinct field types. CGO rejects
a Go struct in an `//export` signature
(`Go type not supported in export: struct`), so the exported functions copy
`Record` to and from `CRecord`, a C struct with the same field order and
sizes. Python declares that layout as `ctypes.Structure` `CRecord` and reads
the value as the `Record` named tuple.

| Go field | Go type | C field | C type | Python field | Python type | Offset |
| --- | --- | --- | --- | --- | --- | --- |
| `Count` | `int64` | `count` | `int64_t` | `count` | `int` | 0 |
| `Ratio` | `float64` | `ratio` | `double` | `ratio` | `float` | 8 |
| `Ready` | `bool` | `ready` | `unsigned char` | `ready` | `bool` | 16 |

The boolean `Ready` gets stored as `0` or `1`. Any non-zero `ready` ends up
`true`. `RecordSize` returns `unsafe.Sizeof(Record{})` and that value matches
`ctypes.sizeof(CRecord)`: 24 bytes on this ABI.

| Export | Direction | Behavior |
| --- | --- | --- |
| `ReturnRecord` | Go to Python | Builds `Record{Count: -7, Ratio: 2.5, Ready: true}` and returns the copy |
| `EchoRecord` | Python to Go to Python | Copies the incoming `CRecord` into `Record` and returns that copy |
| `RecordScore` | Python to Go | Returns `Count * Ratio` when `Ready` is set, otherwise `0` |
| `RecordSize` | Go to Python | Returns the Go struct size in bytes |

`EchoRecord` and `RecordScore` both construct the Go struct before producing a
result, so a mismatched field order or width fails those checks. Tests for
each export remain in `gonpypoc/tests/test_go_returns.py`.

### Building The Go Module

Created the Go module (from the repository root):

```bash
mkdir -p cgotopypoc
cd cgotopypoc
go mod init cgotopypoc
```

The Go version appears in `go.mod`.

Mac OS produces a `.dylib` extension for the shared library. Linux creates
a `.so` file. Windows probably writes a `.dll` file, but I have no way to
verify that.

```bash
# macOS (executed locally on my development laptop)
cd cgotopypoc
CGO_ENABLED=1 go build -buildmode=c-shared -o libcgotopypoc.dylib .

# Linux (executed in the Docker container)
cd cgotopypoc
CGO_ENABLED=1 go build -buildmode=c-shared -o libcgotopypoc.so .
```

**Reference Documentation**

- [Command cgo][ccgo]
- [Calling Go from Python via C][pycgo]

## Docker

The `Dockerfile` builds a Linux image with the latest stable Python and Go,
plus uv, the `gonpypoc` package and a prebuilt `cgotopypoc` shared library.

| Tool | Version | Source |
| --- | --- | --- |
| Python | v3.14.7 | [`python:3.14.7-slim-trixie`][dpyimage] |
| Go | v1.27.1 | copied from [`golang:1.27.1-trixie`][dgoimage] |
| uv | latest | copied from [`ghcr.io/astral-sh/uv:latest`][duv] |

For CGO to compile the shared library, the Docker container includes the
`build-essential` package.

[dr]: https://www.meetup.com/dev-reno/
[wwwuv]: https://docs.astral.sh/uv/getting-started/installation/
[wwwgo]: https://go.dev/doc/install
[wwwgit]: https://git-scm.com/install/
[wwwdocker]: https://docs.docker.com/get-started/get-docker/
[cgobm]: https://pkg.go.dev/cmd/go#hdr-Build_modes
[ctypes]: https://docs.python.org/3/library/ctypes.html
[ccgo]: https://pkg.go.dev/cmd/cgo
[pycgo]: https://pkg.go.dev/cmd/cgo#hdr-C_references_to_Go
[dpyimage]: https://hub.docker.com/_/python
[dgoimage]: https://hub.docker.com/_/golang
[duv]: https://docs.astral.sh/uv/guides/integration/docker/
