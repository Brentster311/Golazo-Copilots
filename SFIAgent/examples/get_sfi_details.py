#!/usr/bin/env python
"""
Get detailed information about a specific SFI action item to help close it.
"""

from s360_client import S360Client
import json
import re
from html import unescape


def strip_html(text: str) -> str:
    """Remove HTML tags and clean up text."""
    if not text:
        return ""
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    # Unescape HTML entities
    clean = unescape(clean)
    # Clean up whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def get_action_item_details(kpi_id: str, service_id: str | None = None) -> None:
    """Get detailed information about a specific action item."""
    
    client = S360Client()
    user = client.get_current_user()
    
    print("=" * 80)
    print(f"SFI ACTION ITEM DETAILS")
    print(f"User: {user.display_name} ({user.alias})")
    print("=" * 80)
    
    # Get user's services if not specified
    if not service_id:
        lv = client.get_default_landing_view(user.alias)
        services = lv.get("SearchDataList", [])
        service_ids = [s["Id"] for s in services if s.get("Group") == "Service"]
    else:
        service_ids = [service_id]
    
    # Get KPI metadata
    print("\n📋 GETTING KPI METADATA...")
    metadata = client.get_all_action_item_metadata()
    items = metadata.get("ActionItemMetadataList", [])
    kpi_meta = next((i for i in items if i.get("ActionItemId") == kpi_id), None)
    
    if kpi_meta:
        print(f"\n🎯 KPI: {kpi_meta.get('ActionItemDisplayName')}")
        print(f"   Domain: {kpi_meta.get('DomainName')}")
        print(f"   State: {kpi_meta.get('State')}")
        print(f"   Data Latency: {kpi_meta.get('DataLatency')} hours")
        print(f"   Approaching SLA Days: {kpi_meta.get('ApproachingSlaDaysLimit')}")
        
        # Parse and display description
        desc = strip_html(kpi_meta.get("Description", ""))
        print(f"\n📖 DESCRIPTION:")
        print("-" * 80)
        # Split into sections
        sections = desc.split("Required Action")
        if len(sections) > 1:
            print("Overview:")
            print(sections[0][:1000])
            print("\n🔧 REQUIRED ACTION:")
            print(sections[1][:1500])
        else:
            print(desc[:2000])
        
        # Parse FAQs
        faqs = kpi_meta.get("FAQs", "[]")
        if faqs:
            try:
                faq_list = json.loads(faqs)
                print(f"\n❓ FAQs ({len(faq_list)} items):")
                print("-" * 80)
                for faq in faq_list:
                    print(f"Q: {faq.get('Question')}")
                    print(f"A: {faq.get('Answer')}")
                    print()
            except json.JSONDecodeError:
                pass
        
        # Parse KPI owners
        owners = kpi_meta.get("KpiOwner", "[]")
        if owners:
            try:
                owner_list = json.loads(owners)
                print(f"\n👥 KPI OWNERS (Contact for help):")
                for owner in owner_list:
                    email = owner.get("Email", "")
                    name = owner.get("Name", "")
                    print(f"   - {name} ({email})")
            except json.JSONDecodeError:
                pass
        
        print(f"\n📧 ICM: {kpi_meta.get('ICMTenantName')} / {kpi_meta.get('ICMTeamName')}")
    
    # Get the action items grid
    print("\n" + "=" * 80)
    print("📊 YOUR ACTION ITEMS FOR THIS KPI")
    print("=" * 80)
    
    grid = client.get_action_items_grid(
        kpi_id=kpi_id,
        audience=service_ids,
        sla_type_filter=0,  # All
    )
    
    rows = grid.get("Rows", [])
    print(f"\nFound {len(rows)} action item(s)")
    
    for i, row in enumerate(rows, 1):
        print(f"\n--- Item {i} ---")
        print(f"Service: {row.get('S360_ServiceTreeServiceName')}")
        print(f"Service ID: {row.get('S360_ServiceId')}")
        print(f"Action Item ID: {row.get('id')}")
        print(f"Assigned To: {row.get('S360_AssignedToName')} ({row.get('S360_AssignedTo')})")
        print(f"Action Owner: {row.get('ActionOwnerName')} ({row.get('ActionOwnerAlias')})")
        print(f"SLA Status: {row.get('SlaType')}")
        print(f"Classification: {row.get('classificationType')}")
        print(f"Cloud: {row.get('cloudType')}")
        print(f"Due Date: {row.get('dueDate')}")
        print(f"ETA: {row.get('EtaDate')}")
        print(f"Original Publish: {row.get('OriginalPublishTime')}")
        
        # Extract URL from title
        title = row.get("title", "")
        url_match = re.search(r'href=["\']([^"\']+)["\']', title)
        if url_match:
            url = url_match.group(1).replace("&amp;", "&")
            print(f"\n🔗 LENS REPORT URL:")
            print(f"   {url}")
        
        # Get ETA history
        action_item_id = row.get("id")
        if action_item_id:
            print(f"\n📅 ETA HISTORY:")
            history = client.get_eta_history(kpi_id, action_item_id)
            if history:
                for h in history[-5:]:  # Last 5
                    print(f"   {h.eta.strftime('%Y-%m-%d') if h.eta else 'N/A'} - {h.notes or 'No notes'}")
            else:
                print("   No ETA history")
    
    # Summary of next steps
    print("\n" + "=" * 80)
    print("✅ NEXT STEPS TO CLOSE THIS TICKET")
    print("=" * 80)
    
    if kpi_meta and "Watson" in kpi_meta.get("ActionItemDisplayName", ""):
        print("""
1. CLICK THE LENS REPORT LINK above to see which specific resources need Azure Watson

2. FOR WINDOWS VMs:
   - Go to: https://aka.ms/azwonboard
   - Follow the onboarding guide

3. FOR LINUX VMs:
   - Go to: https://eng.ms/docs/products/azure-watson/azurewatson/onboardinglinux
   
4. FOR AKS/CONTAINERS:
   - Go to: https://eng.ms/docs/products/azure-watson/azurewatson/watsononcontainerizedworkloads

5. PRE-REQUISITES:
   - AzSecPack must be installed and enabled
   - Update MA config to enable Azure Watson crash dump collection
   - Azure Security Pack scans for registry keys set by Azure Watson

6. AFTER ENABLING:
   - Allow 24 hours for data to refresh in LENS
   - The KPI will auto-close when compliance is detected

7. NEED HELP?
   - Email: supwatson@microsoft.com
   - Office Hours: Every alternate Tuesday 9 AM PST

8. TSG: https://eng.ms/docs/products/azure-watson/azurewatson/s360kpi
""")
    
    # Save full data
    output = {
        "kpi_id": kpi_id,
        "kpi_metadata": kpi_meta,
        "action_items": rows,
    }
    
    with open("sfi_action_item_details.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n💾 Full data saved to sfi_action_item_details.json")


if __name__ == "__main__":
    import sys
    
    # Azure Watson Not Enabled KPI ID
    WATSON_KPI_ID = "49a25abf-fe19-1f6c-20ed-5a0fcbdf6312"
    
    kpi_id = sys.argv[1] if len(sys.argv) > 1 else WATSON_KPI_ID
    get_action_item_details(kpi_id)
