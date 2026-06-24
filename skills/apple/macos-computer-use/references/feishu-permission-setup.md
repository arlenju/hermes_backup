# Feishu Developer Console Permission Setup via computer-use

## Context
Adding Drive API permissions to a Feishu app requires accessing the Developer Console at `open.feishu.cn`. The console enforces QR-code login (no password auth), so `browser_*` tools can't log in. Use `computer_use` to drive the user's Safari/Chrome which already has the login session.

## Steps

### 1. Launch Safari and navigate to permission page
```python
call_mcp("launch_app", {"name": "Safari"})
# Get the PID from the response
call_mcp("hotkey", {"pid": PID, "keys": ["cmd", "l"]})
call_mcp("type_text", {"pid": PID, "text": "https://open.feishu.cn/app/{APP_ID}/permission"})
call_mcp("hotkey", {"pid": PID, "keys": ["return"]})
```

### 2. Navigate to the auth URL for specific permissions
The direct auth URL with pre-selected permissions:
```
https://open.feishu.cn/app/{APP_ID}/auth?q=drive:drive,drive:drive:readonly,space:document:retrieve&op_from=openapi&token_type=tenant
```

### 3. Interact with the permission dialog
The permission dialog is a web SPA. AXPress often fails on web buttons. Use these strategies:

- **Checkbox toggle**: Click the first checkbox (element index ~6), then use Tab+Space for subsequent ones
- **Confirm button**: The "确认开通权限" button is also a web element. Try Tab navigation to reach it, then Enter
- **Coordinate click**: If keyboard navigation fails, use coordinate-based click

### 4. Handle "需审核权限"
`drive:drive`, `drive:drive:readonly`, and `space:document:retrieve` are all "需审核权限" (requires admin approval). After submitting, the company's Feishu admin must approve. The API will return `code: 99991672` until approved.

### 5. Verify via API
```bash
source ~/.hermes/.env
python3 -c "
import os, json, requests
BASE = 'https://open.feishu.cn/open-apis'
r = requests.post(f'{BASE}/auth/v3/tenant_access_token/internal',
    json={'app_id': os.environ['FEISHU_APP_ID'], 'app_secret': os.environ['FEISHU_APP_SECRET']}, timeout=15)
token = r.json().get('tenant_access_token')
headers = {'Authorization': f'Bearer {token}'}
r = requests.get(f'{BASE}/drive/v1/files', headers=headers, params={'page_size': 5}, timeout=30)
print(r.json())
# Expected on success: {"code": 0, "data": {"files": [...]}}
# Expected on failure: {"code": 99991672, "msg": "Access denied..."}
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `AXPress returned -25202` | Web element doesn't support AXPress | Use Tab+Space keyboard nav or coordinate click |
| `code: 99991672` | Permission not granted or not approved | Check if admin approved; check if app version was published |
| QR-code login wall | Console forces mobile scan | Use computer_use to drive user's already-logged-in browser |
| Element indices shift | SPA re-renders after each click | Re-capture (get_window_state) after every action |
