---
name: apple-container
description: |-
  Run Linux containers as lightweight microVMs on macOS via Apple's native
  `container` CLI (Apple Silicon + macOS 26+ only). Use this skill whenever the
  user wants to: run/test/debug something in an isolated Linux environment,
  spin up a throwaway shell/Python/Node, sandbox a suspicious or untrusted
  tool/repo (maigret, scraping CLIs, freshly-cloned GitHub projects),
  cross-compile/test for Linux, or anything phrased as
  「在容器/沙箱里跑 X」「隔离环境跑 X」「用 docker 跑一下 X」
  「跑个 Linux 环境试 X」「跑个 ubuntu/alpine 容器」on this Mac.

  Apple's container is OCI-compatible (pulls from Docker Hub / ghcr / etc.) but
  has different defaults from `docker`: each container is its own microVM,
  not a shared-kernel container. Wrapping `--rm` is the default cleanup pattern.

  NOT for: Intel Macs, macOS 25 or older, Windows containers, full
  docker-compose multi-service stacks (the toolchain doesn't exist yet at 1.0).
  For those, fall back to telling the user to use Docker Desktop or Colima.
metadata:
  version: 1.0.0
  tags: [docker, container, apple, macos, microvm, sandbox, isolation, devops]
---

# Apple Container — Linux containers as microVMs on macOS

`container` is Apple's official native container runtime: Swift-written,
Apple-Silicon-optimized, **one microVM per container**, no Docker Desktop,
no daemon GUI, Apache 2.0. Installed at `/usr/local/bin/container` on this
machine.

## Prerequisites — check first

```bash
container --version              # Should print "container CLI version 1.0.0" or newer
container system status          # Must show "status: running"
```

If `status` is not running, start it: `container system start`.
If kernel is missing, install it: `container system kernel set --recommended --force`.

If `container` is not found, the tool isn't installed. Tell the user
to download the .pkg from <https://github.com/apple/container/releases/latest>
and install it (requires macOS 26+ on Apple Silicon).

## Core workflows

### Run a one-shot command and clean up

```bash
container run --rm <image> <command>
# example
container run --rm alpine:latest uname -a
container run --rm python:3.12-slim python -c "print(1+1)"
```

Always use `--rm` so the microVM is destroyed when the command exits.
Without `--rm`, stopped containers stay around and waste disk.

### Interactive shell

```bash
container run --rm -it <image> <shell>
# example
container run --rm -it ubuntu:24.04 bash
container run --rm -it alpine:latest sh
```

### Mount a host directory (most common pattern)

```bash
container run --rm -v "$PWD":/work -w /work <image> <cmd>
# Mount $PWD into the container at /work, cd into it, run command.
# Files created in /work are visible on the host.
```

Use absolute paths when mounting. `~` and `$PWD` work because the shell
expands them before `container` sees them.

### Build / sandbox an untrusted tool

```bash
# Example: run maigret without polluting the host's Python env
container run --rm -v "$PWD/reports":/reports python:3.12-slim sh -c \
  "pip install -q maigret && maigret USERNAME --html --folderpath /reports"
```

### Image management

```bash
container image list             # what's cached locally
container pull <image>           # pre-pull (otherwise first `run` pulls implicitly)
container image remove <name>    # free disk
```

### Running containers / processes

```bash
container ps                     # what's running right now
container exec <id> <cmd>        # exec into a running container
container stop <id>              # graceful stop
container kill <id>              # force kill
```

## Default flags worth knowing

| Flag | Effect |
|------|--------|
| `--rm` | Delete container when it exits (use this by default) |
| `-it` | Interactive + TTY (for shells / REPLs) |
| `-v HOST:CONTAINER` | Bind-mount; use absolute paths |
| `-w PATH` | Set working directory inside container |
| `-e KEY=VAL` | Pass env vars |
| `-p HOST:CONTAINER` | Port forward (host port → container port) |
| `--memory 2g` | Cap memory |
| `--cpus 2` | Cap CPU |

## Differences from `docker` to remember

- **Each container is its own microVM**, not a shared-kernel container.
  Stronger isolation, slightly higher per-container startup cost
  (≈ 2 s warm, ≈ 10 s cold on first pull).
- **No `docker-compose` equivalent at 1.0.** For multi-service apps, either
  script the orchestration yourself or fall back to Docker Desktop / Colima.
- **No daemon GUI.** Pure CLI. State is managed by `container-apiserver`,
  started/stopped via `container system start|stop`.
- **First-time cost:** the very first `container run` may take 10–30 s to
  pull the image and initialise. Subsequent runs of the same image are fast.
- **Linux-only containers.** No Windows containers, no native macOS containers.
- **`--platform`** defaults to linux/arm64/v8 on Apple Silicon. To run an
  amd64 image (Rosetta-emulated, slower), pass `--platform linux/amd64`.

## Pitfalls observed in practice

1. **`container system start` prompts for kernel install on a fresh machine.**
   Non-interactive cron / agent invocations will hang at the prompt. Run
   `container system kernel set --recommended --force` once at setup time so
   future starts are silent.
2. **First pull is slow on slow networks.** A 60 MB ubuntu image at 2 MB/s
   takes 30 s. Budget for it on cold runs. After the first pull, the image
   is cached under `~/Library/Application Support/com.apple.container/`.
3. **Filesystem mounts must be absolute paths.** Relative paths silently fail
   to mount what you expect. Always expand with `$PWD` or `realpath`.
4. **No `latest` re-pull by default.** `container run alpine` uses the cached
   image. To force a fresh pull, run `container pull alpine:latest` first.
5. **`--platform linux/amd64` works but is slow.** Use only when the image
   genuinely lacks an arm64 variant.
6. **Container hostnames are random UUIDs.** Not configurable to a friendly
   name via a `--name`-equivalent flag in 1.0; if the user needs deterministic
   names for service discovery, fall back to Docker.
7. **Don't run `container system start` repeatedly.** It's idempotent but
   re-issues the kernel-install prompt on first-ever launch. Check
   `container system status` first.
8. **0.x → 1.0 breaking changes happened recently.** UserDefault-backed system
   properties were replaced by a TOML config in 1.0. If user has an old config,
   point them at the [migration tutorial](https://github.com/apple/container/blob/main/docs/tutorials).

## When NOT to use this skill

- **Intel Mac** → tell the user `container` is Apple-Silicon-only; suggest
  Docker Desktop or Colima.
- **macOS 25 or older** → `container` needs macOS 26 virtualization APIs;
  suggest Docker Desktop or Colima.
- **Production deployment** → 1.0 is fresh and breaking changes may continue
  through 1.x. Use Docker / Podman / Colima for anything that must be stable.
- **Multi-service stacks (frontend + DB + redis)** → no compose at 1.0.
  Use Docker Desktop or write a manual orchestration shell script.
- **Need to share a running daemon with VSCode / other Docker-aware tools** →
  most IDE Docker integrations expect a Docker socket; `container` doesn't
  publish one in a compatible shape. Fall back to Docker.

## Quick recipes

### Throwaway Python REPL with packages

```bash
container run --rm -it python:3.12-slim sh -c "pip install -q ipython requests && ipython"
```

### Test a Linux build of the current repo

```bash
container run --rm -v "$PWD":/src -w /src ubuntu:24.04 bash -c \
  "apt update -q && apt install -y -q build-essential && make"
```

### Run a one-off Node.js script in isolation

```bash
container run --rm -v "$PWD":/work -w /work node:20 node script.js
```

### Inspect a suspicious tarball / repo without trusting it

```bash
mkdir -p /tmp/sandbox && tar -xzf suspect.tar.gz -C /tmp/sandbox
container run --rm -it -v /tmp/sandbox:/payload:ro -w /payload ubuntu:24.04 bash
# Read-only mount + microVM isolation. Exit closes the VM.
```

### Run maigret (OSINT username search) without polluting host Python

```bash
mkdir -p reports
container run --rm -v "$PWD/reports":/out python:3.12-slim sh -c \
  "pip install -q maigret && maigret YOUR_USERNAME --html --folderpath /out"
# Report appears in ./reports/ on the host.
```

## See also

- Official docs: <https://github.com/apple/container/blob/main/docs/how-to.md>
- Command reference: <https://github.com/apple/container/blob/main/docs/command-reference.md>
- For Hermes integration (running cron tasks inside containers), see the
  `terminal.backend: docker` config option in `~/.hermes/config.yaml` —
  Apple `container` is OCI-compatible so it can serve as the backend, but
  Hermes's `terminal_tool` codepath was written against the Docker CLI and
  may need adapter shims. Default to keeping `terminal.backend: local` and
  invoking `container run` explicitly from inside agent commands.
