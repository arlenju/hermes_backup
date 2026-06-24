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

def mp3_to_silk(mp3_path: str, silk_path: str = None) -> str:
    """将 MP3 文件转换为 SILK v3 格式"""

    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"输入文件不存在: {mp3_path}")

    if silk_path is None:
        silk_path = os.path.splitext(mp3_path)[0] + ".silk"

    # Step 1: MP3 → WAV (24kHz, 16-bit, mono — SILK 最佳参数)
    print(f"[1/3] 解码 MP3 → WAV: {mp3_path}")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        wav_path = tmp_wav.name

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path,
             "-ar", "24000",
             "-ac", "1",
             "-sample_fmt", "s16",
             wav_path],
            check=True, capture_output=True, timeout=30
        )

        # Step 2: WAV → PCM
        print(f"[2/3] 读取 PCM 数据: {wav_path}")
        import wave
        with wave.open(wav_path, 'rb') as wf:
            assert wf.getnchannels() == 1, "需要单声道音频"
            assert wf.getsampwidth() == 2, "需要 16-bit 音频"
            sample_rate = wf.getframerate()
            pcm_data = wf.readframes(wf.getnframes())

        print(f"     采样率: {sample_rate}Hz, 数据大小: {len(pcm_data)} bytes")

        # Step 3: PCM → SILK via pysilk
        print(f"[3/3] 编码 PCM → SILK: {silk_path}")
        import pysilk
        import io
        pcm_buf = io.BytesIO(pcm_data)
        out_buf = io.BytesIO()
        pysilk.encode(pcm_buf, out_buf, sample_rate, 24000)

        with open(silk_path, 'wb') as f:
            f.write(out_buf.getvalue())

        silk_size = os.path.getsize(silk_path)
        mp3_size = os.path.getsize(mp3_path)
        ratio = silk_size / mp3_size * 100 if mp3_size > 0 else 0

        print(f"\n✅ 转换完成！")
        print(f"   源文件: {mp3_path} ({mp3_size/1024:.1f} KB)")
        print(f"   SILK:   {silk_path} ({silk_size/1024:.1f} KB, {ratio:.0f}%)")

        return silk_path

    except Exception as e:
        print(f"❌ 转换失败: {e}", file=sys.stderr)
        raise
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    mp3_path = sys.argv[1]
    silk_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = mp3_to_silk(mp3_path, silk_path)
    print(f"\n输出: {result}")

    # 验证文件头
    with open(result, 'rb') as f:
        header = f.read(10)
    if header[:1] == b'\x02':
        print("✅ SILK 文件头验证通过")
    else:
        print(f"⚠️  文件头: {header[:8].hex()}")


if __name__ == "__main__":
    main()
