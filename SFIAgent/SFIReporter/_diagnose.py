"""Diagnose why Rohit Pandey maps to Unknown Owner for muralic."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from sfi_reporter.data import get_client

client = get_client()

# 1. Search for "Rohit Pandey" to see what S360 returns
print("=" * 60)
print("STEP 1: S360 search for 'Rohit Pandey'")
print("=" * 60)
results = client.search("Rohit Pandey")
org_results = [r for r in results if r.get("Group") == "Org"]
print(f"Total results: {len(results)}, Org results: {len(org_results)}")
for r in org_results:
    print(f"  Id={r.get('Id')!r}, Name={r.get('Name')!r}, Owners={r.get('Owners')!r}")

# 2. For each candidate alias, call get_manager_chain
print()
print("=" * 60)
print("STEP 2: Manager chains for each candidate alias")
print("=" * 60)
for r in org_results:
    alias = r.get("Id", "")
    if alias:
        print(f"\n  Chain for alias={alias!r}:")
        try:
            chain = client.get_manager_chain(alias)
            for i, person in enumerate(chain):
                print(f"    [{i}] alias={person.alias!r}, name={person.display_name!r}")
            # Check if muralic is in chain
            chain_aliases = [p.alias.lower() for p in chain]
            if "muralic" in chain_aliases:
                idx = chain_aliases.index("muralic")
                print(f"    >>> muralic found at index {idx} — THIS IS IN MURALIC's ORG")
            else:
                print(f"    >>> muralic NOT in chain — NOT in muralic's org")
        except Exception as e:
            print(f"    ERROR: {e}")

# 3. Call get_service_owners to see owner_aliases
print()
print("=" * 60)
print("STEP 3: get_service_owners for muralic's services")
print("=" * 60)
from sfi_reporter.models import OrgAncestry
from sfi_reporter.services import do_refresh, get_service_owners, get_org_mapping

# First get muralic's services
landing = client.get_landing_view("muralic")
services = [s.get("Name", s.get("ServiceName", "")) for s in landing.get("Services", [])]
print(f"Services ({len(services)}): {services}")

service_owners, owner_aliases = get_service_owners(services, on_status=lambda m: print(f"  {m}"))
print(f"\nowner_aliases:")
for name, val in owner_aliases.items():
    print(f"  {name!r}: {val!r}")

# 4. Check Rohit Pandey specifically
print()
print("=" * 60)
print("STEP 4: Rohit Pandey in owner_aliases")
print("=" * 60)
for key in owner_aliases:
    if "rohit" in key.lower() or "pandey" in key.lower():
        print(f"  Found key={key!r}, value={owner_aliases[key]!r}, type={type(owner_aliases[key])}")

# 5. Call get_org_mapping
print()
print("=" * 60)
print("STEP 5: get_org_mapping for muralic")
print("=" * 60)
all_owners = list({o for owners in service_owners.values() for o in owners})
org_mapping = get_org_mapping(all_owners, "muralic", owner_aliases=owner_aliases, on_status=lambda m: print(f"  {m}"))
print(f"\norg_mapping:")
for name, anc in sorted(org_mapping.items()):
    print(f"  {name!r}: level1={anc.level1!r}, level2={anc.level2!r}")
