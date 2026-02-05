"""Flet desktop app for SFI Reporter."""
import logging
import threading
from typing import Optional

import flet as ft

from sfi_reporter.cache import (
    read_cache,
    write_cache,
    is_cache_valid,
    get_cache_age_minutes,
    clear_cache,
)
from sfi_reporter.data import get_current_user_alias, fetch_full_data


def get_cache_age_color(age_minutes: Optional[int]) -> Optional[str]:
    """Get color for cache age indicator.
    
    Args:
        age_minutes: Cache age in minutes.
        
    Returns:
        Color string or None for default.
    """
    if age_minutes is None:
        return None
    if age_minutes > 30:
        return "orange"
    return "green"


def do_refresh(user_alias: str, on_status: Optional[callable] = None) -> Optional[dict]:
    """Fetch fresh data and write to cache with status updates.
    
    Args:
        user_alias: User alias to fetch data for.
        on_status: Optional callback for status updates.
        
    Returns:
        Fetched data or None on error.
    """
    try:
        from sfi_reporter.data import get_user_services, get_action_items_summary
        from datetime import datetime
        
        # Step 1: Fetch services (this includes auth + API call - slow)
        print(f"[1] Fetching services for {user_alias}...")
        if on_status:
            on_status(f"Fetching services for {user_alias}...")
        
        services = get_user_services(user_alias)
        service_ids = [s.get('Id') for s in services if s.get('Id')]
        print(f"[2] Got {len(services)} services")
        
        # Step 2: Fetch action items (another API call - slow)
        print(f"[3] Fetching action items for {len(services)} services...")
        if on_status:
            on_status(f"Fetching action items for {len(services)} services...")
        
        action_items = get_action_items_summary(service_ids) or {}
        print(f"[4] Got action items")
        
        # Step 3: Build result and cache
        print("[5] Saving to cache...")
        if on_status:
            on_status("Saving to cache...")
        
        data = {
            'services': services,
            'action_items': action_items,
            'timestamp': datetime.now().isoformat(),
        }
        
        write_cache(user_alias, data)
        print("[6] Done!")
        return data
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def do_clear_cache(user_alias: str) -> bool:
    """Clear cache for user.
    
    Args:
        user_alias: User alias.
        
    Returns:
        True if cleared, False otherwise.
    """
    return clear_cache(user_alias)


def main(page: ft.Page):
    """Main Flet app entry point."""
    page.title = "SFI Reporter"
    page.window.width = 900
    page.window.height = 600
    page.padding = 20
    
    # State
    current_data: dict = {}
    
    # Detect user alias
    detected_alias = get_current_user_alias() or ""
    
    # UI Components
    user_alias_field = ft.TextField(
        label="User Alias",
        value=detected_alias,
        hint_text="Your Microsoft alias (e.g., 'brentj')",
        width=300,
    )
    
    cache_age_text = ft.Text("", size=12)
    status_text = ft.Text("", size=14)
    progress_ring = ft.ProgressRing(visible=False, width=20, height=20)
    
    services_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("ID")),
        ],
        rows=[],
    )
    
    action_items_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Action Item")),
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Total Count"), numeric=True),
            ft.DataColumn(ft.Text("Out of SLA"), numeric=True),
        ],
        rows=[],
    )
    
    def update_tables(data: dict):
        """Update tables with data."""
        nonlocal current_data
        current_data = data
        
        # Update services table
        services = data.get('services', [])
        services_table.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(s.get('Name', 'Unknown'))),
                ft.DataCell(ft.Text(s.get('Id', 'N/A'))),
            ])
            for s in services[:50]  # Limit to 50 rows for performance
        ]
        
        # Update action items table
        action_items = data.get('action_items', {})
        summary_list = action_items.get('ActionItemSummaryList', [])
        print(f"[DEBUG] Total action items: {len(summary_list)}")
        action_items_table.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(item.get('Kpi', {}).get('KpiName', 'Unknown')[:50])),  # Truncate long names
                ft.DataCell(ft.Text(item.get('Kpi', {}).get('KpiId', 'N/A')[:8])),
                ft.DataCell(ft.Text(str(item.get('ActionItemData', {}).get('CurrentValue', 0)))),
                ft.DataCell(ft.Text(str(item.get('ActionItemData', {}).get('OutOfSLACount', 0)))),
            ])
            for item in summary_list[:50]  # Limit to 50 rows for performance
        ]
        
        # Update cache age
        age = get_cache_age_minutes(data)
        if age is not None:
            color = get_cache_age_color(age)
            cache_age_text.value = f"Cache: {age} minutes old"
            cache_age_text.color = color
        else:
            cache_age_text.value = ""
        
        page.update()
    
    def on_refresh_click(e):
        """Handle refresh button click."""
        alias = user_alias_field.value.strip()
        if not alias:
            status_text.value = "Please enter a user alias"
            status_text.color = "red"
            page.update()
            return
        
        # Show loading
        progress_ring.visible = True
        status_text.value = "Starting..."
        status_text.color = None
        page.update()
        
        def update_status(message: str):
            """Update status text from background thread."""
            status_text.value = message
            try:
                page.update()
            except Exception:
                pass  # Ignore update errors during shutdown
        
        def fetch_in_background():
            try:
                data = do_refresh(alias, on_status=update_status)
            except Exception:
                data = None
            
            if data:
                # Update status before slow table rendering
                print("[7] Updating display...")
                status_text.value = "Updating display..."
                try:
                    page.update()
                except Exception:
                    pass
                
                print("[8] Building table rows...")
                update_tables(data)
                
                print("[9] Final page update...")
                progress_ring.visible = False
                status_text.value = "✅ Data refreshed!"
                status_text.color = "green"
            else:
                progress_ring.visible = False
                status_text.value = "❌ Error fetching data"
                status_text.color = "red"
            
            print("[10] Done with UI update")
            try:
                page.update()
            except Exception:
                pass
        
        threading.Thread(target=fetch_in_background, daemon=True).start()
    
    def on_clear_cache_click(e):
        """Handle clear cache button click."""
        alias = user_alias_field.value.strip()
        if alias and do_clear_cache(alias):
            services_table.rows = []
            action_items_table.rows = []
            cache_age_text.value = ""
            status_text.value = "Cache cleared"
            status_text.color = "blue"
            page.update()
    
    refresh_button = ft.Button(
        "🔄 Refresh Data",
        on_click=on_refresh_click,
    )
    
    clear_cache_button = ft.OutlinedButton(
        "🗑️ Clear Cache",
        on_click=on_clear_cache_click,
    )
    
    # Load cached data on startup
    if detected_alias:
        cached = read_cache(detected_alias)
        if cached and is_cache_valid(cached):
            update_tables(cached)
    
    # Layout
    page.add(
        ft.Column([
            ft.Text("📊 SFI Reporter", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("View SFI/QEI action items for your services", size=14, color="grey"),
            ft.Divider(),
            ft.Row([
                user_alias_field,
                refresh_button,
                progress_ring,
            ], alignment=ft.MainAxisAlignment.START),
            ft.Row([
                cache_age_text,
                status_text,
            ]),
            ft.Divider(),
            ft.Text("🔧 Services", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=services_table,
                border=ft.Border.all(1, "grey"),
                border_radius=5,
                padding=10,
            ),
            ft.Divider(),
            ft.Text("📋 Action Items", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=action_items_table,
                border=ft.Border.all(1, "grey"),
                border_radius=5,
                padding=10,
            ),
            ft.Divider(),
            clear_cache_button,
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    )


if __name__ == "__main__":
    # Suppress asyncio cleanup errors on Windows when closing the app
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)
    ft.run(main)
