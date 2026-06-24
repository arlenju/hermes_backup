---
name: wechat-media
description: "WeChat media handling — voice/SILK messages, image/file/video delivery via iLink Bot API, CDN encryption, and the TTS→SILK conversion pipeline"
version: 1.0.0
author: agent
metadata:
  hermes:
    tags: [wechat, weixin, voice, silk, media, tts]
---

# WeChat Media Handling

WeChat (iLink Bot API) has specific media format requirements that differ from other messaging platforms. This skill covers sending and receiving media, especially the SILK voice codec required for native voice bubbles.

## Key Files

- `scripts/tts_to_voice.py` — One-step TTS→SILK pipeline: text → Edge TTS (MP3) → ffmpeg (WAV) → pysilk (SILK v3)
- `scripts/mp3_to_silk.py` — Standalone MP3→SILK converter (if TTS already done)
- `references/gateway-voice-architecture.md` — How the Hermes WeChat gateway handles voice delivery internally

## Quick Start: Send a Native Voice Bubble

```bash
python3 ~/My_Project/tts_to_voice.py "要说的文字" /path/to/output.silk
# Then include in reply: MEDIA:/path/to/output.silk
```

The WeChat gateway's `send_voice()` method recognizes `.silk` extension and routes it through the native voice bubble path (`ITEM_VOICE` with `encode_type=6`).

## Prerequisites

```bash
pip3 install edge-tts silk-python
brew install ffmpeg
```

## WeChat Media Types

| Type | Extension | Gateway method | Native? |
|------|-----------|---------------|---------|
| Text | — | `send` | ✅ Native text |
| Image | .jpg, .jpeg, .png, .webp, .gif | `send_image_file` | ✅ Native image |
| Video | .mp4, .mov, .avi, .mkv, .webm, .3gp | `send_video` | ✅ Native video |
| **Voice (SILK)** | **.silk** | **`send_voice`** | **✅ Native voice bubble** |
| Audio (MP3 etc.) | .mp3, .wav, .ogg, .opus, .m4a, .flac | `send_voice` → `_send_file(force_file_attachment=True)` | ❌ File attachment |
| File | everything else | `send_document` | ❌ File attachment |

## The SILK Format

WeChat native voice bubbles require **SILK v3** codec — a speech codec originally developed by Skype, now used by Tencent. Characteristics:

- **Header:** `\x02#!SILK_V3` (magic bytes: `02 23 21 53 49 4c 4b 5f 56 33`)
- **Sample rate:** 8/12/16/24 kHz (24 kHz recommended)
- **Channels:** Mono
- **Bit depth:** 16-bit
- **Bit rate:** ~24 kbps for good quality
- **Tencent mode:** Use `tencent=True` in pysilk to add Tencent-specific framing

## Gateway Architecture (weixin.py)

Key code paths in `gateway/platforms/weixin.py`:

| Line | Code | Purpose |
|------|------|---------|
| 110-113 | `MEDIA_*` constants | 1=image, 2=video, 3=file, 4=voice |
| 1763 | `_AUDIO_EXTS` | Extensions treated as audio: `.ogg .opus .mp3 .wav .m4a .flac .silk` |
| 1767-1776 | `_deliver_media()` | Routes by extension to the right send method |
| 1926-1961 | `send_voice()` | `.silk` → native voice; other audio → file attachment |
| 1982-2078 | `_send_file()` | CDN upload + AES-128-ECB encrypt + iLink API send |
| 2040-2043 | SILK params | Sets `encode_type=6`, `sample_rate=24000`, `bits_per_sample=16` for `.silk` |
| 2108-2122 | `_outbound_media_builder()` | `.silk` → `MEDIA_VOICE` + `ITEM_VOICE` builder |

## Common Issues

### SILK voice bubble not delivered

**Symptom:** `send_message` reports success or MEDIA tag included in response, but user sees nothing on WeChat (not even a file).

**Troubleshooting:**
1. **Check gateway logs** for errors: `tail -20 ~/.hermes/logs/gateway.log`
2. **Check for dual instances:** `ERROR gateway.run: Another gateway instance (PID X)...` means send targets a dying instance
3. **Fallback strategy:** MP3 delivery is reliable. Use `text_to_speech` tool or include `MEDIA:/path/to/file.mp3` — user receives a playable file attachment

**Fix for dual instance:** Kill stale processes, then restart:
```bash
pkill -f "hermes.*gateway" && hermes gateway start
```

### `.silk` sent as file attachment, not voice bubble

### `.silk` sent as file attachment, not voice bubble

**Check:** Gateway log for `send_voice`. If `force_file_attachment=True` was set, the file path didn't end with `.silk`.

**Fix:** Ensure the path in `MEDIA:/path/to/file.silk` uses lowercase `.silk` extension. `path.endswith(".silk")` is case-sensitive on the extension.

### pysilk API quirks

The `pysilk.encode()` requires file-like objects for both input and output:

```python
import io, pysilk

pcm_buf = io.BytesIO(pcm_data)
out_buf = io.BytesIO()
pysilk.encode(pcm_buf, out_buf, sample_rate=24000, bit_rate=24000, tencent=True)

with open("output.silk", "wb") as f:
    f.write(out_buf.getvalue())
```

Signature: `encode(input: BinaryIO, output: BinaryIO, sample_rate: int, bit_rate: int, max_internal_sample_rate=24000, packet_loss_percentage=0, complexity=2, use_inband_fec=False, use_dtx=False, tencent=True)`
