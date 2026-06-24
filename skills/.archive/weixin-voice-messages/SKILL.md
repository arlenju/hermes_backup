---
name: weixin-voice-messages
description: "Deliver TTS audio as native WeChat voice bubbles via SILK codec — conversion pipeline, gateway integration, and troubleshooting"
version: 1.0.0
author: agent
metadata:
  hermes:
    tags: [wechat, weixin, voice, tts, silk, messaging]
---

# WeChat Native Voice Messages (TTS → SILK)

Send TTS-generated speech as native WeChat voice bubbles (the "hold-to-talk" style), not as file attachments.

## How It Works

WeChat's iLink Bot API only renders native voice bubbles for audio in **SILK v3 codec** format. The Hermes WeChat gateway (`gateway/platforms/weixin.py`) already supports this:

- `_AUDIO_EXTS` includes `.silk` alongside `.mp3`, `.wav`, `.ogg`, etc.
- `send_voice()` checks file extension: **`.silk` → native voice bubble** via `_send_file(force_file_attachment=False)`. Any other audio format → file attachment with caption "[voice message as attachment]".

So the pipeline is: **TTS → MP3 → WAV → PCM → SILK → MEDIA:path/to/file.silk**

## Prerequisites

```bash
# System
brew install ffmpeg

# Python packages
pip3 install silk-python edge-tts
```

## Quick Start

### One-shot: `tts_to_voice.py`

The integrated script at `~/My_Project/tts_to_voice.py` does the full pipeline:

```bash
python3 ~/My_Project/tts_to_voice.py "要说的文字" [output.silk]
```

Output: prints the path to the generated `.silk` file, ready to include in a response as `MEDIA:/path/to/file.silk`.

### Manual conversion: `mp3_to_silk.py`

If you already have an MP3:

```bash
python3 ~/My_Project/mp3_to_silk.py input.mp3 [output.silk]
```

## Conversion Pipeline (Technical)

```
MP3 ──ffmpeg──▶ WAV (24kHz, mono, 16-bit signed PCM)
WAV ──wave──▶ PCM (raw bytes)
PCM ──pysilk.encode()──▶ SILK v3
```

Key parameters for `pysilk.encode()`:
```python
import pysilk, io
pcm_buf = io.BytesIO(pcm_data)
out_buf = io.BytesIO()
pysilk.encode(pcm_buf, out_buf, sample_rate=24000, bit_rate=24000)
```

- `tencent=True` (default) — enables Tencent-specific SILK mode (required for WeChat)
- `sample_rate`: 24000 Hz recommended for voice quality
- `bit_rate`: 24000 bps — good balance of quality and size (~45% of MP3 size)

## Delivery via Hermes Gateway

Include the `.silk` file path using the `MEDIA:` tag in your response:

```
MEDIA:/Users/jushuai/.hermes/audio_cache/voice.silk
```

The WeChat gateway (`weixin.py` lines 1763-1776) routes:
- `.silk` → `send_voice()` → native voice bubble
- `.mp3/.wav/.ogg` → `send_voice()` → file attachment (playable but not a bubble)
- `.jpg/.png` → `send_image_file()`
- Other → `send_document()`

## TTS Voice Configuration

```bash
# Set preferred Edge TTS voice
hermes config set tts.edge.voice zh-CN-XiaoxiaoNeural

# Check current config
grep -A 3 'tts:' ~/.hermes/config.yaml
```

Recommended Chinese voices:
| Voice | Description |
|-------|-------------|
| `zh-CN-XiaoxiaoNeural` | 小晓 — 温柔女声 |
| `zh-CN-YunxiNeural` | 云希 — 阳光男声 |
| `zh-CN-XiaoyiNeural` | 小伊 — 可爱女声 |
| `zh-CN-YunjianNeural` | 云健 — 成熟男声 |

## Reference Files

- `scripts/tts_to_voice.py` — Integrated TTS→SILK pipeline script
- `scripts/mp3_to_silk.py` — MP3→SILK standalone converter

## Pitfalls

### SILK file sent as document instead of voice bubble
**Cause:** The file doesn't end in `.silk` (case-insensitive check). The gateway checks `audio_path.lower().endswith(".silk")`.

**Fix:** Ensure the output path uses lowercase `.silk` extension.

### `pysilk.encode()` API confusion
The API takes file-like objects, not bytes or paths:
```python
# ✅ Correct
pysilk.encode(io.BytesIO(pcm_data), io.BytesIO(), 24000, 24000)

# ❌ Wrong
pysilk.encode(pcm_data, "out.silk", 24000, 24000)
```

### ffmpeg not installed
The pipeline requires ffmpeg for MP3→WAV conversion. Install via: `brew install ffmpeg`

### edge-tts not installed
The TTS generation step needs the `edge-tts` package: `pip3 install edge-tts`

### Voice transcription may show as text
If WeChat provides a text transcription of the SILK voice message, the gateway may extract the transcription instead of routing the audio. This is expected behavior per the WeChat adapter docs — the adapter uses the transcription when available.
