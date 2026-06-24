#!/usr/bin/env python3
"""Post-write verification helper for Feishu sheet writes.
Usage: python3 verify-write.py <sheet_token> <sheet_id>

Checks that cells were written correctly and counts filled cells per column.
"""
import requests, sys

def verify_write(sheet_token, sheet_id, columns=None):
    with open('/Users/jushuai/.hermes/.env') as f:
        for line in f:
            if 'FEISHU_APP_SECRET' in line:
                app_secret = line.split('=',1)[1].strip()
                break
            if 'FEISHU_APP_ID' in line:
                app_id = line.split('=',1)[1].strip()
    
    r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', 
                      json={'app_id': app_id, 'app_secret': app_secret})
    token = r.json()['tenant_access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Data range
    r = requests.get(f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{sheet_token}/values/{sheet_id}!A:A', headers=headers)
    total = len(r.json()['data']['valueRange']['values']) - 1
    
    if columns is None:
        columns = ['B', 'C', 'E', 'F']
    
    print(f'Rows: {total}')
    for col in columns:
        r = requests.get(f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{sheet_token}/values/{sheet_id}!{col}:{col}', headers=headers)
        vals = r.json()['data']['valueRange']['values'][1:]
        filled = sum(1 for v in vals if v and isinstance(v[0], str) and v[0].strip())
        na = sum(1 for v in vals if v and v[0] == '#N/A')
        unsupported = sum(1 for v in vals if v and isinstance(v[0], dict))
        print(f'  Col {col}: filled={filled}, #N/A={na}, UNSUPPORT={unsupported}')
    
    # Spot check a known filled cell
    r = requests.get(f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{sheet_token}/values/{sheet_id}!B6:B6', headers=headers)
    v = r.json()['data']['valueRange']['values']
    if v and v[0]:
        print(f'\nSpot check B6: {str(v[0][0])[:50]}')
    
    all_ok = True
    for v in vals[:100]:
        if v and isinstance(v[0], dict):
            all_ok = False
    print(f'\nNo UNSUPPORT VALUE in first 100 rows: {"✅" if all_ok else "❌"}')
    return all_ok

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 verify-write.py <sheet_token> <sheet_id> [columns...]')
        sys.exit(1)
    verify_write(sys.argv[1], sys.argv[2], sys.argv[3:] if len(sys.argv) > 3 else None)
