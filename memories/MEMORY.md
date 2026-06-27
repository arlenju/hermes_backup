Fallback: deepseek-v4-flash → openrouter/gemma-4-31b-it:free。本地视觉: MLX :8080, model=~/.lmstudio/models/mlx-community/Qwen3-VL-8B-Instruct-6bit (M5/24G/7.3GB MLX 6bit)。launchd com.hermes.mlx-vision 托管，KeepAlive自重启+开机自启。日志 ~/.hermes/logs/mlx-vision.{log,err}。auxiliary.vision 已切 8080。旧 gemma-4-12b@1234 备用。ARK 无 vision。
§
Hermes runtime venv: ~/.hermes/hermes-agent/venv/ (CLI at ~/.local/bin/hermes execs venv/bin/hermes)。Hermes features (faster-whisper, mlx-vlm 等) pip 装这个, 不是项目 dev venv ~/My_Project/hermes_agent/Hermes-Agent/venv/。
§
备份: GitHub arlenju/hermes_backup (cron 00:00, ~/.hermes/scripts/hermes_backup.sh)。备份 config.yaml(脱敏)+SOUL.md+memories+mnemosyne+plugins+skills(rsync)+LaunchAgents/com.hermes.*+scripts+WORK_NOTES.md。.env/auth.json 本地留。
§
macOS 26.3: launchctl 从 gateway 进程内统统报 I/O error + safety 拦。必须用户外部终端跑 launchctl load/kickstart。合盖断连: `caffeinate -d -i -m -t 86400` 后台 + gateway 后台。
§
用户要求：做事情做了一定要先自己检查，做完再汇报。不要没检查就汇报或问"好了吗"。
§
Custom provider ark (火山): deepseek-v4-pro, deepseek-v4-flash, minimax-m3, glm-5.1。切换 /model custom:ark:<id>。
§
用户日常研究股票/基金。已装 ZhuLinsen/daily_stock_analysis 到 /Users/jushuai/My_Project/11/daily_stock_analysis (独立 venv, 141 deps)。方案A:独立跑+飞书webhook。入口: source venv/bin/activate && python main.py --stocks <codes> | --schedule。配置 .env。
§
语音链路: 听=Qwen3-ASR-0.6B-8bit (MLX 8bit, stt.provider=qwen3_asr command provider via ~/.hermes/scripts/mlx_asr.sh)。说=Edge TTS小晓 (tts.provider=edge)。飞书原生语音 = OGG Opus via MEDIA:标记。
§
PP-OCRv6 (百度飞桨) 已安装: ~/.hermes/ocr_ppocrv6/venv + ~/.hermes/scripts/ocr_image.sh。PaddleOCR 3.7 + PaddlePaddle 3.3。Hermes 辅助: ocr_image.sh image.jpg [--json]。模型缓存 ~/.paddlex/official_models/ (PP-OCRv6_medium_det/rec)。
§
Agently Mail (QQ邮箱CLI) 已配: npm i -g @tencent-qqmail/agently-cli, 邮箱 arlen0342@agent.qq.com。OAuth凭据存 macOS keychain。skill: ~/.agents/skills/agently-mail。两阶段确认（写操作）。
§
Agently Mail: npm i -g @tencent-qqmail/agently-cli v1.0.5, skill ~/.agents/skills/agently-mail。邮箱 arlen0342@agent.qq.com, 用户 jushuai_01@163.com。OAuth keychain。两阶段确认。
§
GitHub 大 repo clone 超时时用 sparse checkout: git clone --depth 1 --filter=blob:none --sparse <url> → git sparse-checkout set skills docs。ppt-master (243MB→96MB) 验证通过。