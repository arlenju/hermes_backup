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
用户日常研究股票/基金。已装 ZhuLinsen/daily_stock_analysis (独立venv,141deps)。入口: source venv/bin/activate && python main.py --stocks <codes> | --schedule。配置 .env。
§
语音链路: 听=Qwen3-ASR-0.6B-8bit (MLX 8bit, stt.provider=qwen3_asr command provider via ~/.hermes/scripts/mlx_asr.sh)。说=Edge TTS小晓 (tts.provider=edge)。飞书原生语音 = OGG Opus via MEDIA:标记。
§
PP-OCRv6 (百度飞桨) 已安装: ~/.hermes/ocr_ppocrv6/venv + ~/.hermes/scripts/ocr_image.sh。PaddleOCR 3.7 + PaddlePaddle 3.3。Hermes 辅助: ocr_image.sh image.jpg [--json]。模型缓存 ~/.paddlex/official_models/ (PP-OCRv6_medium_det/rec)。
§
Agently Mail (QQ邮箱CLI) 已配: npm i -g @tencent-qqmail/agently-cli, 邮箱 arlen0342@agent.qq.com。OAuth凭据存 macOS keychain。skill: ~/.agents/skills/agently-mail。两阶段确认（写操作）。
§
乐享知识库已接入Hermes(lexiang-kb skill)。支持AI搜索/问答/文件上传。关键限制:API只能操作团队知识库,不能操作个人知识库。用户乐享账号名Arlen手机号登录,文档要放个人知识库需用户手动或浏览器登录。已上传7份报告+1份Hermes Bible笔记到示例知识库。用户要求文档分类存放(财经/技术/网络运维)。WeKnora本地部署待探索,未装Docker。
§
用户常分享抖音/头条/X链接，要求研究内容并生成研究报告（Word/PDF）。主题：财经/金融市场（黄金、美股、AI产业链、券商薪酬等）。浏览器+console提取内容→web_search补充→Markdown→md_to_docx.py转Word或Chrome headless转PDF→MEDIA:发飞书。