#!/bin/bash
# ==========================================
# MLX ASR wrapper for Hermes command provider
# Hermes calls this with:
#   {input_path} -> audio file path
#   {model}      -> model name/size
#   {language}   -> language code
#
# Output: transcription text on stdout
# ==========================================

MODEL_PATH="$HOME/.lmstudio/models/mlx-community/Qwen3-ASR-0.6B-8bit"
INPUT="$1"

if [ ! -f "$INPUT" ]; then
    echo "ERROR: audio file not found: $INPUT" >&2
    exit 1
fi

OUTPUT_DIR=$(mktemp -d)
OUTPUT_PREFIX="$OUTPUT_DIR/result"
OUTPUT_FILE="$OUTPUT_PREFIX.txt"

source "$HOME/.hermes/hermes-agent/venv/bin/activate"
python3 -m mlx_audio.stt.generate \
    --model "$MODEL_PATH" \
    --audio "$INPUT" \
    --output-path "$OUTPUT_PREFIX" \
    --format txt \
    --language zh 2>/dev/null

if [ -f "$OUTPUT_FILE" ]; then
    cat "$OUTPUT_FILE"
else
    echo "ERROR: transcription failed" >&2
    exit 1
fi

rm -rf "$OUTPUT_DIR"
