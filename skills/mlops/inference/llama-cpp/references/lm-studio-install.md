# 下载 GGUF 模型并安装到 LM Studio

> 适用场景：从 Hugging Face 下载 GGUF 量化模型，放入 LM Studio 使用

## 工作流

### 1. 查找模型文件

```bash
# 查看 repo 中的 GGUF 文件列表
curl -s "https://huggingface.co/api/models/<repo>/tree/main?recursive=true" | \
  python3 -c "import json,sys; [print(f['path'],f['size']) for f in json.load(sys.stdin) if f['type']=='file' and f['path'].endswith('.gguf')]"
```

### 2. 选择量化版本

| 量化 | 质量 | 大小参考（12B 模型） | 适用场景 |
|------|------|---------------------|---------|
| Q2_K | 最低 | ~4.5 GB | 内存紧张 |
| Q4_K_M | 推荐 | ~6.9 GB | 日常使用（甜点） |
| Q5_K_M | 较好 | ~8.0 GB | 质量优先 |
| Q6_K | 很好 | ~9.1 GB | 接近无损 |
| Q8_0 | 几乎无损 | ~11.8 GB | 大内存 |

### 3. 下载

#### 方式 A：`hf` CLI（推荐，支持断点续传）

```bash
# 安装 hf CLI
curl -LsSf https://hf.co/cli/install.sh | bash -s

# 登录（可选，公开模型不需要）
hf auth login

# 下载单个文件到指定目录
hf download <org>/<repo> --include <filename.gguf> --local-dir <目标目录>
```

**注意：** `huggingface-cli` 已废弃，使用 `hf` 替代。

#### 方式 B：aria2（多线程下载，适合大文件）

```bash
# 安装
brew install aria2

# 多线程下载（4 线程）
aria2c -x 4 -s 4 \
  "https://huggingface.co/<org>/<repo>/resolve/main/<filename.gguf>" \
  -d <目标目录>
```

#### 方式 C：curl（断点续传）

```bash
curl -L -C - -o <filename.gguf> \
  "https://huggingface.co/<org>/<repo>/resolve/main/<filename.gguf>"
```

### 4. 安装到 LM Studio

LM Studio 模型目录：`~/.lmstudio/models/`

```bash
# 创建模型目录（按 组织/模型名 组织）
mkdir -p ~/.lmstudio/models/<org>/<model-name>

# 放入 GGUF 文件
mv <filename.gguf> ~/.lmstudio/models/<org>/<model-name>/
```

LM Studio 会自动扫描 `~/.lmstudio/models/` 下的模型，重启即可看到。

### 5. 验证

```bash
# 检查文件
ls -lh ~/.lmstudio/models/<org>/<model-name>/
```

打开 LM Studio → 模型列表 → 应该能看到新模型。

## 国内网络加速

从国内访问 Hugging Face 可能超时：

### 方式 A：HF 镜像站

```bash
# 使用 HF 镜像
export HF_ENDPOINT=https://hf-mirror.com
hf download <org>/<repo> --include <filename.gguf> --local-dir <目标目录>
```

### 方式 B：aria2 + 镜像

```bash
aria2c -x 8 -s 8 \
  "https://hf-mirror.com/<org>/<repo>/resolve/main/<filename.gguf>" \
  -d <目标目录>
```

### 方式 C：用户本地下载

如果代理也不通，告诉用户：
1. 下载链接：`https://huggingface.co/<org>/<repo>/resolve/main/<filename.gguf>`
2. 目标目录：`~/.lmstudio/models/<org>/<model-name>/`
3. 用户用自己已有的下载工具下好后放进去

## LM Studio 配置要点

- 模型放 `~/.lmstudio/models/` 下，按 `组织/模型名` 组织
- LM Studio 自动扫描该目录，无需手动导入
- 如果模型使用特殊 chat template（如 Gemma 4 的 thought channel），LM Studio 会自动识别 GGUF 内嵌的 template
- 建议在 LM Studio 中设置：`temp 1.0, top_p 0.95, top_k 64`（编码场景可调低 temp）
