# Hermes 配置备份

当前配置和记忆文件自动备份仓库。

## 结构说明
- `config.yaml` — Hermes Agent 配置文件（自动从 `~/.hermes/config.yaml` 同步）
- `memories/MEMORY.md` — Agent 持久记忆（服务器/邮箱/密钥等信息）
- `memories/USER.md` — 用户偏好设置

## 自动备份
每日凌晨 12:00 由 Hermes cron job 自动备份。
