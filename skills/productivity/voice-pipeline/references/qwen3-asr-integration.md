# Qwen3-ASR Integration (MLX on Apple Silicon)

Qwen3-ASR (Alibaba, 2026) — SOTA open-source ASR with 52 languages,
22 Chinese dialects, 92ms TTFB streaming, and excellent code-switching
(中英混杂). Apache 2.0 license.

## Models

| Size | BFloat16 | 8-bit | 4-bit |
|------|----------|-------|-------|
| 0.6B | mlx-community/Qwen3-ASR-0.6B-bf16 (2.4GB) | mlx-community/Qwen3-ASR-0.6B-8bit (1.0GB) | mlx-community/Qwen3-ASR-0.6B-4bit (0.5GB) |
| 1.7B | Original (not MLX-converted) | — | — |

**Recommendation:** 0.6B 8-bit for M5/24GB. 0.6B 4-bit for 16GB machines.
bf16 is unnecessary quality for ASR — the quantization penalty is negligible.

## Integration Paths

### A. Hermes Command Provider (recommended)

Register via `stt.providers.<name>: type: command` in config.yaml.
No Hermes core changes needed. See the main `voice-pipeline` SKILL.md
for step-by-step setup.

### B. vLLM OpenAI-compatible service (future)

If vLLM adds Qwen3-ASR model support, deploy as:
```bash
vllm serve Qwen/Qwen3-ASR-0.6B --port 8001
```
Then configure Hermes `stt.provider: openai` pointing to localhost:8001.
No wrapper script needed.

## CLI Direct Test

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
python3 -m mlx_audio.stt.generate \
  --model ~/.lmstudio/models/mlx-community/Qwen3-ASR-0.6B-8bit \
  --audio /path/to/voice.mp3 \
  --output-path /tmp/result.txt \
  --format txt --language zh
cat /tmp/result.txt
```

## Performance on M5/24GB

- Model load: ~5s (first inference)
- Short voice message (<30s): ~1-2s transcription
- Memory: ~1.1GB RSS for 8-bit model
- VAD: built-in silence detection via mlx-audio

## Pitfalls

1. **mlx-audio must be in Hermes runtime venv:**
   ```bash
   ~/.hermes/hermes-agent/venv/bin/python -m pip install mlx-audio
   ```

2. **First inference is slow** — model loads into memory. Subsequent calls
   reuse cached weights and are near-instant.

3. **Wrapper script must output to stdout** — Hermes command provider reads
   stdout as the transcription. The `mlx_audio.stt.generate` CLI writes to
   a file, so the wrapper must `cat` the result.

4. **Switch back to faster-whisper instantly:**
   ```bash
   hermes config set stt.provider local
   ```
   If the Qwen3-ASR service is down, Hermes falls back gracefully.
