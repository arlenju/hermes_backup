Auto-confirm skill installs with `yes | hermes skills install <id>`. For hub skills blocked by DANGEROUS verdict, manually copy SKILL.md to ~/.hermes/skills/<name>/. GitHub fine-grained PATs need Contents: Write permission.
§
Voice pipeline (skill: voice-pipeline): Edge TTS、faster-whisper STT、MP3→SILK为WeChat、MP3→OGG Opus为飞书原生语音气泡 (ffmpeg -c:a libopus -b:a 24k -ar 24000 -ac 1)。飞书网关识别 .opus 为原生语音 via MEDIA:标记。
§
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
Feishu Drive API 需 drive:drive 权限，cli_aaaf8e2f51b8dbb4 未开通。文档导出走 /drive/v1/export_tasks (markdown)。
§
已装 Motrix.app，内置 aria2c: /Applications/Motrix.app/Contents/Resources/engine/aria2c。HF 大文件下载最稳: curl -sIL 跟 302 拿 CDN 签名URL → aria2c -x16 -s16 --lowest-speed-limit=100K --max-tries=20。hf-mirror.com 对 mlx-community/* 会 308 回源，无效。
§
用户日常研究股票/基金。已装 ZhuLinsen/daily_stock_analysis 到 /Users/jushuai/My_Project/11/daily_stock_analysis (独立 venv, 141 deps)。方案A:独立跑+飞书webhook。入口: source venv/bin/activate && python main.py --stocks <codes> | --schedule。配置 .env。