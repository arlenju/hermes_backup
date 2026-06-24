---
name: huggingface-large-model-download
description: Download large HF models fast/reliably when hf-cli stalls — aria2c against signed CDN URL, xet pitfalls, mirror caveats.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [huggingface, download, aria2c, mlx, vlm, gguf]
---

# huggingface-large-model-download

When the user is downloading a multi-GB model from HuggingFace and **hf-cli is slow, stalling, or has already stalled silently**, this skill applies. Common symptoms:

- `hf download …` running at 3-4 MB/s with `Warning: You are sending unauthenticated requests to the HF Hub.`
- Hours pass, `.cache/huggingface/download/*.incomplete` files stop growing, TCP connection shows `CLOSED` but the python process is still alive.
- `hf-mirror.com` returns `HTTP/2 308` redirecting back to `huggingface.co` (the mirror has not cached this artifact).

## Default path: aria2c against the signed CDN URL

Skip hf-cli for the *big* files. Get the signed CDN URL once and feed it to `aria2c -x 16`. Works because HF's CDN (us.aws.cdn.hf.co) hands out a pre-signed URL that aria2c can hammer with parallel range requests.

```bash
# 1. Resolve the 302 → signed CDN URL (curl follows redirects, reports the final URL)
URL=$(curl -sIL -o /dev/null -w "%{url_effective}" \
  "https://huggingface.co/<org>/<repo>/resolve/main/<file>.safetensors")

# 2. aria2c, 16 connections, auto-resume, no pre-allocation (sparse files)
aria2c -x 16 -s 16 -k 1M --file-allocation=none --continue=true --max-tries=10 \
  --connect-timeout=30 --timeout=60 \
  --console-log-level=warn --summary-interval=20 \
  -o <file>.safetensors "$URL"
```

On macOS Motrix users have aria2c pre-bundled at `/Applications/Motrix.app/Contents/Resources/engine/aria2c` — use that path directly, no `brew install aria2` needed.

For multi-shard models, kick both shards off in parallel with `& … & wait`. Each gets 16 connections.

## Always do hf-cli FIRST for the metadata

Don't try to hand-download `config.json` / `tokenizer.json` / `chat_template.json` etc. one by one. Run `hf download <repo> --local-dir <dir>` ONCE; it will pull all the small files (and stub out the big ones). Then kill it, find the two or three `*.safetensors` / `*.gguf` files that are still missing or sparse, and aria2c them as above.

The resulting directory (small metadata files from hf, big shards from aria2c, all sharing the same `<local-dir>`) is bit-identical to a clean hf download and `mlx_vlm` / `mlx_lm` / `transformers` / LM Studio will all consume it unchanged.

## Pitfalls

### 🚨 Never `HF_HUB_DISABLE_XET=1` mid-download

Hf-hub ≥ 0.30 uses the xet protocol — partial downloads land as `Dr_lZJDwE1cnGAQMwA77jJEQIk8=.<hash>.<segment>.incomplete` shards under `.cache/huggingface/download/`. Setting `HF_HUB_DISABLE_XET=1` and rerunning `hf download` will *discard those shards* and start from zero. If a hf-cli run accumulated several GB and you want to switch transports, **leave the xet shards alone and go straight to aria2c on the missing top-level files** — do not try to coax hf-cli to fall back to plain HTTPS, you'll lose the cache.

### `hf-mirror.com` does NOT always help

The mirror only helps when it has the artifact pre-cached. For popular models (Qwen, Llama, DeepSeek base weights) it works. For niche mlx-community or unsloth re-quants, the mirror returns `HTTP/2 308 Location: https://huggingface.co/...` — meaning the request gets bounced back to the main site at the user's original speed.

Test before committing:
```bash
curl -sI "https://hf-mirror.com/<org>/<repo>/resolve/main/<file>" | head -3
# HTTP/2 308 → mirror won't help; HTTP/2 302/200 + AWS/Cloudflare CDN → mirror helps
```

### Stalls are silent

A stalled `hf download` keeps the python process alive but TCP shows `CLOSED`. The user will not see an error; they will see `running` in `process(action='poll')`. When unsure, run:
```bash
lsof -p <pid> | grep ESTABLISHED   # zero lines = no active downloads
ls -lhT <local-dir>/.cache/huggingface/download/*.incomplete   # check mtime
```
Mtime > 2 minutes old + zero ESTABLISHED → stalled. Kill and switch to aria2c.

### Set HF_TOKEN if staying on hf-cli

Unauthenticated rate limits cap throughput around 3-4 MB/s and trigger more frequent disconnects. If the user has a token, `export HF_TOKEN=hf_...` before `hf download` typically 3-5× the speed. But on a slow/uncached path, aria2c+CDN-signed-URL still beats authenticated hf-cli.

## Where the file lives after download

Hermes-friendly conventions on macOS:
- LM Studio + MLX shared models: `~/.lmstudio/models/<org>/<repo>/`
- GGUF for llama.cpp: `~/.lmstudio/models/<org>/<repo>/` (LM Studio also reads it)
- Raw safetensors for mlx_vlm / transformers: same dir works (`mlx_vlm.generate --model ~/.lmstudio/models/mlx-community/Qwen3-VL-8B-Instruct-6bit ...`)

Keep models under `~/.lmstudio/models/` even when serving via mlx_vlm directly — one canonical place, LM Studio sees them automatically if the user wants to switch backends later.

## Background-job hygiene

Long downloads MUST use `terminal(background=True, notify_on_complete=True)`. Without the notify flag the process runs silently and you'll forget it. Poll progress with `du -sh <local-dir>` (not `ls -lh`) — aria2c creates sparse files where `ls` lies about the real bytes-on-disk.

## Verification before declaring success

```bash
# Final filesizes match the HF page
ls -lh <local-dir>/*.safetensors
# Read the index
cat <local-dir>/model.safetensors.index.json | head -5
# Optional: sha256 spot-check on the first shard
shasum -a 256 <local-dir>/model-00001-of-*.safetensors
```

Cross-reference filesizes with the HF model card "Files and versions" tab before telling the user it's done.
