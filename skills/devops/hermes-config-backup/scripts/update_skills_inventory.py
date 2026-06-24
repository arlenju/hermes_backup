#!/usr/bin/env python3
"""
Update SKILLS_INVENTORY.md — auto-generates from ~/.hermes/skills/
Run: python3 ~/.hermes/scripts/update_skills_inventory.py

Part of hermes-config-backup skill. For full docs see that skill's SKILL.md.
"""
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
SKILLS_DIR = HERMES_HOME / "skills"

# --- CONFIGURE THESE FOR YOUR REPO ---
INVENTORY_PATH = Path.home() / "My_Project" / "hermes_agent" / "Hermes-Agent" / "SKILLS_INVENTORY.md"
REPO_DIR = Path.home() / "My_Project" / "hermes_agent" / "Hermes-Agent"

CATEGORY_ORDER = [
    ("uncategorized", "🧠", "Uncategorized"),
    ("apple", "🍎", "Apple"),
    ("autonomous-ai-agents", "🤖", "Autonomous AI Agents"),
    ("creative", "🎨", "Creative"),
    ("data-science", "📊", "Data Science"),
    ("devops", "🔧", "DevOps"),
    ("email", "📧", "Email"),
    ("github", "🐙", "GitHub"),
    ("media", "🎵", "Media"),
    ("messaging", "💬", "Messaging"),
    ("meta", "🏭", "Meta"),
    ("mlops", "🔬", "MLOps"),
    ("note-taking", "📝", "Note-taking"),
    ("productivity", "⚡", "Productivity"),
    ("red-teaming", "🔴", "Red-teaming"),
    ("research", "🔬", "Research"),
    ("smart-home", "🏠", "Smart Home"),
    ("social-media", "🐦", "Social Media"),
    ("software-development", "💻", "Software Development"),
]


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from SKILL.md content."""
    meta = {"name": "", "description": "", "category": ""}
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return meta
    front = m.group(1)
    for line in front.split("\n"):
        for key in ("name", "description", "category"):
            m2 = re.match(rf"{key}\s*:\s*\"?(.*?)\"?\s*$", line.strip(), re.IGNORECASE)
            if m2:
                meta[key] = m2.group(1).strip().strip('"').strip("'")
    return meta


def scan_skills() -> dict[str, list]:
    """Scan ~/.hermes/skills/ and return {category: [(name, description), ...]}"""
    skills = {}
    if not SKILLS_DIR.exists():
        return skills

    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir():
            continue

        has_sub_skills = False
        for sub in entry.iterdir():
            if sub.is_dir() and (sub / "SKILL.md").exists():
                has_sub_skills = True
                break

        if has_sub_skills:
            category = entry.name
            for skill_dir in sorted(entry.iterdir()):
                if not skill_dir.is_dir():
                    continue
                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    continue
                content = skill_md.read_text(encoding="utf-8")
                meta = parse_frontmatter(content)
                name = meta["name"] or skill_dir.name
                desc = meta["description"] or "(no description)"
                skills.setdefault(category, []).append((name, desc))
        else:
            skill_md = entry / "SKILL.md"
            if not skill_md.exists():
                continue
            content = skill_md.read_text(encoding="utf-8")
            meta = parse_frontmatter(content)
            name = meta["name"] or entry.name
            desc = meta["description"] or "(no description)"
            category = meta.get("category") or "uncategorized"
            if not category:
                category = "uncategorized"
            skills.setdefault(category, []).append((name, desc))

    return skills


def generate_markdown(skills: dict) -> str:
    """Generate the full SKILLS_INVENTORY.md content."""
    now = datetime.now().strftime("%Y-%m-%d")
    total = sum(len(v) for v in skills.values())

    lines = [
        "# Hermes Agent — Skills Inventory",
        "",
        f"> 自动生成于 {now} | 共 **{total} 个 Skills**",
        "",
        "## 分类目录",
        "",
    ]

    for canonical, icon, display_name in CATEGORY_ORDER:
        if canonical in skills and skills[canonical]:
            label = display_name.lower().replace(" ", "-").replace("--", "-")
            lines.append(f"- [{icon} {display_name}](#{label})")

    if "uncategorized" in skills and skills["uncategorized"]:
        lines.append("- [🧠 Uncategorized](#uncategorized)")

    lines.append("")

    counter = 0
    for canonical, icon, display_name in CATEGORY_ORDER:
        if canonical not in skills or not skills[canonical]:
            continue
        cat_skills = sorted(skills[canonical], key=lambda x: x[0].lower())

        lines.append("---")
        lines.append("")
        lines.append(f"### {icon} {display_name}")
        lines.append("")
        lines.append("| # | Skill | Description |")
        lines.append("|---|-------|-------------|")
        for i, (name, desc) in enumerate(cat_skills, 1):
            counter += 1
            clean_desc = desc.replace("\n", " ").strip()
            lines.append(f"| {counter} | **{name}** | {clean_desc} |")
        lines.append("")

    if "uncategorized" in skills and skills["uncategorized"]:
        cat_skills = sorted(skills["uncategorized"], key=lambda x: x[0].lower())
        lines.append("---")
        lines.append("")
        lines.append("### 🧠 Uncategorized")
        lines.append("")
        lines.append("| # | Skill | Description |")
        lines.append("|---|-------|-------------|")
        for i, (name, desc) in enumerate(cat_skills, 1):
            counter += 1
            clean_desc = desc.replace("\n", " ").strip()
            lines.append(f"| {counter} | **{name}** | {clean_desc} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 汇总统计")
    lines.append("")
    lines.append("| 分类 | 数量 |")
    lines.append("|------|:----:|")
    summary_total = 0
    for canonical, icon, display_name in CATEGORY_ORDER:
        if canonical in skills and skills[canonical]:
            count = len(skills[canonical])
            summary_total += count
            lines.append(f"| {icon} {display_name} | {count} |")
    if "uncategorized" in skills and skills["uncategorized"]:
        count = len(skills["uncategorized"])
        summary_total += count
        lines.append(f"| 🧠 Uncategorized | {count} |")
    lines.append(f"| **合计** | **{summary_total}** |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> 生成工具：Hermes Agent | 脚本：`~/.hermes/scripts/update_skills_inventory.py`")
    lines.append("")

    return "\n".join(lines)


def git_push():
    """Commit and push the inventory file if changed."""
    try:
        os.chdir(str(REPO_DIR))
        result = subprocess.run(
            ["git", "diff", "--quiet", "SKILLS_INVENTORY.md"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("No changes to SKILLS_INVENTORY.md")
            return

        subprocess.run(["git", "add", "SKILLS_INVENTORY.md"], check=True)
        subprocess.run(
            ["git", "commit", "-m", "docs: auto-update skills inventory"],
            check=True, capture_output=True
        )
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Pushed SKILLS_INVENTORY.md to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git error: {e}")
    except Exception as e:
        print(f"⚠️  Error: {e}")


def main():
    skills = scan_skills()
    if not skills:
        print("No skills found!")
        sys.exit(1)

    content = generate_markdown(skills)
    INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    INVENTORY_PATH.write_text(content, encoding="utf-8")
    print(f"✅ Written {len(content)} chars to {INVENTORY_PATH}")
    print(f"   {sum(len(v) for v in skills.values())} skills across {len(skills)} categories")

    git_push()


if __name__ == "__main__":
    main()
