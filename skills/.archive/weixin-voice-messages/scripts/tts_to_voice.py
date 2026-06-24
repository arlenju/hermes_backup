#!/usr/bin/env python3
"""
TTS → SILK 一体化脚本：生成语音并转为微信原生语音格式

用法:
  python3 tts_to_voice.py "要说的文字" [output.silk]

依赖:
  pip install silk-python edge-tts
  brew install ffmpeg
"""

import sys
import os
import asyncio
import subprocess
import tempfile
import io


async def generate_tts(text: str, voice: str = "zh-CN-XiaoxiaoNeural", output: str = None) -> str:
    """Use Edge TTS to generate MP3 audio."""
    if output is None:
        output = tempfile.mktemp(suffix=".mp3")
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output)
    size = os.path.getsize(output)
    print(f"  TTS OK: {output} ({size/1024:.1f} KB)")
    return output


def mp3_to_silk(mp3_path: str, silk_path: str = None) -> str:
    """Convert MP3 to SILK v3 via WAV intermediate."""
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
        import pysilk
        pcm_buf = io.BytesIO(pcm_data)
        out_buf = io.BytesIO()
        pysilk.encode(pcm_buf, out_buf, sample_rate, 24000)
        with open(silk_path, 'wb') as f:
            f.write(out_buf.getvalue())
        mp3_size = os.path.getsize(mp3_path)
        silk_size = os.path.getsize(silk_path)
        print(f"  SILK OK: {silk_path} ({silk_size/1024:.1f} KB, {silk_size/mp3_size*100:.0f}%)")
        return silk_path
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)


async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    text = sys.argv[1]
    silk_path = sys.argv[2] if len(sys.argv) > 2 else tempfile.mktemp(suffix=".silk")
    if not silk_path.lower().endswith(".silk"):
        silk_path += ".silk"
    print(f'Text: "{text}"')
    mp3_file = await generate_tts(text)
    try:
        result = mp3_to_silk(mp3_file, silk_path)
    finally:
        if os.path.exists(mp3_file):
            os.unlink(mp3_file)
    print(f"\nDone: {os.path.abspath(result)}")
    print(f"Send with: MEDIA:{os.path.abspath(result)}")


if __name__ == "__main__":
    asyncio.run(main())
