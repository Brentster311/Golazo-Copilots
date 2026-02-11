"""Debug: show people hierarchy for muralic."""
import sys, json
sys.path.insert(0, 'SFIReporter/src')
sys.path.insert(0, 'src')
from sfi_reporter.data import get_client

client = get_client()

# Get muralic's landing view
landing = client.get_default_landing_view('muralic')
search_list = landing.get('SearchDataList', [])

print('=== Landing View Items ===')
for item in search_list:
    print(json.dumps(item, indent=2))

print()
print('=== TeamGroups ===')
team_groups = [i for i in search_list if i.get('Group') == 'TeamGroup']
for tg in team_groups:
    tg_id = tg.get('Id')
    tg_name = tg.get('Name', '')
    print(f'TeamGroup: {tg_name} (Id={tg_id})')
    print()
    print(f'--- People Hierarchy for [{tg_id}] ---')
    hierarchy = client._extended.query_people_hierarchy([tg_id])
    print(json.dumps(hierarchy, indent=2))
    print()

# Also try alexhowells
print('\n\n========== ALEXHOWELLS ==========')
landing2 = client.get_default_landing_view('alexhowells')
search_list2 = landing2.get('SearchDataList', [])

print('=== Landing View Items ===')
for item in search_list2:
    print(json.dumps(item, indent=2))

print()
print('=== TeamGroups ===')
team_groups2 = [i for i in search_list2 if i.get('Group') == 'TeamGroup']
for tg in team_groups2:
    tg_id = tg.get('Id')
    tg_name = tg.get('Name', '')
    print(f'TeamGroup: {tg_name} (Id={tg_id})')
    print()
    print(f'--- People Hierarchy for [{tg_id}] ---')
    hierarchy = client._extended.query_people_hierarchy([tg_id])
    print(json.dumps(hierarchy, indent=2))
    print()
