# Awesome Hermes Agent — Key Projects

Curated from [github.com/0xNyk/awesome-hermes-agent](https://github.com/0xNyk/awesome-hermes-agent).
Ecosystem status: Hermes v0.12.0, 134k+ stars (last reviewed 2026-05-06).

## Quick Start (3-step)

1. Get running → Official Docs quickstart
2. Add first skills → `wondelai/skills` or `litprog-skill`
3. Get a GUI → `hermes-workspace` or `mission-control`

## Categories & Top Picks

### Plugins (pip into Hermes venv + config)
| Project | What it does | Install pattern |
|---------|-------------|-----------------|
| **rtk-hermes** | Terminal output compression 60-90% | brew + pip + plugins.enabled |
| **hermes-plugins** | Goal mgmt, inter-agent bridge, model selection, cost control | pip + plugins.enabled |
| **hermes-web-search-plus** | Multi-provider search (Serper, Tavily, Exa) | pip + plugins.enabled |
| **hermes-weather-plugin** | NWS model imagery, NEXRAD radar | pip + plugins.enabled |
| **rtk-hermes** | Terminal output compression via RTK | brew + pip + plugins.enabled |

### Memory Providers (pip into Hermes venv + memory.provider)
| Project | Type | Key feature |
|---------|------|-------------|
| **Mnemosyne** | Local (SQLite+vec+FTS5) | 98.9% LongMemEval, 23 tools, zero deps |
| **Hindsight** | Cloud (vectorize.io) | retain/recall/reflect, needs API key |
| **mnemo-hermes** | Local (Ollama) | pgvector, 5 tools, no API keys needed |
| **Mnemosyne** (from AxDSan) | Local | Sub-ms, BEAM architecture, TripleStore |

### Tools & Utilities
| Project | Stars | What it does |
|---------|-------|-------------|
| **mission-control** | 3.7k | Fleet dashboard, task dispatch, cost tracking |
| **hermes-workspace** | 500+ | Web GUI: chat, terminal, skills, memory |
| **hermes-web-ui** | 3.6k | Vue3 dashboard, multi-backend, token analytics |
| **hermes-desktop** | beta | Native macOS workspace |
| **SkillClaw** | 705 | Auto-evolve + deduplicate skill library |
| **camofox-browser** | 4k | Stealth headless browser, bypasses Cloudflare |
| **open-design** | 28k | Claude Design alternative, 129 design systems |
| **drawio-skill** | 1.1k | Natural language → draw.io diagrams |

### Integrations
| Project | What it connects |
|---------|-----------------|
| **hermes-nextcloud** | Self-hosted Nextcloud (files, notes, calendar, contacts) |
| **hermes-android** | Android device control |
| **microsoft-workspace-skill** | Outlook/365 via Graph API |
| **hermes-incident-commander** | Autonomous SRE, self-healing |
| **oh-my-hermes** | Multi-agent orchestration (deep-research, triage, autopilot) |
| **personal-api** | Obsidian vault → AI-readable identity layer |

### agentskills.io Ecosystem
| Project | What it does |
|---------|-------------|
| **wondelai/skills** | Cross-platform agent skills (production) |
| **youtube-skills** | YouTube search/transcripts via TranscriptAPI (bypasses cloud IP blocks) |
| **Anthropic-Cybersecurity-Skills** | 753+ MITRE ATT&CK skills (4k+ stars) |
| **chainlink-agent-skills** | Oracle network, CCIP, smart contracts |
| **black-forest-labs/skills** | Official FLUX model skills |
| **AgentCash** | 300+ premium APIs with wallet balance |

## Discovery Workflow

When the user asks "what's useful from awesome-hermes-agent":

1. Load this reference file for the curated list
2. Cross-reference against `skills_list()` to see what's already installed
3. For each candidate, check the repo's README for Hermes-specific install instructions
4. Determine install pattern: hub install, pip plugin, memory provider, or manual copy
5. Batch install all selected projects, then single gateway restart at end
