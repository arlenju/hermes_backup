---
name: voice-pipeline
description: "TTS, STT, and voice message pipeline for Hermes — configure Edge TTS voices, install faster-whisper, convert MP3→SILK for WeChat, MP3→Opus for Feishu native voice bubbles"
version: 1.3.0
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

### TTS Provider Selection Guide

| When to use | Provider | Reason |
|-------------|----------|--------|
| **中文为主, 免费, 本地闭环** | `edge` (XiaoxiaoNeural) | Best free Chinese TTS, no API key, works offline after first use |
| **英文专业播报** | `edge` (Yunyang/any) or `openai` | Either works; Edge is free |
| **需要定制音色/说话风格** | `elevenlabs` or `openai` | API-based, paid |
| **全本地化(M5, 无网)** | `edge` first; fallback `neutts` | Edge TTS uses a websocket to bing.com on first call — not truly offline. neutts is fully local but lower quality. |

**Switching the provider:** `hermes config set tts.provider edge` (takes effect on next gateway `/restart` or CLI relaunch).

**Pitfall — default provider is NOT always Edge.** The Hermes default config may set `tts.provider: openai`, which requires `VOICE_TOOLS_OPENAI_KEY` and charges per character. Always check current config:
```bash
grep "provider:" ~/.hermes/config.yaml | head -5
```
If it says `openai`, switch to `edge` for free Chinese TTS.

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

### Built-in Providers

Hermes ships with 6 native STT backends:

| Provider | Name | Auth | Quality |
|----------|------|------|---------|
| **Local faster-whisper** | `local` | None (free, offline) | Good (base: ~140MB) |
| **Groq Whisper** | `groq` | `GROQ_API_KEY` | Excellent (free tier) |
| **OpenAI Whisper** | `openai` | `VOICE_TOOLS_OPENAI_KEY` | Excellent (paid) |
| **Mistral Voxtral** | `mistral` | `MISTRAL_API_KEY` | Good |
| **xAI Grok STT** | `xai` | `XAI_API_KEY` | Excellent, 21 languages |
| **ElevenLabs Scribe** | `elevenlabs` | `ELEVENLABS_API_KEY` | Good, diarization |

Config:
```yaml
stt:
  enabled: true
  provider: local       # local, groq, openai, mistral, xai, elevenlabs
  local:
    model: base         # tiny, base, small, medium, large-v3
    language: ''        # auto-detect if empty
```

> **Model size tradeoff:** `base` (~140MB download on first use) balances quality and speed. `small` is more accurate but slower. `tiny` is fastest but less accurate.

### Custom STT: Command-Provider Pattern (Zero Python)

For any CLI-based ASR engine (Qwen3-ASR, whisper.cpp, vosk, etc.), register it as a **command provider** — no plugin, no Python code, no core modifications:

```yaml
stt:
  enabled: true
  provider: qwen3-asr   # your custom name

  # Custom providers (registered under `stt.providers`)
  providers:
    qwen3-asr:
      type: command                    # Hermes runs the CLI, reads stdout
      command: "/path/to/asr_script.sh {input_path}"
      timeout: 300                     # seconds (default: 300)
      format: txt                      # output format (txt/json/srt/vtt; default: txt)
      language: zh                     # language hint passed to script

  local:
    model: base                        # kept as fallback
```

**How it works:**
1. Hermes receives a voice message, saves to temp file
2. Replaces `{input_path}` / `{model}` / `{language}` placeholders in the command
3. Runs the command, waits up to `timeout` seconds
4. Reads stdout as the transcription result

### Simple Env-Var Escape Hatch

For one-off testing, set `HERMES_LOCAL_STT_COMMAND` and use `local_command` provider:

```bash
export HERMES_LOCAL_STT_COMMAND='/path/to/asr_script.sh {input_path}'
hermes config set stt.provider local_command
```

### Qwen3-ASR Integration (MLX on Apple Silicon)

[Qwen3-ASR](https://huggingface.co/collections/mlx-community/qwen3-asr) by Alibaba is 2026 open-source SOTA ASR — 52 languages, 22 Chinese dialects, 92ms TTFB streaming, excellent code-switching (中英混杂). Works on Apple Silicon via MLX.

**1. Install mlx-audio**
```bash
source ~/.hermes/hermes-agent/venv/bin/activate
pip install mlx-audio
```

**2. Download model (8-bit, ~1GB)**
```bash
hf download mlx-community/Qwen3-ASR-0.6B-8bit \
  --local-dir ~/.lmstudio/models/mlx-community/Qwen3-ASR-0.6B-8bit
```

**3. Write wrapper script (`~/.hermes/scripts/mlx_asr.sh`)**
```bash
#!/bin/bash
MODEL_PATH="$HOME/.lmstudio/models/mlx-community/Qwen3-ASR-0.6B-8bit"
INPUT="$1"
OUTPUT_DIR=$(mktemp -d)
OUTPUT_FILE="$OUTPUT_DIR/result.txt"
source "$HOME/.hermes/hermes-agent/venv/bin/activate"
python3 -m mlx_audio.stt.generate --model "$MODEL_PATH" --audio "$INPUT" \
  --output-path "$OUTPUT_FILE" --format txt --language zh 2>/dev/null
[ -f "$OUTPUT_FILE" ] && cat "$OUTPUT_FILE" || { echo "ERROR"; exit 1; }
rm -rf "$OUTPUT_DIR"
```
```bash
chmod +x ~/.hermes/scripts/mlx_asr.sh
```

**4. Register in config.yaml**
```yaml
stt:
  enabled: true
  provider: qwen3-asr
  providers:
    qwen3-asr:
      type: command
      command: "~/.hermes/scripts/mlx_asr.sh {input_path}"
      timeout: 300
      language: zh
  local:
    model: base
```

**5. Restart gateway** (`hermes gateway restart` or kill+relaunch CLI)

**Fallback:** `hermes config set stt.provider local` to revert to faster-whisper.

**Note:** Qwen3-ASR-0.6B 8-bit uses ~1.1GB RAM on M5. First inference loads model (~5s); subsequent calls are near-instant.

### CLI-Based STT Verification

Test the ASR directly from terminal:
```bash
source ~/.hermes/hermes-agent/venv/bin/activate
python3 -m mlx_audio.stt.generate \
  --model ~/.lmstudio/models/mlx-community/Qwen3-ASR-0.6B-8bit \
  --audio /path/to/test.mp3 --output-path /tmp/result.txt \
  --format txt --language zh
cat /tmp/result.txt
```

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

### `uv pip install` as fallback when venv pip is broken or missing

If `~/.hermes/hermes-agent/venv/bin/python -m pip install <pkg>` fails (ModuleNotFoundError: No module named 'pip'), use `uv` instead — it manages packages into any venv without needing pip inside it:

```bash
# Install a package into the Hermes runtime venv using uv
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python faster-whisper

# Or activate the venv first, then use uv without --python
source ~/.hermes/hermes-agent/venv/bin/activate
uv pip install faster-whisper
```

`uv` is pre-installed on this machine at `/opt/homebrew/bin/uv` and handles dependency resolution faster than pip. This is the preferred fallback when pip itself is broken.

### STT provider silently broken — always test before assuming it works

The config may show `stt.provider: qwen3_asr` with a command provider pointing to `~/.hermes/scripts/mlx_asr.sh`, but the underlying `mlx_audio` Python module may be missing from the venv. The script fails silently (stderr suppressed with `2>/dev/null`) and Hermes reports "transcription failed" with no useful diagnostic.

**Diagnostic sequence when STT fails:**
1. Check what provider is configured: `grep -A5 'stt:' ~/.hermes/config.yaml`
2. If command provider, run the script directly with a test audio file and WITHOUT stderr suppression to see the real error:
   ```bash
   # Convert incoming audio to wav first if needed
   ffmpeg -i /path/to/audio.ogg /tmp/asr_input.wav -y
   # Run the ASR script directly, showing all errors
   bash ~/.hermes/scripts/mlx_asr.sh /tmp/asr_input.wav
   ```
3. If `ModuleNotFoundError: No module named 'mlx_audio'`, install it:
   ```bash
   source ~/.hermes/hermes-agent/venv/bin/activate
   uv pip install mlx-audio
   ```
4. If the module can't be installed quickly, fall back to `faster-whisper`:
   ```bash
   uv pip install --python ~/.hermes/hermes-agent/venv/bin/python faster-whisper
   hermes config set stt.provider local
   ```
5. **If faster-whisper is ALSO missing** (common after venv rebuilds or fresh installs), install it first before it can serve as fallback:
   ```bash
   # Check if faster-whisper is actually installed
   ~/.hermes/hermes-agent/venv/bin/python -c "import faster_whisper; print('OK')"
   # If ModuleNotFoundError, install it:
   uv pip install --python ~/.hermes/hermes-agent/venv/bin/python faster-whisper
   # Also check mlx_whisper and whisper as alternatives:
   ~/.hermes/hermes-agent/venv/bin/python -c "import mlx_whisper" 2>&1
   ~/.hermes/hermes-agent/venv/bin/python -c "import whisper" 2>&1
   ```
6. **Last-resort: install into system Python** and run directly (bypasses Hermes STT config entirely):
   ```bash
   uv pip install faster-whisper  # installs into system python3
   # Convert incoming audio to wav first
   ffmpeg -i /path/to/audio.ogg /tmp/asr_input.wav -y
   # Run directly
   python3 -c "
   from faster_whisper import WhisperModel
   model = WhisperModel('base')
   segments, info = model.transcribe('/tmp/asr_input.wav', language='zh')
   print(''.join(s.text for s in segments))
   "
   ```
   This is useful when you need to transcribe one audio file immediately without reconfiguring the full STT pipeline.

   **Audio format conversion first:** Incoming voice messages from Feishu/WeChat are often OGG Opus format. Always convert to WAV before feeding to any ASR engine:
   ```bash
   ffmpeg -i /path/to/audio.ogg /tmp/asr_input.wav -y
   ```
   OGG Opus → WAV conversion is instant and lossless. Most ASR engines (faster-whisper, mlx_audio, Qwen3-ASR) expect WAV input, not raw OGG.

   **ASR output quality check:** After transcription, always do a sanity check on the output. ASR may mishear proper nouns — "WorkBuddy" might become "Workbody", "Hermes" might become "Harnis", "DeepSeek" might become "Deep Seak". When the transcription contains product names or technical terms, verify with a quick web_search before using the transcript as the basis for research or reports. This is not optional — a misheard product name in a research report looks unprofessional.

   **Proven fallback chain when STT is broken (this session):** When `mlx_audio` is missing from the venv and `faster-whisper` is also missing, the fastest recovery is:
   ```bash
   # 1. Convert incoming audio to WAV
   ffmpeg -i /path/to/audio.ogg /tmp/asr_input.wav -y
   # 2. Install faster-whisper into SYSTEM Python (not venv — faster, no venv activation needed)
   uv pip install --system faster-whisper
   # 3. Run directly with system python3
   python3 -c "
   from faster_whisper import WhisperModel
   model = WhisperModel('base')
   segments, info = model.transcribe('/tmp/asr_input.wav', language='zh')
   print(''.join(s.text for s in segments))
   "
   ```
   This bypasses the Hermes STT config entirely and gets transcription working in under 2 minutes. The model downloads on first use (~140MB, ~30s).

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

- `references/feishu-voice-bubbles.md` — full debug transcript for Feishu OGG Opus integration
- `references/qwen3-asr-integration.md` — Qwen3-ASR model info, CLI test, performance, and pitfalls

## CLI Voice Mode

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
