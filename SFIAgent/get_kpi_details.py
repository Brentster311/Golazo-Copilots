#!/usr/bin/env python
"""Get detailed info about [USGov] 1.05 Azure Tenant Security KPI."""

from s360_client import S360Client
import json
import re
from html import unescape

def strip_html(text):
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

c = S360Client()
user = c.get_current_user()

# [USGov] 1.05 Azure Tenant Security KPI
kpi_id = '11df79b1-bc5d-4d9e-a984-d91c573c45c5'

# Get user's services
lv = c.get_default_landing_view(user.alias)
services = lv.get('SearchDataList', [])
service_ids = [s['Id'] for s in services if s.get('Group') == 'Service']

print(f"User: {user.alias}")
print(f"Services: {[s['Name'] for s in services]}")

# Get all action item metadata
print("\n" + "=" * 80)
print("[USGov] 1.05 Azure Tenant Security")
print("=" * 80)

all_meta = c.get_all_action_item_metadata()
items = all_meta.get('ActionItemMetadataList', [])
item_meta = next((i for i in items if i.get('ActionItemId') == kpi_id), None)

if item_meta:
    print(f"\n--- DESCRIPTION ---")
    desc = strip_html(item_meta.get('Description', ''))
    print(desc[:3000])
    
    print("\n--- KPI OWNERS ---")
    owners = item_meta.get('KpiOwner', '[]')
    if owners:
        try:
            owner_list = json.loads(owners)
            for o in owner_list[:5]:
                print(f"  - {o.get('Name')} ({o.get('Email')})")
        except:
            pass
            
    print("\n--- FAQs ---")
    faqs = item_meta.get('FAQs', '[]')
    if faqs:
        try:
            faq_list = json.loads(faqs)
            for faq in faq_list[:10]:
                print(f"Q: {faq.get('Question')}")
                print(f"A: {strip_html(faq.get('Answer', ''))[:500]}\n")
        except:
            pass

# Get the action items grid
print("\n" + "=" * 80)
print("YOUR ACTION ITEMS")
print("=" * 80)

grid = c.get_action_items_grid(kpi_id=kpi_id, audience=service_ids, sla_type_filter=2)
rows = grid.get('Rows', []) or []
print(f"Found {len(rows)} out-of-SLA items\n")

for i, row in enumerate(rows, 1):
    print(f"\n{'='*70}")
    print(f"ACTION ITEM {i}")
    print(f"{'='*70}")
    
    control_id = row.get('Baseline_Control_ID', 'Unknown')
    subtype = row.get('ActionItemSubtype', '')
    
    print(f"Control ID: {control_id}")
    print(f"SFI Subtype: {subtype}")
    print(f"Service: {row.get('S360_ServiceTreeServiceName')}")
    print(f"Assigned To: {row.get('S360_AssignedToName')}")
    print(f"Due Date: {row.get('dueDate')}")
    print(f"Cloud: {row.get('cloudType')}")
    print(f"Vulnerability Count: {row.get('Vulnerability_Count')}")
    
    remediation = row.get('Remediation_Guide', '')
    if remediation:
        print(f"\n📋 REMEDIATION GUIDE: {remediation}")
    
    details_link = row.get('Link_To_Details', '')
    if details_link:
        # Extract actual URL
        import re
        match = re.search(r'href="([^"]+)"', details_link)
        if match:
            print(f"🔍 VIEW FINDINGS: {match.group(1)}")
