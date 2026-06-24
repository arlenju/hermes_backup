# Hermes Agent Self-Evolution — 架构参考

来源：https://github.com/NousResearch/hermes-agent-self-evolution 的 README.md 和 PLAN.md

## 引擎

| 引擎 | 用途 | 许可证 |
|------|------|--------|
| **DSPy + GEPA** | 反思式提示进化 — 读取执行踪迹，提出定向突变 | MIT |
| **Darwinian Evolver** | 代码进化，基于 Git 的生物体 | AGPL v3 (外部 CLI) |

## 优化阶段

| 阶段 | 目标 | 状态 |
|------|------|------|
| Phase 1 | Skill 文件 (SKILL.md) | ✅ 已实现 |
| Phase 2 | Tool 描述 | 🔲 规划中 |
| Phase 3 | System prompt 段落 | 🔲 规划中 |
| Phase 4 | Tool 实现代码 | 🔲 规划中 |
| Phase 5 | 持续改进流水线 | 🔲 规划中 |

## 约束门 (Guardrails)

每个进化变体必须通过：
1. 完整测试套件 — `pytest tests/ -q` 必须 100% 通过
2. 大小限制 — Skills ≤15KB, tool 描述 ≤500 字符
3. 缓存兼容性 — 不允许对话中途变更
4. 语义保持 — 不能偏离原始目的
5. PR 审查 — 所有变更经过人工审查

## 项目结构

```
hermes-agent-self-evolution/
├── evolution/
│   ├── core/           # 核心引擎 (config, dataset, fitness, constraints)
│   ├── skills/         # Skill 进化 (evolve_skill.py, skill_module.py)
│   └── tools/          # Tool 描述进化 (规划中)
├── datasets/           # 评估数据集
├── reports/            # 生成的报告
├── tests/              # 测试套件
├── generate_report.py  # 报告生成器
└── PLAN.md             # 完整架构计划
```
