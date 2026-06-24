#!/usr/bin/env python3
"""
MP3 → SILK v3 转换脚本
用于将 TTS 生成的 MP3 音频转为微信原生语音消息格式（SILK v3）

用法:
  python3 mp3_to_silk.py input.mp3 [output.silk]

依赖:
  pip install silk-python
  brew install ffmpeg
"""

import sys
import os
import subprocess
import tempfile
import io


def mp3_to_silk(mp3_path: str, silk_path: str = None) -> str:
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"Input not found: {mp3_path}")
    if silk_path is None:
        silk_path = os.path.splitext(mp3_path)[0] + ".silk"
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name
    try:
        # MP3 → WAV (24 kHz, mono, 16-bit)
        print(f"[1/3] Decoding MP3 → WAV")
        subprocess.run(["ffmpeg", "-y", "-i", mp3_path, "-ar", "24000",
                        "-ac", "1", "-sample_fmt", "s16", wav_path],
                       check=True, capture_output=True, timeout=30)
        # WAV → PCM
        import wave
        with wave.open(wav_path, 'rb') as wf:
            pcm_data = wf.readframes(wf.getnframes())
            sample_rate = wf.getframerate()
        print(f"      {sample_rate}Hz, {len(pcm_data)} bytes PCM")
        # PCM → SILK (tencent mode for WeChat compat)
        import pysilk
        pcm_buf = io.BytesIO(pcm_data)
        out_buf = io.BytesIO()
        pysilk.encode(pcm_buf, out_buf, sample_rate, 24000, tencent=True)
        with open(silk_path, 'wb') as f:
            f.write(out_buf.getvalue())
        mp3_sz = os.path.getsize(mp3_path)
        silk_sz = os.path.getsize(silk_path)
        print(f"✅ {silk_path} ({silk_sz/1024:.1f} KB, {silk_sz/mp3_sz*100:.0f}% of MP3)")
        return silk_path
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    mp3_to_silk(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
