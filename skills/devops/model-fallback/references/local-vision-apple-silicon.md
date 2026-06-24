# Local Vision Model Setup — Apple Silicon (M-series Macs)

Class-level reference for picking, downloading, serving, and wiring a local vision-language model into Hermes' `auxiliary.vision` channel on Apple Silicon.

## TL;DR

On M-series Macs **prefer MLX over GGUF** for VLMs. MLX uses unified memory + Neural Engine and runs ~30–50% faster than llama.cpp/LM Studio GGUF on the same chip. LM Studio cannot serve MLX models — bring up `mlx_vlm.server` directly.

## 2026 Recommended Stack

| Component | Choice | Notes |
|---|---|---|
| Model | `mlx-community/Qwen3-VL-8B-Instruct-6bit` (~7.8 GB) | Top open VLM 2026; apache-2.0; HF page lists Hermes integration |
| Quant tier | 6-bit | Sweet spot (matches user's Q6_K preference). 4-bit (~4.5 GB) for <16 GB RAM; 8-bit (~8.5 GB) for max accuracy |
| Server | `mlx_vlm.server` | OpenAI-compatible API |
| Port | 8080 | Avoid clash with LM Studio on 1234 |
| Storage | `~/.lmstudio/models/mlx-community/` | Reuse existing model dir; LM Studio ignores MLX files but no conflict |

### Other strong candidates (when 8B isn't right)

- `mlx-community/Qwen3-VL-4B-Instruct-6bit` — ~3.5 GB, lighter machines.
- `mlx-community/Qwen3-VL-32B-Instruct-*` — needs 32+ GB unified memory.
- `mlx-community/GLM-4.6V-*` — competitive alternative if Qwen3-VL has a specific weakness.

## HuggingFace VLM Model Zoo (mlx-vlm supported)

All models below have MLX quantized versions under the `mlx-community` org on HuggingFace (or the listed org). Serve any with `mlx_vlm.server --model <hf-id> --port 8080`. Memory estimates are for 4-bit unless otherwise noted.

### ⭐ General-purpose VLMs (Chinese + English, best all-rounders)

| Model | HF ID | 4-bit Size | 24GB Fit | Notes |
|---|---|---|---|---|
| **Qwen3-VL-8B** | `mlx-community/Qwen3-VL-8B-Instruct-4bit` | ~5.5 GB | ✅ | Current default; excellent Chinese OCR |
| **Qwen3-VL-8B 6bit** | (local) | ~7.8 GB | ✅ | Quality-first, currently in use |
| **Qwen3-VL-4B** | `mlx-community/Qwen3-VL-4B-Instruct-4bit` | ~3 GB | ✅ | Lightweight fast path |
| **Qwen3-VL-30B-A3B** | `lmstudio-community/Qwen3-VL-30B-A3B-Instruct-MLX-8bit` | MoE ~12 GB | ✅ | Active params only 3B, big batch+MoE |
| **Qwen3-VL-32B** | `mlx-community/Qwen3-VL-32B-Instruct-4bit` | ~18 GB | ⚠️ | Pushes 24 GB; may swap |
| **Qwen2.5-VL-7B** | `mlx-community/Qwen2.5-VL-7B-Instruct-4bit` | ~5 GB | ✅ | Mature, stable fallback |
| **Qwen2-VL-7B** | `mlx-community/Qwen2-VL-7B-Instruct-4bit` | ~5 GB | ✅ | Previous gen, still solid |
| **InternVL3-8B** | `mlx-community/InternVL3-8B-MLX-4bit` | ~5 GB | ✅ | Strong multi-image; good Chinese |
| **InternVL2-8B** | `mlx-community/InternVL2-8B-4bit` | ~5 GB | ✅ | Well-tested |

### 🤖 Frontier / MoE (new architectures)

| Model | HF ID | 4-bit Size | 24GB Fit | Notes |
|---|---|---|---|---|
| **Gemma 4 12B** | `mlx-community/gemma-4-12b-it-4bit` | ~8 GB | ✅ | Google; strong reasoning, MTP speculation |
| **Gemma 4 26B-A4B** | `mlx-community/gemma-4-26b-a4b-it-4bit` | MoE ~10 GB | ✅ | Active 4B, batch fits |
| **Gemma 4 31B** | `mlx-community/gemma-4-31b-it-bf16` | bf16 ~62 GB | ❌ | Only 4-bit (~18 GB) would fit |
| **DiffusionGemma 26B-A4B** | `mlx-community/diffusiongemma-26B-A4B-it-4bit` | MoE ~10 GB | ✅ | Diffusion decoder VLM |
| **Llama 3.2 Vision 11B** | `mlx-community/Llama-3.2-11B-Vision-Instruct-4bit` | ~7 GB | ✅ | Meta; English-strong |
| **Llama 4 Scout** | `mlx-community/Llama-4-Scout-17B-4E-Instruct-4bit` | ~10 GB | ✅ | 17B MoE, 10M context |
| **Pixtral 12B** | `mlx-community/pixtral-12b-4bit` | ~8 GB | ✅ | Mistral; good benchmarks |
| **Mistral Small 3.1** | `mlx-community/Mistral-Small-3.1-24B-Instruct-2501-4bit` | ~14 GB | ⚠️ | Tight on 24 GB |
| **SmolVLM 2B** | `mlx-community/SmolVLM-2B-4bit` | ~1.5 GB | ✅ | Tiny; fast for simple tasks |
| **Hunyuan-VL-7B** | `mlx-community/Hunyuan-VL-7B-4bit` | ~5 GB | ✅ | Tencent; Chinese strong |

### 🧪 Specialized / Niche

| Model | HF ID | Size | Use Case |
|---|---|---|---|
| **Phi-4 Multimodal** | `mlx-community/Phi-4-multimodal-instruct-4bit` | ~6 GB | Vision + audio input |
| **Phi-4 Reasoning Vision** | `mlx-community/Phi-4-reasoning-vision-4bit` | ~7 GB | Step-by-step reasoning |
| **Moondream 3** | `mlx-community/moondream3` | 2.8 GB | Ultra-light, fast |
| **Florence-2** | `mlx-community/Florence-2-base-ft-4bit` | ~0.8 GB | OCR / captioning / detection |
| **Jina VLM** | `jinaai/jina-vlm-mlx` | 2 GB (4-bit) | Vision embedding + understanding |
| **PaliGemma2-3B** | `mlx-community/paligemma2-3b-ft-docci-448-8bit` | ~3 GB | Document understanding |
| **MiniCPM-o** | (custom convert) | 8B MoE | Omni model (image+audio+video) |
| **MiniCPM-V 4.6** | (custom convert) | 8B | Latest MiniCPM; strong Chinese |
| **Idefics3-8B** | `mlx-community/Idefics3-8B-4bit` | ~5 GB | Multi-image native |
| **Llava-v1.6-7B** | `mlx-community/llava-v1.6-mistral-7b-4bit` | ~5 GB | Classic, well-tested |
| **Llava-1.5-7B** | `mlx-community/llava-1.5-7b-4bit` | ~5 GB | Original LLaVA |

### 🎯 Vision-specific / OCR / Tool-use

| Model | HF ID | Size | Use Case |
|---|---|---|---|
| **DeepSeek-OCR** | `mlx-community/deepseek-ocr-4bit` | ~5 GB | OCR specialist |
| **DeepSeek-OCR-2** | `mlx-community/deepseek-ocr-2-4bit` | ~5 GB | Improved OCR |
| **GLM-OCR** | `mlx-community/glm-ocr-4bit` | ~5 GB | OCR specialist |
| **PaddleOCR-VL** | (custom convert) | ~3 GB | OCR specialist |
| **Falcon-OCR** | `mlx-community/falcon-ocr-4bit` | ~4 GB | Lightweight OCR |
| **Molmo 2 7B** | `mlx-community/Molmo-2-7B-4bit` | ~5 GB | Visual grounding |
| **MolmoPoint** | (custom convert) | — | Point-level VLM interaction |
| **LocateAnything** | (custom convert) | ~3 GB | Bounding box → NL query |
| **RF-DETR** | (in mlx_vlm) | — | Object detection |
| **SAM 3 / SAM 3.1** | (in mlx_vlm) | ~1 GB | Segmentation |
| **Granite Vision 3.2** | `mlx-community/granite-vision-3.2-4bit` | ~5 GB | Enterprise doc understanding |
| **Granite 4.0 Vision** | `mlx-community/granite-4.0-vision-4bit` | ~7 GB | IBM; reasoning-heavy |

### 🔮 Cloud-exclusive (no MLX local equivalent) — for fallback

Some models only exist as cloud APIs but the user's Ark plan supports them:
- `doubao-seed-1-6-vision-250815` (Ark) — the only GUI-capable model on the user's Ark plan
- `doubao-2.0-multimodal` series (Ark)
- `Seed 1.6 Vision` (Ark)

### Selection Guide for Hermes

| Use case | Recommendation |
|---|---|
| General screenshot analysis (中文) | **Qwen3-VL-8B 6bit** (current) or **InternVL3-8B** |
| Speed-critical / low memory | **Qwen3-VL-4B** or **Moondream 3** |
| Complex reasoning about images | **Gemma 4 12B** or **Phi-4 Reasoning Vision** |
| OCR-heavy workflow | **DeepSeek-OCR** or **Florence-2** (lightweight) |
| Multi-image comparison | **InternVL3-8B** or **Idefics3** |
| Maximum quality (24GB ceiling) | **Qwen3-VL-30B-A3B** MoE or **Gemma 4 26B-A4B** MoE |

## Install (one-time)

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
pip install mlx-vlm mlx-lm
```

Always install into Hermes runtime venv (`~/.hermes/hermes-agent/venv/`), not project dev venv.

## Download

```bash
mkdir -p ~/.lmstudio/models/mlx-community
cd ~/.lmstudio/models/mlx-community
hf download mlx-community/Qwen3-VL-8B-Instruct-6bit \
  --local-dir ./Qwen3-VL-8B-Instruct-6bit \
  --max-workers 8
```

## Serve

Foreground (test):

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
python -m mlx_vlm.server \
  --model ~/.lmstudio/models/mlx-community/Qwen3-VL-8B-Instruct-6bit \
  --port 8080
```

For lid-close resilience on macOS 26.x (Tahoe), launchctl bootstrap fails I/O — use `caffeinate -d -i -m -t 86400` + background process pattern instead (see memory).

## Configure Hermes

Edit `~/.hermes/config.yaml`:

```yaml
auxiliary:
  vision:
    provider: auto
    model: mlx-community/Qwen3-VL-8B-Instruct-6bit
    base_url: http://127.0.0.1:8080/v1
    api_key: not-needed
    timeout: 120
```

Verify with a screenshot through `vision_analyze`.

## Pitfalls

- **LM Studio does not serve MLX.** It only loads GGUF. Use `mlx_vlm.server` for MLX models.
- **`trust_remote_code` VLMs** (e.g. NVIDIA LocateAnything, custom architectures) won't run in LM Studio at all; need transformers or vLLM with `--trust-remote-code`.
- **Grounding models ≠ general VLMs.** `nvidia/LocateAnything-3B` is a YOLO replacement that returns bboxes for natural-language queries. Bad pick for "describe this screenshot" tasks. For "look and understand", pick a general VLM like Qwen3-VL.
- **Don't preempt cutover.** Keep the old GGUF model installed until the new MLX path is verified working end-to-end (an unverified config change can silently break `vision_analyze`).
- **Memory ceiling on 24 GB Macs**: 8B-6bit (~8 GB resident) + system + browser tabs is fine; 32B models will swap and die.

## User preferences embedded here

- Quality-first quantization: 6-bit / Q6_K default.
- Only add models, don't auto-switch the active model — confirm before flipping `auxiliary.vision.model`.
- 中文交互优先；该模型对中文 OCR / UI 截图理解显著优于 gemma-4-12b。
