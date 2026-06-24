# Codex++ Repair Guide

Codex++ is a tweak system for the Codex desktop app. When Codex auto-updates, it overwrites the Codex++ patch, causing the "Codex++ needs to restart Codex" popup.

## macOS App Management Block

On macOS (especially Tahoe 26.x), direct modification of `/Applications/Codex.app` is blocked by **macOS App Management** permissions with error:

```
Cannot write to /Applications/Codex.app/Contents/Resources.
macOS App Management is blocking modification of /Applications/Codex.app/Contents/Resources.
EPERM: operation not permitted, open '.../.codexpp-write-probe'
```

Running `codexplusplus repair` or `codexplusplus install` directly fails even from Terminal with App Management permission granted.

## Workaround: Patch in /tmp, Swap Back

```bash
# 1. Uninstall old patch
codexplusplus uninstall

# 2. Copy to temp location (bypasses App Management)
cp -R /Applications/Codex.app /tmp/CodexPatched.app

# 3. Patch the copy (skip resigning — we'll sign after swap)
codexplusplus install --app /tmp/CodexPatched.app --resign false

# 4. Swap: move original aside, move patched in
mv /Applications/Codex.app /Applications/Codex.app.bak
mv /tmp/CodexPatched.app /Applications/Codex.app

# 5. Ad-hoc sign the patched app
codesign --force --deep --sign - /Applications/Codex.app

# 6. Update state.json to point to correct appRoot
# Edit ~/Library/Application Support/codex-plusplus/state.json
# Set "appRoot" to "/Applications/Codex.app" and "resigned" to true

# 7. Clean up backup
rm -rf /Applications/Codex.app.bak

# 8. Verify
codexplusplus status
```

## Verification

`codexplusplus status` should show:
- `app root: /Applications/Codex.app`
- `resigned: true`
- `integrity: current asar matches patched`
- `plist hash: OK`

## Notes

- The `--resign false` flag is critical when patching in /tmp — codesign fails on /tmp paths with "unsealed contents present in the bundle root"
- After swapping back to /Applications, ad-hoc signing works fine
- The watcher (launchd) is installed during `install` and auto-repairs on future updates
