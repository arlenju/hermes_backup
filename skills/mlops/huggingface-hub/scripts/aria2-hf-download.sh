#!/usr/bin/env bash
# aria2-hf-download.sh — Reliable HF download for one file using aria2c.
#
# Use when `hf download` stalls on the Xet bridge / CDN. Resolves the final
# signed CDN URL once with curl, then hands it to aria2c with --continue and
# stall detection. Supports resuming from an existing partial.
#
# Usage:
#   bash aria2-hf-download.sh <repo_id> <local_dir> <filename>
#
# Example:
#   bash aria2-hf-download.sh \
#     mlx-community/Qwen3-VL-8B-Instruct-6bit \
#     ~/.lmstudio/models/mlx-community/Qwen3-VL-8B-Instruct-6bit \
#     model-00001-of-00002.safetensors

set -euo pipefail

REPO_ID="${1:?repo_id required, e.g. mlx-community/Qwen3-VL-8B-Instruct-6bit}"
LOCAL_DIR="${2:?local_dir required}"
FILENAME="${3:?filename required, e.g. model-00001-of-00002.safetensors}"

# Prefer Motrix's bundled aria2c (always present on the host) over PATH.
ARIA="${ARIA2C:-}"
if [[ -z "$ARIA" ]]; then
  if [[ -x /Applications/Motrix.app/Contents/Resources/engine/aria2c ]]; then
    ARIA=/Applications/Motrix.app/Contents/Resources/engine/aria2c
  elif command -v aria2c >/dev/null 2>&1; then
    ARIA="$(command -v aria2c)"
  else
    echo "aria2c not found. Install via 'brew install aria2' or Motrix." >&2
    exit 1
  fi
fi

mkdir -p "$LOCAL_DIR"
cd "$LOCAL_DIR"

# Follow the 302/308 chain to the signed CDN URL.
HF_URL="https://huggingface.co/${REPO_ID}/resolve/main/${FILENAME}?download=true"
echo "▶ Resolving CDN URL for ${FILENAME}..."
CDN_URL=$(curl -sIL -o /dev/null -w "%{url_effective}" "$HF_URL")
if [[ -z "$CDN_URL" || "$CDN_URL" == "$HF_URL" ]]; then
  echo "Failed to resolve CDN URL." >&2
  exit 1
fi
echo "  → ${CDN_URL:0:90}..."

echo "▶ Downloading with aria2c (16 connections, 20 retries, stall guard)..."
"$ARIA" \
  -x 16 -s 16 -k 1M \
  --file-allocation=none \
  --continue=true \
  --max-tries=20 \
  --retry-wait=10 \
  --connect-timeout=30 \
  --timeout=60 \
  --lowest-speed-limit=100K \
  --console-log-level=warn \
  --summary-interval=30 \
  -o "$FILENAME" \
  "$CDN_URL"

echo "✅ ${FILENAME} complete:"
ls -lh "$FILENAME"
[[ -e "${FILENAME}.aria2" ]] && echo "⚠️  ${FILENAME}.aria2 still present — download did not complete cleanly" || true
