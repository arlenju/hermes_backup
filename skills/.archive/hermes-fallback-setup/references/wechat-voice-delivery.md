# WeChat Native Voice Delivery via TTS→SILK

Hermes' WeChat adapter supports sending native voice bubbles (like holding-to-talk recordings) when the audio file is in **SILK v3** format.

## How It Works

The WeChat gateway (`gateway/platforms/weixin.py`) routes outbound audio based on file extension:

| Extension | Delivery method | User sees |
|-----------|----------------|-----------|
| `.mp3`, `.wav`, `.ogg`, etc. | File attachment | Downloadable audio file |
| `.silk` | Native voice bubble | Like a recorded voice message |

## Code Flow

1. Response text is scanned for `MEDIA:<path>` tags by `extract_media()` in `base.py`
2. `.silk` is in `MEDIA_DELIVERY_EXTS` so the tag is recognized
3. `_deliver_media()` checks `ext in _AUDIO_EXTS` → calls `send_voice()`
4. `send_voice()` checks `path.endswith(".silk")` → calls `_send_file(force_file_attachment=False)`
5. `_outbound_media_builder()` returns `MEDIA_VOICE` for `.silk` files with `force_file_attachment=False`
6. Uploaded to WeChat CDN as voice item with `encode_type=6`, `sample_rate=24000`, `bits_per_sample=16`

## Sending via MEDIA Tag

Include in your response:
```
MEDIA:/path/to/file.silk
```

The MEDIA tag is stripped from the visible text and the file is sent separately.

## Dependencies for SILK Encoding

```bash
pip install silk-python        # PCM → SILK encoding
brew install ffmpeg             # MP3 → WAV conversion
pip install edge-tts            # TTS generation (optional, if generating speech)
```

## SILK Format Requirements

- **Sample rate:** 24000 Hz (SILK supports 8/12/16/24 kHz)
- **Channels:** Mono
- **Bit depth:** 16-bit signed
- **Header:** `\x02#!SILK_V3` magic bytes

## Known Limitations

- Gateway connectivity issues (double instance conflicts) can cause silent delivery failures
- The WeChat iLink API may silently fail on some SILK payloads
- No `send_voice` error surfaces in the agent session; check `gateway.log` for details
