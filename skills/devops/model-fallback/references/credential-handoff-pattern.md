---
name: credential-handoff-pattern
description: When the agent needs a user credential (API key, OAuth token, account login), use the handoff pattern: agent tells user the path, user creates the credential themselves, user pastes the key string back, agent writes + probes. Never log into the user's web accounts via browser automation.
type: reference
---

# Credential Handoff Pattern

## When to Use

- The task requires a credential the agent doesn't already have
  (new API key, account login, OAuth scope, billing access).
- The user has the account and can produce the credential in under
  5 minutes via a documented provider console.
- Examples from this session: Volcengine ARK standard inference
  key (for vision), GitHub PAT (for repos), OpenAI platform key
  (for embeddings), Google Cloud service account.

## Why This Pattern Exists

**Never log into the user's web account via browser automation.**
Driving a real login flow — SMS codes, slider captchas, 2FA,
session cookies — has a bad cost/benefit ratio:

- **Security risk**: a successful login exposes everything
  (billing, all keys, all data, account settings) for the rest
  of the session.
- **Friction**: providers build anti-automation into their
  login flows on purpose. SMS, captcha, 2FA, "unusual activity
  detected" emails — these are not edge cases, they are the
  happy path for an unrecognized browser.
- **Token cost**: a 10-minute browser automation session burns
  context the user is paying for.
- **User control**: when the user creates the key themselves,
  they keep the lifecycle in their own hands (rotation, scope
  changes, revocation). The agent should be a one-time consumer,
  not an account operator.

**The right pattern is to split the work** — the user does the
human part (auth + 2FA), the agent does the machine part (config
write + live verification).

## The 4-Step Handoff Template

### Step 1 — Identify the exact credential needed

Before telling the user anything, **identify the specific credential
type and scope** the task requires. For Volcengine ARK vision models:

- Type: API Key (Bearer token, format `ark-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
- Scope: standard inference (NOT Agent Plan — those are disjoint keys)
- Permission: at minimum "视觉理解 / multimodal understanding"
- Where it's created: ARK console → API Key 管理 → 创建 API Key

For other providers, do the same scoping. Don't tell the user
"go to the console and make a key" — that's vague and they'll
make the wrong one. Tell them exactly which page, which button,
which scope to check.

### Step 2 — Send the user a 3-bullet instruction, not a 10-step tutorial

Format the user-facing instruction as **at most 3 bullets**, each
one a single concrete action. The whole message should fit in one
chat screen. Example from a real session:

> 帅哥去控制台开个 Key 给晓晓吧：
> 1. 打开 https://console.volcengine.com/ark → API Key 管理
> 2. 创建 API Key，权限范围勾「**在线推理** + **视觉理解**」
>    （不要勾 Agent Plan，那个不支持视觉）
> 3. 复制生成的 Key（`ark-xxxx...` 开头）发我

This is the maximum length. If you find yourself writing a 4th
bullet, you're probably explaining too much — cut.

### Step 3 — Wait for the key string. Do NOT pre-write config.

**The agent should NOT pre-write `auxiliary.vision.api_key` with
a placeholder or the old broken key** while waiting. The config
file write is cheap and reversible, but a wrong value sitting in
config.yaml can trigger auto-failover to a bad model on the next
session start. Better: keep the old config as-is, do the write
+ probe atomically when the key arrives.

Exception: pre-writing non-credential fields (model name, base_url,
provider, timeout) is fine and useful — the user can confirm the
configuration is what they expected while the key is being
created.

### Step 4 — When the key arrives: write + probe in one atomic step

```bash
# Single-value writes (Hermes security policy blocks direct
# file edits, but `hermes config set` is the CLI escape hatch)
hermes config set auxiliary.vision.api_key "ark-NEW_KEY_HERE"
```

Then **immediately** run the live probe — never write the key
and then ask "want me to test it?". The probe IS the test, the
test IS the delivery. See `hermes-vision-model-setup.md` for
the verified Python probe template.

## Edge Cases

### User has already given a credential (key, password) in chat

The credential is now in the chat log. The agent should:

1. Use it as transient input for the config write, **not save it
   to memory or any persistent store**.
2. After the write succeeds, **redact or summarize** the
   conversation turn (memory rules already cover this for sessions,
   but be mindful).
3. If the key needs to persist in `.env`, use the standard
   `hermes config set auxiliary.vision.api_key "ark-..."` path —
   this writes to `config.yaml`, not `.env`. The literal-key
   rule (pitfall #6 in main SKILL.md) applies.

### User insists "你自己去弄" / "you do it yourself"

Ask once: "好，那我需要你的账号 + 密码 / 2FA 码 / 短信码 — 你愿意提供吗？".
If yes, follow their direction. **If at any point a credential
exchange fails or feels stuck, abort the automation immediately
and revert to the handoff pattern** — don't try to power through
a broken login.

#### Real-World Flow: ARK Console Phone Login (Captcha + SMS)

When the user says "去浏览器打开弄一下" and provides their phone number,
the Volcengine ARK console login flow has a specific sequence:

1. Navigate to `https://console.volcengine.com/ark/region:ark+cn-beijing/`
   → auto-redirects to `signin.volcengine.com`
2. Switch to "手机号登录" tab (click the tab element `@e27`)
3. Fill in the phone number in the `textbox` field
4. **Captcha gate**: the "获取验证码" button is disabled until a
   graphic captcha is entered. There is a separate `textbox` field
   (usually the second one on the form) for the captcha. The user
   must see the captcha image — take a screenshot via
   `browser_vision` (even if vision analysis fails, the screenshot
   file is still saved) and send it to the user via `MEDIA:<path>`.
5. User reads the captcha from the screenshot and tells the agent
6. Agent fills the captcha → clicks "获取验证码"
7. User receives SMS code and sends it to the agent
8. Agent fills the SMS code → clicks "登录 / 注册"

**Important caveat**: the captcha image is typically rendered in an
iframe or as a background image. `browser_vision` with
`question="页面上有没有图形验证码图片"` is the right probe. If the
vision model isn't configured yet (e.g. you're in the process of
setting it up), the screenshot file itself (`screenshot_path`) is
still captured — send it to the user so they can read the captcha
themselves.

**When to abort this flow**: if at any point the page throws a
captcha harder than a simple text/number (slider, puzzle, click-in-order),
abort immediately and revert to the 4-step handoff template. These
are designed to block automation and will waste 10+ minutes of
session time.

### The credential requires a paid plan or a free trial activation

Hand off. The user has the payment instrument, the agent does
not (and shouldn't, for spending safety).

### The credential can be created by the agent in a sandboxed tenant

Some providers (e.g. a free-tier OpenAI account created by the
agent) — if the user explicitly says "create a new throwaway
account", this is OK. Default to user-created.

## Real Session Example (Volcengine ARK, June 2026)

The user asked: "用豆包的视觉模型" (use Doubao's vision model).
The agent's first attempt was to drive the ARK console login via
browser automation. After the login page loaded, the agent
self-corrected and pivoted to the handoff pattern:

1. Identified the credential: standard inference API key with
   visual understanding permission (the Agent Plan key the user
   already had did NOT support vision — verified by live test
   returning 404 `UnsupportedModel`).
2. Sent a 3-bullet instruction with the exact console path and
   the exact permission scope to check.
3. The user's next message was the new key string.
4. Agent wrote the new key + ran the live probe in one turn.

Outcome: config + verified in one round trip. The pivot away
from browser automation was the right call — SMS codes and
2FA would have eaten the next 10 minutes of session time.

## See Also

- Main `model-fallback` SKILL.md → "Verification before reporting
  success" pitfall (#11) and "Never log into the user's web
  accounts" pitfall (#12)
- `hermes-vision-model-setup.md` → live probe template for the
  ARK vision case
- `custom-provider-ark-quickstart.md` → general ARK setup
  walkthrough (overlaps on credential creation, but broader)
