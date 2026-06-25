#!/bin/bash
# Hermes auxiliary OCR using PP-OCRv6.
# Usage: ~/.hermes/scripts/ocr_image.sh /path/to/image.jpg [--json]
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Usage: $0 IMAGE [--json]" >&2
  exit 2
fi
source "$HOME/.hermes/ocr_ppocrv6/venv/bin/activate"
python "$HOME/.hermes/ocr_ppocrv6/ocr_image.py" "$@"
