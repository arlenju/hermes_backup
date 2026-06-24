#!/usr/bin/env python3
"""
MP3 → SILK v3 converter for WeChat native voice messages.

Usage:
  python3 mp3_to_silk.py input.mp3 [output.silk]

Dependencies:
  pip install silk-python
  brew install ffmpeg
"""

import sys
import os
import subprocess
import tempfile
import io


def convert(mp3_path: str, silk_path: str = None) -> str:
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(mp3_path)
    if silk_path is None:
        silk_path = os.path.splitext(mp3_path)[0] + ".silk"

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path,
             "-ar", "24000", "-ac", "1", "-sample_fmt", "s16", wav_path],
            check=True, capture_output=True, timeout=30,
        )
        import wave
        with wave.open(wav_path, 'rb') as wf:
            pcm_data = wf.readframes(wf.getnframes())
            sample_rate = wf.getframerate()
        print(f"  WAV: {sample_rate}Hz, {len(pcm_data)} bytes")

        import pysilk
        pcm_buf = io.BytesIO(pcm_data)
        out_buf = io.BytesIO()
        pysilk.encode(pcm_buf, out_buf, sample_rate, 24000)
        with open(silk_path, 'wb') as f:
            f.write(out_buf.getvalue())

        mp3_size = os.path.getsize(mp3_path)
        silk_size = os.path.getsize(silk_path)
        print(f"\nOK: {silk_path} ({silk_size/1024:.1f} KB, {silk_size/mp3_size*100:.0f}%)")
        return silk_path
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
