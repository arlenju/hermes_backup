# 工作笔记 - Hermes Agent 日常运维

> 最后更新: 2026-06-10
> 维护人: 晓晓 (Hermes Agent)

---

## 1. 飞书表格数据处理

### 常见任务
- **填充 IP 用途/管理员**：从 IP 数据库或参考表跨表匹配，填充目标表的 B(源地址用途)、C(源地址管理员)、E(目标地址用途)、F(目标地址管理员) 列
- **反向补充 IP 数据库**：从防火墙日志表提取新 IP，追加到 IP 数据库末尾
- **替换"待设置"占位符**：IP 数据库中管理员列为"待设置"的，从参考表匹配真实姓名

### 参考表来源
| 表 | Token | 说明 |
|----|-------|------|
| IP 数据库 | `R1hjsurIAhif1ctTQ1zcz4Y7nwc` | 24K+ 行，A=IP, B=用途, C=管理员 |
| 旧表1 | (历史) | 7,976 行，IP→用途/管理员 |
| 旧表2 | (历史) | 9,799 行，IP→用途/管理员 |
| 新表6 | (历史) | 5,189 行，SourceIP/DestinationIP→用途/管理员 |

### 操作要点
- 使用 feishu-sheet-api skill，通过 REST API 操作
- 先读 A 列确定实际数据范围（避免读空行超时）
- 批量写入（4000 行/批），间隔 0.3s 防限流
- 写完后必须验证：读回样本单元格、统计各列填充数
- `foregroundColor` 不生效（API 返回 code=0 但不可见），用 `backgroundColor` 代替
- "待设置"是普通字符串不是 dict，需单独判断

---

## 2. noVNC 远程桌面

### 服务链路
```
Screen Sharing (5900) ← websockify (6080) ← cloudflared tunnel → mac.210823.xyz
```

### 启动/修复步骤
1. **启动屏幕共享**：`launchctl start com.apple.screensharing`（无需 sudo）
2. **检查 5900 端口**：`lsof -i :5900`，应看到 VNC 协议响应 `RFB 003.889`
3. **启动 websockify**：转发 6080 → 5900
   ```bash
   cd ~/My_Project/noVNC-1.5.0
   python3 -m websockify 6080 127.0.0.1:5900 --web=~/My_Project/noVNC-1.5.0
   ```
4. **检查 cloudflared**：`ps aux | grep cloudflared`，确保隧道在运行
5. **验证**：`curl http://127.0.0.1:6080/vnc.html` 应返回 200

### 常见问题
- **5900 不监听**：屏幕共享服务未运行 → `launchctl start com.apple.screensharing`
- **websockify 转发到 3283 不工作**：ARDAgent 端口不响应 VNC → 改为转发到 5900
- **mac.210823.xyz 跳转登录**：Cloudflare Access 保护，需登录认证
- **cloudflared 用 token 运行**：`cloudflared tunnel run --token <token>`

---

## 3. 模型配置管理

### 当前配置
- **主模型**：minimax-m3（火山引擎 Ark）
- **Fallback 链**：deepseek/deepseek-v4-flash → openrouter/google/gemma-4-31b-it:free
- **本地模型**：LM Studio (127.0.0.1:41343)

### 切换模型
```bash
# 通过 hermes 命令
hermes config set model.provider <provider>
hermes config set model.default <model_name>

# 或直接编辑 config.yaml
hermes config edit
```

### 模型健康监控
- 每小时：`~/.hermes/scripts/model_health.py` — 测试所有模型，输出排名
- 每 6 小时：`model_health.py reorder` — 测试 + 重排 fallback 链

---

## 4. 环境健康检查

### 检查清单
```bash
# 1. 模型状态
hermes doctor
hermes status

# 2. 服务进程
ps aux | grep -E 'websockify|cloudflared|ARDAgent'
lsof -i :5900 -i :6080 -i :3283

# 3. 备份状态
cd ~/.hermes_backup_repo && git log --oneline -3

# 4. 磁盘空间
df -h /

# 5. 飞书/微信网关
hermes gateway status
```

### 定期检查项
- 模型链路是否正常（主模型 + fallback）
- noVNC 服务是否在线
- 每日备份是否成功
- 飞书/微信网关连接状态

---

## 5. GitHub 备份

### 仓库信息
- **仓库**：`arlenju/hermes_backup`
- **本地路径**：`~/.hermes_backup_repo/`
- **备份内容**：config.yaml, SOUL.md, memories/, plugins/, 工作笔记
- **备份脚本**：`~/.hermes/scripts/hermes_backup.sh`
- **定时**：每日 00:00（cron job: `ee402d24c4ef`）

### 手动备份
```bash
cd ~/.hermes_backup_repo
cp ~/.hermes/config.yaml .
cp ~/.hermes/SOUL.md .
cp -R ~/.hermes/memories/ .
cp -R ~/.hermes/plugins/ .
git add -A
git commit -m "手动备份 $(date)"
git push
```

### 技能清单更新
- 每日 03:00 自动更新（cron job: `492bba53cb2c`，no_agent 模式）
- 脚本：`~/.hermes/scripts/update_skills_inventory.py`

---

## 6. 飞书/微信平台

### 平台信息
- **飞书**：DM chat_id = `oc_7fcb7be5745a24bc07b2f9dd43b0ed7f`
- **微信**：Home channel = `o9cq809t7oibCa6W31PGdnQJOskQ@im.wechat`
- **TTS 语音**：zh-CN-XiaoxiaoNeural（小晓，温柔女声）
- **语音消息**：MP3 → OGG Opus（ffmpeg -c:a libopus -b:a 24k -ar 24000 -ac 1）

### 用户偏好
- 称呼：帅哥
- 沟通风格：极简直接，短指令
- 用户姓名：鞠帅
- 时区：东八区

---

## 7. 常用命令速查

```bash
# Hermes 操作
hermes doctor                    # 健康检查
hermes status                    # 状态查看
hermes config edit               # 编辑配置
hermes cron list                 # 查看定时任务
hermes gateway status            # 网关状态
hermes skills list               # 技能列表

# 飞书表格操作
# 使用 feishu-sheet-api skill 中的 Python 脚本

# noVNC 维护
launchctl start com.apple.screensharing    # 启动屏幕共享
lsof -i :5900                              # 检查 VNC 端口

# Git 备份
cd ~/.hermes_backup_repo && git status
```
