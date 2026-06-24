---
name: tts-to-silk-wechat-voice
description: "Convert TTS audio to SILK format for native WeChat voice message delivery. Uses edge-tts + ffmpeg + pysilk."
version: 1.0.0
author: hermes-agent
platforms: [macos, linux]
prerequisites:
  commands: [ffmpeg]
  python_packages: [edge-tts, silk-python]
---

# TTS → SILK — WeChat Native Voice Messages

Hermes can send native voice bubbles (like pressing-and-holding-to-record) to WeChat, but only if the audio is in **SILK v3** format. MP3/WAV/OGG are delivered as file attachments.

## How It Works

The WeChat gateway (`gateway/platforms/weixin.py`) checks file extension in `send_voice()`:
- `.silk` → native voice bubble via `force_file_attachment=False`
- other audio formats → file attachment with fallback caption

The `_AUDIO_EXTS` set already includes `.silk`.

## Scripts

### `~/My_Project/tts_to_voice.py` — All-in-one

```bash
# Generate TTS + convert to SILK in one step
python3 ~/My_Project/tts_to_voice.py "要说的文字" [output.silk]
```

Pipeline:
1. `edge-tts` generates MP3 with zh-CN-XiaoxiaoNeural voice
2. `ffmpeg` decodes MP3 → 24kHz mono 16-bit WAV
3. `pysilk` encodes PCM → SILK v3
4. Output path printed for use in `MEDIA:` tag

### `~/My_Project/mp3_to_silk.py` — Convert existing MP3

```bash
python3 ~/My_Project/mp3_to_silk.py input.mp3 [output.silk]
```

## Usage in Chat

After generating the `.silk` file, include it in your response:

```
MEDIA:/path/to/output.silk
```

The WeChat gateway will detect the `.silk` extension and call `send_voice()` with native voice bubble delivery.

## Dependencies

```bash
brew install ffmpeg
pip3 install edge-tts silk-python
```

## Known Limitations

- iLink Bot API only accepts SILK for native voice bubbles
- The conversion adds ~1-2s latency per message
- `tencent=True` flag is set by default in pysilk (compatible with WeChat)
