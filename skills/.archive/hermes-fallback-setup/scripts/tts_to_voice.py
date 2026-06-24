#!/usr/bin/env python3
"""TTS → SILK pipeline: generate speech then convert to WeChat-native voice.

Usage:  python3 tts_to_voice.py "text to speak" [output.silk]

Requires: pip install edge-tts silk-python, brew install ffmpeg
"""
import sys, os, asyncio, subprocess, tempfile, io, wave
import edge_tts

async def generate_tts(text, voice="zh-CN-XiaoxiaoNeural", output=None):
    if output is None:
        output = tempfile.mktemp(suffix=".mp3")
    await edge_tts.Communicate(text, voice).save(output)
    return output

def mp3_to_silk(mp3_path, silk_path=None):
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
        out_buf = io.BytesIO()
        pysilk.encode(io.BytesIO(pcm), out_buf, sr, 24000, tencent=True)
        with open(silk_path, 'wb') as f:
            f.write(out_buf.getvalue())
        return silk_path
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)

async def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    text = sys.argv[1]
    silk = sys.argv[2] if len(sys.argv) > 2 else tempfile.mktemp(suffix=".silk")
    mp3 = await generate_tts(text)
    try:
        result = mp3_to_silk(mp3, silk)
    finally:
        if os.path.exists(mp3):
            os.unlink(mp3)
    print(f"✅ {result} ({os.path.getsize(result)/1024:.1f} KB)")
    print(f"   Include MEDIA:{result} in response for WeChat voice bubble.")

if __name__ == "__main__":
    asyncio.run(main())
