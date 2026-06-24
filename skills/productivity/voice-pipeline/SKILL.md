---
name: voice-pipeline
description: "TTS, STT, and voice message pipeline for Hermes — configure Edge TTS voices, install faster-whisper, convert MP3→SILK for WeChat, MP3→Opus for Feishu native voice bubbles"
version: 1.2.0
author: agent
metadata:
  hermes:
    tags: [hermes, tts, stt, voice, wechat, feishu, audio]
---

# Voice Pipeline

TTS, STT, and voice message handling for Hermes Agent — from text-to-speech output to native voice message delivery on messaging platforms.

## Quick Start

```bash
# STT (speech-to-text) — transcribe incoming voice messages
pip install faster-whisper
hermes config set stt.enabled true
hermes config set stt.provider local
hermes config set stt.local.model base

# TTS (text-to-speech) — speak replies
hermes config set tts.provider edge  # free, no API key
hermes config set tts.edge.voice zh-CN-XiaoxiaoNeural  # 小晓, 温柔女声

# Verify
hermes config check  # Check ✓ marks on stt.* and tts.*
```

## Supported TTS Providers

| Provider | Env var | Free? | Chinese voices |
|----------|---------|-------|----------------|
| Edge TTS | None | ✅ Yes | ✅ Excellent (Xiaoxiao, Yunyang, etc.) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier | Limited |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid | Some |
| MiniMax | `MINIMAX_API_KEY` | Paid | Good |
| Mistral | `MISTRAL_API_KEY` | Paid | None |

**Edge TTS is the default** — no API key needed, excellent Chinese voice quality.

## Edge TTS Chinese Voices

| Voice ID | Name | Style |
|----------|------|-------|
| `zh-CN-XiaoxiaoNeural` | 小晓 | 温柔女声 (default) |
| `zh-CN-YunyangNeural` | 云扬 | 成熟男声 |
| `zh-CN-XiaoyiNeural` | 小伊 | 活泼女声 |
| `zh-CN-YunxiNeural` | 云希 | 阳光男声 |
| `zh-CN-XiaohanNeural` | 小涵 | 知性女声 |
| `zh-CN-YunjianNeural` | 云健 | 沉稳男声 |

Set voice: `hermes config set tts.edge.voice zh-CN-XiaoxiaoNeural`

## STT (Speech-to-Text)

Supports voice messages from messaging platforms (Telegram, WeChat, Discord, etc.).

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local       # local, groq, openai, mistral
  local:
    model: base         # tiny, base, small, medium, large-v3
    language: ''        # auto-detect if empty
```

> **Model size tradeoff:** `base` (~140MB download on first use) balances quality and speed. `small` is more accurate but slower. `tiny` is fastest but less accurate.

## Pitfalls & Workarounds

### Runtime venv vs project dev venv — install deps in the RIGHT one

The `hermes` CLI wrapper at `~/.local/bin/hermes` points to `~/.hermes/hermes-agent/venv/bin/hermes`. **Python packages must be installed in that venv**, not the project development venv:

```bash
# ✅ CORRECT — install into the runtime venv Hermes actually uses
~/.hermes/hermes-agent/venv/bin/python -m pip install faster-whisper
~/.hermes/hermes-agent/venv/bin/python -m pip install sounddevice numpy

# ❌ WRONG — this is the dev/project venv; `hermes` does NOT use it
~/My_Project/hermes_agent/Hermes-Agent/venv/bin/python -m pip install ...
```

**Verification:**
```bash
# Confirm the hermes command uses the right venv
cat ~/.local/bin/hermes
# → exec "~/.hermes/hermes-agent/venv/bin/hermes" "$@"
```

If you install into the wrong venv, `/voice on` will still fail with "Audio libraries not installed" even though `pip list` shows them.

### CLI voice mode needs sounddevice + numpy too

`/voice on` requires three Python packages, not just faster-whisper:

```bash
~/.hermes/hermes-agent/venv/bin/python -m pip install faster-whisper sounddevice numpy
```

`sounddevice` depends on system PortAudio (pre-installed on macOS). Install test:

```bash
~/.hermes/hermes-agent/venv/bin/python -c "import sounddevice; print('OK')"
```

### `hermes config set` may fail (venv import issues)

If the editable install breaks (`ModuleNotFoundError: No module named 'hermes_cli'`), `hermes config set` commands fail. **Fallback: edit config.yaml directly** with Python:

```bash
cd ~/My_Project/hermes_agent/Hermes-Agent
PYTHONPATH="$PWD:$PYTHONPATH" ~/My_Project/hermes_agent/Hermes-Agent/venv/bin/python -c "
import yaml
with open('config.yaml') as f:
    cfg = yaml.safe_load(f)
cfg.setdefault('stt', {})['enabled'] = True
cfg['stt']['provider'] = 'local'
cfg['stt'].setdefault('local', {})['model'] = 'base'
cfg.setdefault('tts', {}).setdefault('edge', {})['voice'] = 'zh-CN-XiaoxiaoNeural'
with open('config.yaml', 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False)
"
```

⚠️ `yaml.dump` reformats the entire file — verify all top-level keys survived after write.

### Venv may lack pip

If `pip` is missing from the venv, reinstall it:
```bash
~/My_Project/hermes_agent/Hermes-Agent/venv/bin/python -m ensurepip --upgrade
```

### Check existing config before setting

STT/TTS may already be configured. Inspect first:
```bash
cd ~/My_Project/hermes_agent/Hermes-Agent
PYTHONPATH="$PWD:$PYTHONPATH" ~/My_Project/hermes_agent/Hermes-Agent/venv/bin/python -c "
import yaml
with open('config.yaml') as f:
    cfg = yaml.safe_load(f)
stt = cfg.get('stt', {})
print('STT enabled:', stt.get('enabled'))
print('STT provider:', stt.get('provider'))
print('STT model:', stt.get('local', {}).get('model'))
print('TTS provider:', cfg.get('tts', {}).get('provider'))
print('TTS voice:', cfg.get('tts', {}).get('edge', {}).get('voice'))
"
```

### faster-whisper model downloads on first use

The `base` model is ~140MB and auto-downloads when you first create `WhisperModel("base")`. First transcription will be slow.

## WeChat Voice Messages (SILK Format)

### The Problem

WeChat's iLink Bot API expects voice messages in **SILK v3** codec (Tencent's proprietary format derived from Skype SILK). The Hermes TTS tool produces MP3, which gets delivered as a **file attachment** — not a native voice bubble.

### MP3 → SILK Conversion

The helper script `scripts/mp3_to_silk.py` converts TTS-generated MP3 audio to WeChat-compatible SILK format.

**Dependencies:**
```bash
pip install silk-python
brew install ffmpeg       # or: apt install ffmpeg
```

**Usage:**
```bash
python3 scripts/mp3_to_silk.py input.mp3 [output.silk]
```

**Pipeline:**
```
TTS (Edge) → MP3 → ffmpeg → WAV (24kHz, mono, s16) → PCM → pysilk.encode() → SILK v3
```

The SILK file can then be uploaded via the WeChat gateway's `send_voice` API (requires gateway-level integration — by default Hermes sends MEDIA: marked files as document attachments, not voice bubbles).

### SILK File Header Verification

Valid SILK v3 files start with bytes `\\x02` followed by SILK header. Verify with:
```bash
python3 -c "
with open('file.silk', 'rb') as f:
    h = f.read(10)
print('SILK OK' if h[:1] == b'\\\\x02' else 'Not SILK')
print('Header hex:', h[:8].hex())
"
```

## Feishu Voice Bubbles (飞书原生语音) — WORKING

### Discovery: OGG Opus via MEDIA: tag works today

Despite `voice_compatible: false` from the TTS tool, **Feishu DOES accept OGG Opus as native voice bubbles** when delivered via the MEDIA: tag in the agent's response. No gateway changes needed.

**Proven workflow (this session):**
1. Generate TTS audio: `text_to_speech(text=...)` → MP3
2. Convert to OGG Opus via ffmpeg:
   ```bash
   ffmpeg -i input.mp3 -c:a libopus -b:a 24k -ar 24000 -ac 1 output.opus -y
   ```
3. Include `MEDIA:/path/to/output.opus` in the response text — the Feishu gateway delivers it as a native voice bubble (waveform + play button), NOT a file attachment.

**Key parameters that worked:**
| Parameter | Value | Notes |
|-----------|-------|-------|
| Codec | libopus (OGG container) | AMR encoder may not be available in default ffmpeg |
| Bitrate | 24k | Good balance of quality vs. file size |
| Sample rate | 24000 Hz | Matches Edge TTS output |
| Channels | 1 (mono) | Voice messages are always mono |

### Edge TTS Timeout on Long Text

Edge TTS (`wss://speech.platform.bing.com/...`) can timeout on longer text strings. Short texts (1-2 sentences) work reliably. If TTS fails with a connection timeout:
- Try a shorter text input
- Retry the same request (transient network issue)
- Split into multiple shorter messages instead of one long one

### Quick Conversion Script

See `scripts/mp3_to_feishu_opus.py` for a one-shot converter that wraps the ffmpeg command above. Usage:
```bash
python3 scripts/mp3_to_feishu_opus.py input.mp3 output.opus
```

### Reference

See `references/feishu-voice-bubbles.md` for the full session transcript, debugging steps, and format requirements.

---

## Voice Mode (Interactive)

In CLI sessions, enable voice-to-voice mode:
```
/voice on        # Full voice: listen + speak
/voice tts       # Speak replies only
/voice off       # Text only
```

### Voice mode etiquette (seamless experience)

When `/voice on` is active, the agent MUST:
1. **Reply with TTS only** — call `text_to_speech()` for every response
2. **Stay text-silent** — do NOT output the MEDIA: path, do NOT echo what you're saying in text, do NOT output any visible text at all. The TTS is the delivery; visible text breaks immersion.
3. **Keep responses concise** — TTS is slower to consume than text, so shorter sentences land better.

This applies regardless of platform. The user hears you; they don't need to read you too.

## Config Reference

```yaml
tts:
  provider: edge              # edge, elevenlabs, openai, minimax, mistral
  edge:
    voice: zh-CN-XiaoxiaoNeural
  elevenlabs:
    voice_id: pNInz6obpgDQGcFmaJgB
  auto_tts: false             # auto-speak every reply
  beep_enabled: true           # play beep before speech (gateway)
  silence_threshold: 200
  silence_duration: 3.0

stt:
  enabled: true
  provider: local
  local:
    model: base
    language: ''
```

## Known Limitations

- **WeChat voice bubbles:** TTS → MP3 → file attachment, not native voice bubble. SILK conversion is possible (see script above) but Hermes gateway doesn't yet auto-convert or route .silk files through `send_voice`.
- **Feishu voice bubbles:** ✅ **WORKING** via OGG Opus conversion + MEDIA: tag (see Feishu section above). Not a limitation anymore.
- **First-use download:** faster-whisper downloads ~140MB model on first use.
- **Edge TTS rate limits:** Very generous free tier, but extremely long audio may be truncated.

## Absorption Note

This skill absorbed `weixin-voice-messages` and `tts-to-silk-wechat-voice` (2026-06-13). Both were narrow WeChat SILK skills whose content was already fully covered here. The absorbed skills' scripts (`tts_to_voice.py`, `mp3_to_silk.py`) were already present under `scripts/` and the `wechat-media` skill's `scripts/` directory. No unique content was lost.
