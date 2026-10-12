# Latest stable Python (3.14.7) and Go (1.27.1) on Debian Trixie.
# Go is copied from the official image so both toolchains share the same libc.
ARG PYTHON_IMAGE=python:3.14.7-slim-trixie
ARG GO_IMAGE=golang:1.27.1-trixie
ARG UV_IMAGE=ghcr.io/astral-sh/uv:latest

FROM ${GO_IMAGE} AS go
FROM ${UV_IMAGE} AS uv
FROM ${PYTHON_IMAGE}

COPY --from=go /usr/local/go /usr/local/go
COPY --from=uv /uv /uvx /bin/

# gcc and related tools are required for cgo when building Go shared libraries.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/local/go/bin:${PATH}" \
    GOPATH=/go \
    GOTOOLCHAIN=local \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_NO_DEV=1

WORKDIR /app
COPY gonpypoc /app/gonpypoc
COPY cgotopypoc /app/cgotopypoc

WORKDIR /app/cgotopypoc
RUN go build -buildmode=c-shared -o libcgotopypoc.so .

WORKDIR /app/gonpypoc
RUN uv sync --locked --no-editable

ENV PATH="/app/gonpypoc/.venv/bin:${PATH}" \
    CGOTOPYPOC_DIR=/app/cgotopypoc

CMD ["gonpypoc"]
