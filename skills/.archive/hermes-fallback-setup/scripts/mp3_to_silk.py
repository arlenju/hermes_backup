#!/usr/bin/env python3
"""MP3 → SILK v3 converter for WeChat native voice messages.

Usage:  python3 mp3_to_silk.py input.mp3 [output.silk]

Requires: pip install silk-python, brew install ffmpeg
"""
import sys, os, subprocess, tempfile, io, wave

def convert(mp3_path, silk_path=None):
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(mp3_path)
    if silk_path is None:
        silk_path = os.path.splitext(mp3_path)[0] + ".silk"

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name
    try:
        subprocess.run(["ffmpeg", "-y", "-i", mp3_path, "-ar", "24000",
                        "-ac", "1", "-sample_fmt", "s16", wav_path],
                       check=True, capture_output=True, timeout=30)
        with wave.open(wav_path, 'rb') as wf:
            pcm = wf.readframes(wf.getnframes())
            sr = wf.getframerate()
        import pysilk
        pysilk.encode(io.BytesIO(pcm), io.BytesIO(), sr, 24000, tencent=True)
        # pysilk.encode writes to second arg; re-read from actual output
        out_buf = io.BytesIO()
        pysilk.encode(io.BytesIO(pcm), out_buf, sr, 24000, tencent=True)
        with open(silk_path, 'wb') as f:
            f.write(out_buf.getvalue())
        return silk_path
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    result = convert(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"✅ {result} ({os.path.getsize(result)/1024:.1f} KB)")
