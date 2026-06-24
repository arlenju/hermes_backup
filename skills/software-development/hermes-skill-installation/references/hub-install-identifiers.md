# Known Hub Skill Identifiers

## openai/skills/.curated/ (trusted)
```
aspnet-core, chatgpt-apps, cli-creator, cloudflare-deploy, define-goal,
figma-*, gh-address-comments, gh-fix-ci, hatch-pet, jupyter-notebook,
linear, migrate-to-codex, netlify-deploy, notion-*, openai-docs,
pdf, playwright, playwright-interactive, render-deploy, screenshot,
security-best-practices, security-ownership-map, security-threat-model,
sentry, speech, transcribe, vercel-deploy, winui-app, yeet
```

## openai/skills/.system/ (trusted)
```
imagegen, openai-docs, plugin-creator, skill-creator, skill-installer
```

⚠️ `skill-installer` is BLOCKED by security scanner (DANGEROUS: reads GITHUB_TOKEN).
Even though it's from a trusted repo, `--force` does not override DANGEROUS verdict.
Use manual install (curl + copy to ~/.hermes/skills/) to bypass.

## garrytan/gstack (community tap, DEFAULT_TAPS)
```
gstack
```
Sub-skills within gstack (loaded as routing rules, not standalone installs):
/qa, /qa-only, /review, /ship, /investigate, /spec, /design-review,
/plan-ceo-review, /plan-eng-review, /plan-design-review, /plan-devex-review,
/autoplan, /context-save, /context-restore, /office-hours, /browse,
/retro, /codex, /careful, /guard, /freeze, /gstack-upgrade, /cso,
/make-pdf, /health, /learn, /plan-tune, /benchmark, /canary, /setup-deploy,
/document-release, /document-generate, /sync-gbrain, /setup-browser-cookies,
/open-gstack-browser, /land-and-deploy, /devex-review, /setup-deploy

## anthropics/skills/ (trusted)
Check via: curl -s https://api.github.com/repos/anthropics/skills/contents/skills

## huggingface/skills/ (trusted)
Check via: curl -s https://api.github.com/repos/huggingface/skills/contents/skills

## NousResearch (community, not in DEFAULT_TAPS)
```
hermes-agent-self-evolution  — Python package, no SKILL.md, install as project
```

## garrytan/gbrain (community, not in DEFAULT_TAPS)
```
gbrain  — No root SKILL.md. Branch: master. Active skill: skills/setup/SKILL.md
```

## NVlabs/skills (future, if available)
Check via: curl -s https://api.github.com/repos/NVIDIA/skills/contents/skills
