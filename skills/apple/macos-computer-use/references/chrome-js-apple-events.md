# Chrome JavaScript from Apple Events (CUA browser automation)

## Why this matters

When driving Chrome on macOS via the CUA `mcp_cua_driver_page` tool, the `execute_javascript` action requires Chrome to have **"Allow JavaScript from Apple Events"** enabled. Without this, you get:

```
osascript error: "Google Chrome" encountered an error:
JavaScript for automation is disabled.
To enable, go to View > Developer > Allow JavaScript from Apple Events (12)
```

## Enabling it via the CUA page tool

The `mcp_cua_driver_page` tool has a built-in action to enable this:

```python
mcp_cua_driver_page(
    action="enable_javascript_apple_events",
    bundle_id="com.google.Chrome",
    user_has_confirmed_enabling=True  # REQUIRED — fails if omitted
)
```

**Effects:**
- Chrome quits (saves tabs, restores on next launch)
- Enables the preference
- Relaunches Chrome
- The user sees a brief dialog asking for permission
- After relaunch, `mcp_cua_driver_page(action="execute_javascript", ...)` works

## Required: user confirmation

The first call without `user_has_confirmed_enabling=True` returns:

```
Set user_has_confirmed_enabling=true to proceed. This will quit and relaunch the browser.
```

Always **ask the user first** with a `clarify()` call before passing `true`. Show them that Chrome will be restarted and tabs will be restored.

## Alternative: address bar navigation (no JS needed)

If you just need to navigate to a URL (not execute custom JS), use the address bar instead — no JS Apple Events required:

1. `mcp_cua_driver_get_window_state(pid=CHROME_PID, window_id=WID)` to find the address bar element index
2. `mcp_cua_driver_click(pid=..., window_id=..., element_index=N)` to focus the address bar
3. `mcp_cua_driver_type_text(pid=..., text="https://...")` to type the URL
4. `mcp_cua_driver_press_key(pid=..., key="return")` to navigate

## ⚠️ Pitfall: Omnibox dropdown blocks navigation

After typing a URL and pressing Return, Chrome may show an **Omnibox search suggestion popup** instead of navigating. This happens when:

- The address bar loses focus
- Chrome auto-completes with a history suggestion
- The keypress lands on the dropdown instead of the URL

**Fix:** Press Escape first to dismiss the dropdown, then press Return again:

```python
mcp_cua_driver_type_text(pid=..., text="https://github.com/...")
mcp_cua_driver_press_key(pid=..., key="return")
# If page doesn't navigate (still shows "新标签页" or previous page):
mcp_cua_driver_press_key(pid=..., key="escape")   # dismiss Omnibox
mcp_cua_driver_press_key(pid=..., key="return")    # navigate
```

## After enabling: querying page content

Once JS Apple Events works, you have three ways to inspect page content:

### 1. Execute JavaScript

```python
mcp_cua_driver_page(
    action="execute_javascript",
    pid=CHROME_PID,
    window_id=WID,
    javascript="document.querySelector('h1')?.textContent"
)
```

### 2. Query DOM (returns structured element data)

```python
mcp_cua_driver_page(
    action="query_dom",
    pid=CHROME_PID,
    window_id=WID,
    css_selector="a"
)
# Returns: [{"tagName": "A", "textContent": "link text", "href": "..."}, ...]
```

### 3. Get visible text

```python
mcp_cua_driver_page(
    action="get_text",
    pid=CHROME_PID,
    window_id=WID
)
```

## Finding the right Chrome PID and window_id

```python
# List all windows to find Chrome's main browsing window
mcp_cua_driver_list_windows(pid=CHROME_PID)
# Look for the window with the title matching the current page
# (e.g., "Repository search results - Google Chrome - username")
```

Chrome has many helper windows (toolbars, popups, the tab strip). The main content window is the one with `is_on_screen=true` and a meaningful title. Filter by `on_screen_only=False` to see all windows including minimized ones.

## Filtering large AX trees with `query`

Chrome pages (especially GitHub, SPAs) can produce **1400+ element accessibility trees** that are truncated at 2000 nodes. Navigating these raw is impractical.

**Use `get_window_state` with the `query` parameter** to filter the AX tree to matching lines plus their ancestor chain:

```python
# Filter tree to only elements matching "hermes"
mcp_cua_driver_get_window_state(
    pid=CHROME_PID,
    window_id=WID,
    query="hermes"
)

# Filter by star counts to find repo metadata
mcp_cua_driver_get_window_state(
    pid=CHROME_PID,
    window_id=WID,
    query="stars"
)

# Filter by a repo name
mcp_cua_driver_get_window_state(
    pid=CHROME_PID,
    window_id=WID,
    query="obsidian-skills"
)
```

The `query` is case-insensitive substring match against line content. It keeps the full ancestor chain so you can still see the element context. Element indices remain valid — filtering only trims the rendered Markdown output.

**Complement with `mcp_cua_driver_page(action="query_dom", ...)`** for structured data from web pages (returns tag name, text content, href, etc. in JSON).

## Known limitations

- **One-time enable**: The JS Apple Events setting persists across Chrome restarts once enabled. You only need to do this once.
- **Bundle ID is required**: Pass `bundle_id="com.google.Chrome"` — the `pid` parameter alone is not accepted by the `enable_javascript_apple_events` action.
- **Safari doesn't need this**: Safari's WebKit inspector server works via `WEBCLASS` env variable. The `enable_javascript_apple_events` action is Chrome/Brave/Edge-specific.
