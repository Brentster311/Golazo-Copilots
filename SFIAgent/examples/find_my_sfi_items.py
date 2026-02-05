#!/usr/bin/env python
"""
Find SFI (Secure Future Initiative) action items assigned to a user.
"""

from s360_client import S360Client
import json


def find_my_sfi_items(user_alias: str = "brentj") -> None:
    """Find all SFI action items assigned to the specified user."""
    
    client = S360Client()
    
    # Get current user info
    user = client.get_current_user()
    print(f"Logged in as: {user.display_name} ({user.alias})")
    print("=" * 70)
    
    # Get the user's default landing view to find their services
    print(f"\n📋 Getting services for {user_alias}...")
    landing_view = client.get_default_landing_view(user_alias)
    
    services = landing_view.get("SearchDataList", [])
    service_ids = [s["Id"] for s in services if s.get("Group") == "Service"]
    
    print(f"Found {len(service_ids)} services associated with {user_alias}")
    for svc in services[:5]:
        print(f"  - {svc['Name']} ({svc['Id'][:8]}...)")
    if len(services) > 5:
        print(f"  ... and {len(services) - 5} more")
    
    # Get action items summary using service IDs
    print(f"\n📊 Getting action items summary for your services...")
    summary = client.get_action_items_summary(audience=service_ids)
    
    # Parse the summary
    programs = summary.get("ProgramsLookup", {})
    action_item_list = summary.get("ActionItemSummaryList", [])
    
    print(f"\nPrograms: {len(programs)}")
    for prog_id, prog in programs.items():
        print(f"  - {prog.get('ProgramDisplayName', prog_id)}")
        waves = prog.get("WavesLookup", {})
        for wave_id, wave in list(waves.items())[:3]:
            print(f"      Wave: {wave.get('DisplayName')} ({wave.get('WaveStartDate', '')[:10]} - {wave.get('WaveEndDate', '')[:10]})")
    
    # Group by domain
    items_by_domain: dict[str, list] = {}
    for item in action_item_list:
        domain = item.get("Domain", {}).get("DomainName", "Unknown")
        if domain not in items_by_domain:
            items_by_domain[domain] = []
        items_by_domain[domain].append(item)
    
    # Summary statistics
    print("\n" + "=" * 70)
    print("📈 ACTION ITEMS SUMMARY BY DOMAIN")
    print("=" * 70)
    
    total_out_of_sla = 0
    total_approaching = 0
    total_in_sla = 0
    
    for domain, items in sorted(items_by_domain.items()):
        domain_out = sum(i.get("ActionItemData", {}).get("OutOfSLACount", 0) for i in items)
        domain_approaching = sum(i.get("ActionItemData", {}).get("ApproachingSLACount", 0) for i in items)
        domain_in = sum(i.get("ActionItemData", {}).get("InSLACount", 0) for i in items)
        
        total_out_of_sla += domain_out
        total_approaching += domain_approaching
        total_in_sla += domain_in
        
        print(f"\n🔹 {domain}: {len(items)} KPIs")
        print(f"   ❌ Out of SLA: {domain_out}")
        print(f"   ⚠️  Approaching SLA: {domain_approaching}")
        print(f"   ✅ In SLA: {domain_in}")
    
    print("\n" + "-" * 70)
    print(f"TOTAL: ❌ {total_out_of_sla} Out | ⚠️ {total_approaching} Approaching | ✅ {total_in_sla} In SLA")
    
    # Focus on Security domain (SFI)
    print("\n" + "=" * 70)
    print("🔒 SECURITY (SFI) ACTION ITEMS DETAIL")
    print("=" * 70)
    
    security_items = items_by_domain.get("Security", [])
    if security_items:
        # Sort by Out of SLA count (highest first)
        security_items.sort(
            key=lambda x: x.get("ActionItemData", {}).get("OutOfSLACount", 0),
            reverse=True
        )
        
        for item in security_items:
            kpi = item.get("Kpi", {})
            kpi_name = kpi.get("KpiName", "Unknown")
            kpi_id = kpi.get("KpiId", "")
            
            data = item.get("ActionItemData", {})
            out_of_sla = data.get("OutOfSLACount", 0)
            approaching = data.get("ApproachingSLACount", 0)
            in_sla = data.get("InSLACount", 0)
            current_value = data.get("CurrentValue", 0)
            
            forums = item.get("Forums", [])
            is_launch_criteria = item.get("IsLaunchCriteria", False)
            
            # Determine status icon
            if out_of_sla > 0:
                status = "❌ OUT OF SLA"
            elif approaching > 0:
                status = "⚠️  APPROACHING"
            else:
                status = "✅ IN SLA"
            
            print(f"\n{status}")
            print(f"   KPI: {kpi_name}")
            print(f"   KPI ID: {kpi_id}")
            print(f"   Current Value: {current_value}")
            print(f"   Out of SLA: {out_of_sla} | Approaching: {approaching} | In SLA: {in_sla}")
            print(f"   Forums: {', '.join(forums) if forums else 'None'}")
            if is_launch_criteria:
                print(f"   ⭐ LAUNCH CRITERIA")
    else:
        print("No Security (SFI) items found!")
    
    # Get detailed ETA data for security items
    print("\n" + "=" * 70)
    print("📝 DETAILED ETA DATA FOR YOUR SERVICES")
    print("=" * 70)
    
    eta_data = client.get_eta_and_annotation_data(
        audience=service_ids,
        accessing_user_alias=user_alias,
    )
    
    eta_items = eta_data.get("ActionItems", [])
    if eta_items:
        # Group by SLA type
        out_of_sla_items = [i for i in eta_items if i.get("SlaType") == "OutOfSla"]
        missing_eta_items = [i for i in eta_items if i.get("SlaType") == "MissingEta"]
        
        print(f"\nFound {len(eta_items)} total items:")
        print(f"  ❌ Out of SLA: {len(out_of_sla_items)}")
        print(f"  ⚠️  Missing ETA: {len(missing_eta_items)}")
        
        # Show out of SLA items
        if out_of_sla_items:
            print("\n--- OUT OF SLA ITEMS ---")
            for item in out_of_sla_items[:10]:
                print(f"\n  KPI: {item.get('KpiDisplayName', 'Unknown')}")
                print(f"  Service: {item.get('ServiceName', 'Unknown')}")
                print(f"  ETA: {item.get('Eta', 'No ETA')}")
                print(f"  Annotation: {item.get('Annotation', 'None')[:100] if item.get('Annotation') else 'None'}")
    else:
        print("No detailed ETA data available.")
    
    # Save full data to JSON
    output = {
        "user": user_alias,
        "services": [{"id": s["Id"], "name": s["Name"]} for s in services],
        "programs": list(programs.keys()),
        "summary_by_domain": {k: len(v) for k, v in items_by_domain.items()},
        "totals": {
            "out_of_sla": total_out_of_sla,
            "approaching_sla": total_approaching,
            "in_sla": total_in_sla,
        },
        "security_items": security_items,
        "eta_items": eta_items if 'eta_items' in dir() else [],
    }
    
    with open("my_sfi_items.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n💾 Full data saved to my_sfi_items.json")


if __name__ == "__main__":
    import sys
    user = sys.argv[1] if len(sys.argv) > 1 else "brentj"
    find_my_sfi_items(user)
