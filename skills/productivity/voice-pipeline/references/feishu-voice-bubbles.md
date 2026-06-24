# Feishu Voice Bubbles — Discovery Session

## Date
2026-06-08

## Problem
TTS audio delivered via Hermes Feishu gateway shows up as a file attachment (MP3 download), not a native voice bubble with waveform + tap-to-play.

## What We Tried

### 1. AMR (failed)
- `ffmpeg -i input.mp3 -ar 8000 -ac 1 -ab 12.2k output.amr`
- Error: `Automatic encoder selection failed. Default encoder for format amr (codec amr_nb) is probably disabled.`
- macOS default ffmpeg doesn't ship AMR-NB encoder. Would need `--enable-libopencore-amrnb` ffmpeg build.

### 2. OGG Opus (worked!)
- `ffmpeg -i input.mp3 -c:a libopus -b:a 24k -ar 24000 -ac 1 output.opus`
- Successfully converted and sent via `MEDIA:/tmp/voice_test.opus`
- Feishu gateway recognized .opus as native voice bubble

### 3. Multiple consecutive sends (worked)
- Sent 3 back-to-back OGG Opus files, all delivered as native voice bubbles.

### 4. Edge TTS on longer text (flaky)
- First attempt (longer sentence, ~30 chars) → timeout on `wss://speech.platform.bing.com/...`
- Second attempt with same text → timeout again
- Short text (~10 chars) → success
- Conclusion: Edge TTS can be flaky on longer inputs. Retry or split into shorter segments.

## Key Finding
The Feishu gateway auto-detects .opus files and routes them as native voice messages, even though `voice_compatible: false` from the TTS tool suggests it won't. The `voice_compatible` flag refers to the TTS provider's output format (MP3), not the final delivered file format.

## Commands Used
```bash
# Convert TTS MP3 → OGG Opus for Feishu voice bubble
ffmpeg -i <input.mp3> -c:a libopus -b:a 24k -ar 24000 -ac 1 <output.opus> -y
```

## Edge Cases
- Very short audio (<2 seconds) still plays fine
- Standard 24kbps Opus is ~2-3KB per second of audio
- ffmpeg conversion is near-instant (~150x speed on M-series Mac)
