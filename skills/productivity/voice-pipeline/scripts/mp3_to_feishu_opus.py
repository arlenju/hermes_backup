#!/usr/bin/env python3
"""
Convert an MP3 file to OGG Opus for Feishu native voice bubbles.

Usage:
    python3 mp3_to_feishu_opus.py input.mp3 [output.opus]

Dependencies:
    ffmpeg (must be on PATH, libopus encoder)

The output Opus file can be sent as a Feishu native voice bubble
by including MEDIA:/path/to/output.opus in the agent's response.
"""

import sys
import subprocess
import os

def convert_mp3_to_opus(input_path: str, output_path: str | None = None) -> str:
    if not os.path.exists(input_path):
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if output_path is None:
        basename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = f"{basename}.opus"

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c:a", "libopus",
        "-b:a", "24k",
        "-ar", "24000",
        "-ac", "1",
        "-y",  # overwrite
        output_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        print("Error: ffmpeg not found. Install it first:", file=sys.stderr)
        print("  brew install ffmpeg    # macOS", file=sys.stderr)
        print("  apt install ffmpeg      # Debian/Ubuntu", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: ffmpeg timed out", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"Error: ffmpeg failed (exit {result.returncode})", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = convert_mp3_to_opus(input_path, output_path)
    print(f"OK: {result}")
