"""Quick end-to-end diagnostic for Rohit Pandey resolution in do_refresh."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.stdout.reconfigure(encoding='utf-8')

from sfi_reporter.tk_app import do_refresh

print("Running do_refresh('muralic')...")
data = do_refresh("muralic", on_status=lambda m: print(f"  {m}"))

if data is None:
    print("ERROR: do_refresh returned None")
    sys.exit(1)

print(f"\nis_manager: {data.get('is_manager')}")

# Check org_mapping
om = data.get('org_mapping', {})
print(f"\norg_mapping ({len(om)} entries):")
for name, anc in sorted(om.items()):
    print(f"  {name!r}: level1={anc.level1!r}, level2={anc.level2!r}")

# Check for Rohit Pandey specifically
for key in om:
    if 'rohit' in key.lower() or 'pandey' in key.lower():
        print(f"\n>>> FOUND: {key!r} → {om[key]}")

# Check owner_aliases (stored in data?)
oa = data.get('owner_aliases', {})
print(f"\nowner_aliases ({len(oa)} entries):")
for name, val in sorted(oa.items()):
    print(f"  {name!r}: {val!r}")

# Check owner_stats
os_ = data.get('owner_stats', {})
print(f"\nowner_stats ({len(os_)} entries):")
for name, stats in sorted(os_.items()):
    print(f"  {name!r}: total={stats.get('count')}, sla={stats.get('sla')}, invalid_eta={stats.get('invalid_eta')}")
