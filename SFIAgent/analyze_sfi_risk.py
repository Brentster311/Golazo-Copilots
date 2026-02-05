#!/usr/bin/env python
"""Analyze SFI items by risk and count."""

from s360_client import S360Client

c = S360Client()
user = c.get_current_user()
lv = c.get_default_landing_view(user.alias)
services = lv.get('SearchDataList', [])
service_ids = [s['Id'] for s in services if s.get('Group') == 'Service']

print(f'User: {user.alias}')
print(f'Services: {[s["Name"] for s in services]}')

# Get action items summary
summary = c.get_action_items_summary(audience=service_ids)
items = summary.get('ActionItemSummaryList', [])

# Focus on Security domain
sec = [i for i in items if i.get('Domain', {}).get('DomainName') == 'Security']

# Sort by Out of SLA count (highest risk first)
sec.sort(key=lambda x: x.get('ActionItemData', {}).get('OutOfSLACount', 0), reverse=True)

print()
print('=' * 90)
print('SECURITY (SFI) ITEMS RANKED BY RISK (Out of SLA Count)')
print('=' * 90)

for item in sec:
    kpi = item.get('Kpi', {})
    data = item.get('ActionItemData', {})
    out = data.get('OutOfSLACount', 0)
    app = data.get('ApproachingSLACount', 0)
    ins = data.get('InSLACount', 0)
    
    risk = 'CRITICAL' if out > 3 else 'HIGH' if out > 0 else 'MEDIUM' if app > 0 else 'LOW'
    
    print(f'{risk:8} | Out:{out:3} App:{app:3} In:{ins:3} | {kpi.get("KpiName", "Unknown")}')

tot_out = sum(i.get('ActionItemData', {}).get('OutOfSLACount', 0) for i in sec)
tot_app = sum(i.get('ActionItemData', {}).get('ApproachingSLACount', 0) for i in sec)
tot_in = sum(i.get('ActionItemData', {}).get('InSLACount', 0) for i in sec)

print('=' * 90)
print(f'TOTALS: Out of SLA: {tot_out} | Approaching: {tot_app} | In SLA: {tot_in}')
print(f'TOTAL SECURITY ITEMS: {tot_out + tot_app + tot_in}')
print()
print('BIGGEST ISSUE BY COUNT:')
biggest = sec[0] if sec else None
if biggest:
    kpi = biggest.get('Kpi', {})
    data = biggest.get('ActionItemData', {})
    print(f'  {kpi.get("KpiName")}')
    print(f'  Out of SLA: {data.get("OutOfSLACount", 0)}')
    print(f'  KPI ID: {kpi.get("KpiId")}')
