"""Debug: Query MS Graph for muralic's org — manager chain UP and direct reports DOWN."""
import sys, json, requests
sys.path.insert(0, 'SFIReporter/src')
sys.path.insert(0, 'src')
sys.path.insert(0, 'accia-s360/src')
from sfi_reporter.data import get_client

client = get_client()
token = client._auth.get_graph_token()
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
GRAPH = "https://graph.microsoft.com/v1.0"

def graph_get(path):
    r = requests.get(f"{GRAPH}{path}", headers=headers, timeout=15)
    if r.status_code == 200:
        return r.json()
    print(f"  ERROR {r.status_code}: {r.text[:200]}")
    return None

# --- Walk UP: manager chain ---
print("=" * 60)
print("MANAGER CHAIN (walking UP from muralic)")
print("=" * 60)
alias = "muralic"
for i in range(10):  # max 10 levels
    data = graph_get(f"/users/{alias}@microsoft.com?$select=displayName,mailNickname,jobTitle,department")
    if data:
        print(f"  Level {i}: {data.get('displayName')} ({data.get('mailNickname')}) — {data.get('jobTitle')}, {data.get('department')}")
    mgr = graph_get(f"/users/{alias}@microsoft.com/manager?$select=displayName,mailNickname,jobTitle")
    if mgr:
        alias = mgr.get('mailNickname', '')
        if not alias:
            break
    else:
        print("  (no manager)")
        break

# --- Walk DOWN: direct reports ---
print()
print("=" * 60)
print("DIRECT REPORTS (muralic)")
print("=" * 60)
reports = graph_get("/users/muralic@microsoft.com/directReports?$select=displayName,mailNickname,jobTitle,department")
if reports and 'value' in reports:
    for r in reports['value']:
        print(f"  {r.get('displayName')} ({r.get('mailNickname')}) — {r.get('jobTitle')}")

    # --- Walk DOWN one more level: each direct's reports ---
    for r in reports['value']:
        sub_alias = r.get('mailNickname')
        if sub_alias:
            sub_reports = graph_get(f"/users/{sub_alias}@microsoft.com/directReports?$select=displayName,mailNickname,jobTitle")
            if sub_reports and sub_reports.get('value'):
                print(f"\n  {r.get('displayName')}'s direct reports:")
                for sr in sub_reports['value']:
                    print(f"    {sr.get('displayName')} ({sr.get('mailNickname')}) — {sr.get('jobTitle')}")
else:
    print("  No direct reports found")
