#!/bin/bash
# ==============================================
# Hermes 自动备份脚本 - 推送到 GitHub 仓库
# ==============================================
# 此脚本由 Hermes cron job 每天凌晨 12:00 执行
# 将 ~/.hermes/config.yaml 和 memory 文件备份到 GitHub
# ==============================================

REPO_DIR="$HOME/.hermes_backup_repo"
HERMES_DIR="$HOME/.hermes"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "===== Hermes 自动备份 $TIMESTAMP ====="

# ========== 1. 确保仓库存在并处于干净状态 ==========
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "仓库不存在，克隆中..."
    gh repo clone arlenju/hermes_backup "$REPO_DIR" 2>&1 || {
        echo "克隆失败"
        exit 1
    }
fi

cd "$REPO_DIR"

# 检查是否卡在 rebase/merge 中，如果有则中止
if [ -d ".git/rebase-merge" ] || [ -d ".git/rebase-apply" ]; then
    echo "检测到卡住的 rebase，执行 git rebase --abort..."
    git rebase --abort 2>/dev/null || true
fi

# 检查是否有 MERGE_HEAD（卡在合并中）
if [ -f ".git/MERGE_HEAD" ]; then
    echo "检测到卡住的 merge，执行 git merge --abort..."
    git merge --abort 2>/dev/null || true
fi

# 如果有未提交的变更，先 stash
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "暂存未提交的变更..."
    git stash push -m "backup-script-auto-stash" 2>/dev/null || true
fi

# ========== 2. 从远程拉取最新状态 ==========
echo "拉取远程最新状态..."
git fetch origin main 2>&1 || echo "⚠️ fetch 失败，继续..."

# 如果本地落后于远程，用 rebase 同步，但忽略冲突
if git merge-base --is-ancestor HEAD origin/main 2>/dev/null; then
    # 本地是远程祖先或相等，直接 fast-forward
    git merge --ff-only origin/main 2>/dev/null || true
else
    # 已分叉，用 rebase 但忽略冲突
    git rebase origin/main 2>/dev/null || {
        echo "⚠️ rebase 冲突，放弃 rebase，重置到 origin/main"
        git rebase --abort 2>/dev/null || true
        git reset --hard origin/main 2>/dev/null
    }
fi

# ========== 3. 复制配置文件 ==========
echo "复制 config.yaml..."
cp "$HERMES_DIR/config.yaml" "$REPO_DIR/config.yaml"

echo "复制 SOUL.md..."
cp "$HERMES_DIR/SOUL.md" "$REPO_DIR/SOUL.md" 2>/dev/null || echo "SOUL.md 不存在，跳过"

echo "复制 memories..."
mkdir -p "$REPO_DIR/memories"
cp "$HERMES_DIR/memories/USER.md" "$REPO_DIR/memories/USER.md" 2>/dev/null || echo "USER.md 不存在，跳过"
cp "$HERMES_DIR/memories/MEMORY.md" "$REPO_DIR/memories/MEMORY.md" 2>/dev/null || echo "MEMORY.md 不存在，跳过"
cp "$HERMES_DIR/memories/"*.md "$REPO_DIR/memories/" 2>/dev/null || echo "其他 memory 文件不存在，跳过"

echo "复制 plugins..."
cp -R "$HERMES_DIR/plugins/" "$REPO_DIR/plugins/" 2>/dev/null || echo "plugins 不存在，跳过"

# ========== 4. 提交并推送 ==========
if git diff --quiet && git diff --cached --quiet; then
    echo "没有变更，跳过提交 ✅"
else
    git add -A
    git commit -m "自动备份 $TIMESTAMP"
    echo "推送中..."
    if git push origin main 2>&1; then
        echo "推送成功 ✅"
    else
        echo "推送失败 ⚠️，尝试强制同步后重试..."
        sleep 2
        git fetch origin main
        git reset --hard origin/main
        # 重新复制文件
        cp "$HERMES_DIR/config.yaml" "$REPO_DIR/config.yaml"
        cp -R "$HERMES_DIR/memories/"*.md "$REPO_DIR/memories/" 2>/dev/null || true
        git add -A
        git commit -m "自动备份 $TIMESTAMP (强制同步)" || true
        git push origin main 2>&1 && echo "重试推送成功 ✅" || echo "重试仍然失败 ⚠️"
    fi
fi

echo "===== 备份完成 ====="
