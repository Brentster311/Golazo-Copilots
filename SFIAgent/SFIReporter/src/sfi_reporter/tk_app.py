"""Tkinter desktop app for SFI Reporter."""
import json
import logging
import re
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import NamedTuple, Optional
import webbrowser


class OrgAncestry(NamedTuple):
    """Mapping of a service owner to their hierarchical ancestors.
    
    level1: The viewer's direct report ancestor (or "Unknown Owner", or self-name)
    level2: The sub-report under level1, or None if the owner IS the level1 direct
    """
    level1: str
    level2: Optional[str]

from sfi_reporter.cache import (
    read_cache,
    write_cache,
    is_cache_valid,
    get_cache_age_minutes,
    clear_cache,
    get_cache_dir,
)
from sfi_reporter.data import get_current_user_alias
from sfi_reporter.llm_client import LLMConfig, LLMConfigError, LLMError, analyze_item, fetch_action_item_urls, AnalysisResult
from sfi_reporter.llm_storage import save_analysis, load_analysis, analysis_exists
from sfi_reporter.logging_config import setup_logging, get_log_path, patch_subprocess_windows

logger = logging.getLogger(__name__)

SETTINGS_FILENAME = 'settings.json'

def _load_setting(key: str, default=None):
    """Load a single setting from the shared settings.json in the cache dir."""
    path = get_cache_dir() / SETTINGS_FILENAME
    if not path.exists():
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f).get(key, default)
    except (json.JSONDecodeError, IOError):
        return default

def _save_setting(key: str, value) -> None:
    """Persist a single setting to the shared settings.json in the cache dir."""
    path = get_cache_dir() / SETTINGS_FILENAME
    data = {}
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    data[key] = value
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        logger.error('Error saving setting %s: %s', key, e)


# Regex patterns for URL extraction
# Allow single quotes in URLs (common in query params) but not at the very end
# Also allow parentheses which are common in S360 lens URLs
URL_PATTERN = re.compile(r'https?://[^\s<>"]+(?<![\'"])')
HTML_ANCHOR_PATTERN = re.compile(r'<a[^>]+href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>', re.IGNORECASE)


# Column toggle constants
REQUIRED_COLUMNS = ['title', 'dueDate', 'SlaType']

COLUMN_DISPLAY_NAMES = {
    'title': 'Title',
    'dueDate': 'Due Date',
    'SlaType': 'SLA Type',
    'ActionOwnerName': 'Action Owner',
    'ActionOwnerAlias': 'Action Owner Alias',
    'EtaDate': 'ETA Date',
    'EtaStatus': 'ETA Status',
    'S360_ServiceTreeServiceName': 'Service Name',
    'S360_AssignedToName': 'Assigned To',
    'serviceTreeId': 'Service Tree ID',
    'S360_ProgramIds': 'Program IDs',
    'url': 'URL',
    'id': 'Action Item ID',
    '_kpi_id': 'KPI ID',
    'createdDate': 'Created Date',
    'closedDate': 'Closed Date',
    'Details': 'Details',
    'Remediation': 'Remediation',
    'SubscriptionId': 'Subscription ID',
    'SubscriptionName': 'Subscription Name',
    'TenantName': 'Tenant Name',
}

# SLA status value mapping (used in treeview display)
SLA_STATUS_MAP = {0: "In SLA", 1: "Approaching", 2: "Out of SLA"}

# Extended SLA map: handles int keys, string-numeric keys, and API string variants
_SLA_DISPLAY_MAP = {
    0: "In SLA", 1: "Approaching", 2: "Out of SLA",
    "0": "In SLA", "1": "Approaching", "2": "Out of SLA",
    "InSla": "In SLA", "Approaching": "Approaching", "OutOfSla": "Out of SLA",
}


def _resolve_sla_display(sla_type) -> str:
    """Map any SlaType value (int, str, None) to a human-readable label."""
    if sla_type is None:
        return ""
    return _SLA_DISPLAY_MAP.get(sla_type, "")


def _resolve_eta_status(eta_status) -> str:
    """Return ETA Status string, defaulting to '' for None."""
    return eta_status if eta_status else ""


# Map API column names to tree column identifiers
COLUMN_ID_MAP = {
    'title': 'title',
    'serviceTreeId': 'service',
    'SlaType': 'sla',
    'dueDate': 'due_date',
    'DueDate': 'due_date',
    'EtaDate': 'eta_date',
    'S360_AssignedTo': 'assigned_to',
    'assignedTo': 'assigned_to',
    'ActionOwnerName': 'action_owner',
    'ActionOwnerAlias': 'action_owner',
}

# Column widths for treeview
COLUMN_WIDTHS = {
    'title': 250, 'service': 150, 'sla': 80, 'due_date': 90,
    'eta_date': 90, 'assigned_to': 90, 'action_owner': 120
}

# Column anchors for treeview
COLUMN_ANCHORS = {
    'title': tk.W, 'service': tk.W, 'sla': tk.CENTER,
    'due_date': tk.CENTER, 'eta_date': tk.CENTER,
    'assigned_to': tk.W, 'action_owner': tk.W
}


def get_available_columns(items: list[dict]) -> list[str]:
    """Get union of all column keys from items.
    
    Args:
        items: List of item dictionaries.
        
    Returns:
        Sorted list of unique column names, with required columns first.
    """
    if not items:
        return list(REQUIRED_COLUMNS)
    
    all_keys = set()
    for item in items:
        all_keys.update(item.keys())
    
    # Sort with required columns first, then alphabetically
    required = [k for k in REQUIRED_COLUMNS if k in all_keys]
    others = sorted([k for k in all_keys if k not in REQUIRED_COLUMNS])
    return required + others


def filter_item_columns(item: dict, visible: list[str]) -> dict:
    """Filter item to only visible columns.
    
    Args:
        item: Item dictionary with all columns.
        visible: List of visible column names.
        
    Returns:
        New dictionary with only visible columns.
    """
    return {k: v for k, v in item.items() if k in visible}


def select_all_columns(available: list[str]) -> list[str]:
    """Return all available columns.
    
    Args:
        available: List of available column names.
        
    Returns:
        Copy of available list.
    """
    return list(available)


def clear_all_columns(available: list[str]) -> list[str]:
    """Return only required columns.
    
    Args:
        available: List of available column names.
        
    Returns:
        List containing only required columns that are in available.
    """
    return [c for c in REQUIRED_COLUMNS if c in available]


def validate_visible_columns(visible: list[str]) -> list[str]:
    """Ensure required columns are always present.
    
    Args:
        visible: List of visible column names.
        
    Returns:
        List with required columns guaranteed to be present.
    """
    result = list(visible)
    for col in REQUIRED_COLUMNS:
        if col not in result:
            result.append(col)
    return result


def get_empty_columns(item: dict) -> set[str]:
    """Identify columns that have empty values for a specific item.
    
    Empty values include: None, empty string, whitespace-only string,
    empty list, or the string "None".
    
    Note: 0 (zero) and False are NOT considered empty as they are valid data.
    
    Args:
        item: Dictionary of column name to value.
        
    Returns:
        Set of column names that have empty values.
    """
    empty = set()
    for col, value in item.items():
        if value is None:
            empty.add(col)
        elif isinstance(value, str):
            if value.strip() == '' or value == 'None':
                empty.add(col)
        elif isinstance(value, list) and len(value) == 0:
            empty.add(col)
    return empty


def is_manager_view(landing_view: list) -> bool:
    """Detect if the user is a manager based on their landing view.
    
    Managers have a TeamGroup in their landing view, while ICs have
    individual Service entries.
    
    Args:
        landing_view: List of SearchDataList items from get_default_landing_view()
        
    Returns:
        True if user is a manager (has TeamGroup), False otherwise.
    """
    if not landing_view:
        return False
    return any(item.get('Group') == 'TeamGroup' for item in landing_view)


def parse_owners_field(owners_json: str | None) -> list[str]:
    """Parse the Owners field from S360 search results.
    
    The Owners field is a JSON-encoded string like '["John Doe","Jane Smith"]'.
    
    Args:
        owners_json: JSON string of owner names, or None
        
    Returns:
        List of owner names, empty list on parse failure.
    """
    if not owners_json or owners_json == 'null':
        return []
    
    try:
        parsed = json.loads(owners_json)
        if isinstance(parsed, list):
            return parsed
        return []
    except (json.JSONDecodeError, TypeError):
        return []


def get_org_mapping(owner_names: list[str], manager_alias: str, on_status: Optional[callable] = None) -> dict[str, OrgAncestry]:
    """Get mapping from each owner to their hierarchical ancestors (up to 2 levels).
    
    For each owner, queries S360 to get their manager chain and finds:
    - If owner IS the manager → OrgAncestry(self, None)
    - If owner reports directly to manager_alias → OrgAncestry(self, None)
    - If owner is 1 hop below a direct → OrgAncestry(direct_name, owner_name)
    - If owner is 2+ hops below a direct → OrgAncestry(direct_name, sub_report_name)
    - If owner is not in manager's org → OrgAncestry("Unknown Owner", None)
    
    Args:
        owner_names: List of unique owner names to look up
        manager_alias: The manager's alias (e.g., "alexhowells")
        on_status: Optional callback for status updates
        
    Returns:
        Dict mapping owner_name → OrgAncestry(level1, level2)
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from sfi_reporter.data import get_client
    import threading
    
    if not owner_names:
        return {}
    
    org_mapping: dict[str, OrgAncestry] = {}
    lock = threading.Lock()
    completed = [0]
    total = len(owner_names)
    
    def _resolve_display_name(client, alias: str) -> str:
        """Look up a person's display name by alias."""
        try:
            results = client.search(alias)
            for r in results:
                if r.get('Group') == 'Org' and r.get('Id', '').lower() == alias.lower():
                    return r.get('Owners', alias)
        except Exception:
            pass
        return alias
    
    def lookup_owner(owner_name: str) -> tuple[str, OrgAncestry]:
        """Look up an owner and find their hierarchical ancestors.
        
        Algorithm:
        1. Search S360 for the owner name to get their alias and Managers chain
        2. For each exact name match, check if manager_alias is in their chain
        3. Use the FIRST match that has manager_alias in their chain
        4. Determine hierarchy depth and return OrgAncestry tuple
        """
        try:
            client = get_client()
            results = client.search(owner_name)
            
            for r in results:
                if r.get('Group') != 'Org':
                    continue
                
                result_owners = r.get('Owners', '')
                if result_owners.lower() != owner_name.lower():
                    continue
                
                # Check if this owner IS the manager (their chain won't include themselves)
                result_alias = r.get('Id', '')
                if result_alias.lower() == manager_alias.lower():
                    return owner_name, OrgAncestry(level1=owner_name, level2=None)
                
                # Get this person's Managers chain
                managers_json = r.get('Managers', '[]')
                try:
                    managers = json.loads(managers_json) if isinstance(managers_json, str) else managers_json
                except (json.JSONDecodeError, TypeError):
                    managers = []
                
                if not managers:
                    continue
                
                # KEY CHECK: Is manager_alias in their chain?
                managers_lower = [m.lower() for m in managers]
                if manager_alias.lower() not in managers_lower:
                    continue
                
                manager_idx = managers_lower.index(manager_alias.lower())
                remaining = len(managers) - 1 - manager_idx  # entries after manager_alias
                
                # Chain: [CEO, ..., manager_alias, level1_alias, level2_alias, ..., immediate_mgr]
                
                if remaining == 0:
                    # This person reports directly to the viewer
                    return owner_name, OrgAncestry(level1=owner_name, level2=None)
                
                # Level 1: the viewer's direct report
                level1_alias = managers[manager_idx + 1]
                level1_name = _resolve_display_name(client, level1_alias)
                
                if remaining == 1:
                    # This person reports to a direct → they ARE the level2
                    return owner_name, OrgAncestry(level1=level1_name, level2=owner_name)
                
                # remaining >= 2: two or more levels deep → cap at level2
                level2_alias = managers[manager_idx + 2]
                level2_name = _resolve_display_name(client, level2_alias)
                return owner_name, OrgAncestry(level1=level1_name, level2=level2_name)
            
            return owner_name, OrgAncestry(level1='Unknown Owner', level2=None)
            
        except Exception:
            return owner_name, OrgAncestry(level1='Unknown Owner', level2=None)
    
    if on_status:
        on_status(f"Looking up {total} service owners...")
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(lookup_owner, name): name for name in owner_names}
        
        for future in as_completed(futures):
            owner_name, ancestry = future.result()
            with lock:
                org_mapping[owner_name] = ancestry
                completed[0] += 1
                if on_status and completed[0] % 5 == 0:
                    on_status(f"Looking up owners: {completed[0]}/{total}")
    
    return org_mapping


def extract_direct_reports(service_owners: dict[str, list[str]], manager_name: Optional[str] = None) -> set[str]:
    """Extract direct report names from service_owners dict.
    
    Direct reports are identified ONLY by team entries like "Gowri Bhaskara's Team".
    This is the definitive source - no heuristics or inference.
    
    Args:
        service_owners: Dict mapping service_name to list of owner names
        manager_name: Optional manager's name to include
        
    Returns:
        Set of direct report names
    """
    directs = set()
    
    # Extract from "X's Team" patterns - these are the ONLY directs
    for service_name in service_owners.keys():
        if "'s Team" in service_name:
            name = service_name.replace("'s Team", "")
            directs.add(name)
    
    # Add manager if provided
    if manager_name:
        directs.add(manager_name)
    
    return directs


def aggregate_by_owner(items: list[dict], service_owners: dict[str, list[str]], 
                       org_mapping: Optional[dict] = None,
                       allowed_owners: Optional[set[str]] = None) -> dict:
    """Aggregate action item stats by service owner (level-1 rollup).
    
    When org_mapping is provided, each owner is mapped to their level-1 ancestor.
    Supports both legacy string mappings and OrgAncestry tuple mappings.
    
    When allowed_owners is specified without org_mapping, uses the old behavior:
    - The first owner in the list that's in allowed_owners
    - Or "Unknown Owner" if no allowed owner matches
    
    Args:
        items: List of detailed action items
        service_owners: Dict mapping service_id to list of owner names
        org_mapping: Optional dict mapping owner_name -> OrgAncestry or string
        allowed_owners: Optional set of owner names to include (legacy, for manager view)
        
    Returns:
        Dict mapping owner name to stats: {owner: {count, sla, invalid_eta}}
    """
    from sfi_reporter.data import is_invalid_eta
    
    def _get_level1(mapped) -> str:
        """Extract level1 from either OrgAncestry or legacy string mapping."""
        if isinstance(mapped, OrgAncestry):
            return mapped.level1
        return mapped  # Legacy string
    
    owner_stats: dict[str, dict] = {}
    
    for item in items:
        service_name = item.get('S360_ServiceTreeServiceName', '')
        owners = service_owners.get(service_name, None)
        
        # Handle missing or empty owners
        if owners is None:
            owners = ['Unknown Owner']
        elif len(owners) == 0:
            owners = ['No Owner']
        
        # Determine the target owner for this item
        if org_mapping is not None:
            # Use org_mapping to find the level-1 owner
            target_owner = None
            for owner in owners:
                mapped = org_mapping.get(owner)
                if mapped:
                    level1 = _get_level1(mapped)
                    if level1 and level1 != 'Unknown Owner':
                        target_owner = level1
                        break
            
            if target_owner is None:
                target_owners = ['Unknown Owner']
            else:
                target_owners = [target_owner]
        elif allowed_owners is not None:
            # Legacy behavior: Find the first owner that's in allowed_owners
            matched_owner = None
            for owner in owners:
                if owner in allowed_owners:
                    matched_owner = owner
                    break
            
            # If no match, use "Unknown Owner"
            if matched_owner is None:
                target_owners = ['Unknown Owner']
            else:
                target_owners = [matched_owner]
        else:
            target_owners = owners
        
        # Calculate item stats
        is_out_of_sla = item.get('SlaType') == 'OutOfSla'
        has_invalid_eta = is_invalid_eta(item.get('EtaDate'))
        
        # Add to each owner (usually just one when filtering)
        for owner in target_owners:
            if owner not in owner_stats:
                owner_stats[owner] = {'count': 0, 'sla': 0, 'invalid_eta': 0}
            
            owner_stats[owner]['count'] += 1
            if is_out_of_sla:
                owner_stats[owner]['sla'] += 1
            if has_invalid_eta:
                owner_stats[owner]['invalid_eta'] += 1
    
    return owner_stats


def aggregate_by_level2(items: list[dict], service_owners: dict[str, list[str]],
                        org_mapping: dict[str, OrgAncestry]) -> dict[tuple[str, str], dict]:
    """Aggregate action item stats by (level1, level2) pairs.
    
    Only includes entries where level2 is not None (i.e., actual sub-reports).
    Items whose owners map to level2=None (direct reports) or Unknown Owner are excluded.
    
    Args:
        items: List of detailed action items
        service_owners: Dict mapping service_name to list of owner names
        org_mapping: Dict mapping owner_name → OrgAncestry
        
    Returns:
        Dict mapping (level1_name, level2_name) → {count, sla, invalid_eta}
    """
    from sfi_reporter.data import is_invalid_eta
    
    level2_stats: dict[tuple[str, str], dict] = {}
    
    for item in items:
        service_name = item.get('S360_ServiceTreeServiceName', '')
        owners = service_owners.get(service_name, None)
        
        if owners is None or len(owners) == 0:
            continue
        
        # Find the first owner with a valid level2 mapping
        target_key = None
        for owner in owners:
            mapped = org_mapping.get(owner)
            if isinstance(mapped, OrgAncestry) and mapped.level2 is not None and mapped.level1 != 'Unknown Owner':
                target_key = (mapped.level1, mapped.level2)
                break
        
        if target_key is None:
            continue
        
        is_out_of_sla = item.get('SlaType') == 'OutOfSla'
        has_invalid_eta = is_invalid_eta(item.get('EtaDate'))
        
        if target_key not in level2_stats:
            level2_stats[target_key] = {'count': 0, 'sla': 0, 'invalid_eta': 0}
        
        level2_stats[target_key]['count'] += 1
        if is_out_of_sla:
            level2_stats[target_key]['sla'] += 1
        if has_invalid_eta:
            level2_stats[target_key]['invalid_eta'] += 1
    
    return level2_stats


def collect_services_for_owner(owner_name: str, level: str,
                               service_owners: dict[str, list[str]],
                               org_mapping: dict) -> set[str]:
    """Collect all service names belonging to an owner's subtree.
    
    For level1 drill-down: collects all services where any owner maps to this
    level1 ancestor (includes all level2 sub-reports under them).
    
    For level2 drill-down: collects all services where any owner maps to this
    specific level2 sub-report.
    
    Args:
        owner_name: The owner name to drill into
        level: "level1" or "level2"
        service_owners: Dict mapping service_name → list of owner names
        org_mapping: Dict mapping owner_name → OrgAncestry or string
        
    Returns:
        Set of service names belonging to the owner's subtree
    """
    # Build set of raw owner names that belong to this subtree
    matching_owners: set[str] = set()
    
    for raw_owner, mapped in org_mapping.items():
        if isinstance(mapped, OrgAncestry):
            if level == "level1" and mapped.level1 == owner_name:
                matching_owners.add(raw_owner)
            elif level == "level2" and mapped.level2 == owner_name:
                matching_owners.add(raw_owner)
        else:
            # Legacy string mapping — treat as level1
            if level == "level1" and mapped == owner_name:
                matching_owners.add(raw_owner)
    
    # Also include the owner_name itself for direct ownership
    matching_owners.add(owner_name)
    
    # Collect services owned by any matching owner
    result: set[str] = set()
    for svc_name, owners in service_owners.items():
        if any(o in matching_owners for o in owners):
            result.add(svc_name)
    
    return result


def get_service_owners(service_names: list[str], on_status: Optional[callable] = None) -> dict[str, list[str]]:
    """Fetch owners for each service using S360 search API in parallel.
    
    Args:
        service_names: List of service names to look up
        on_status: Optional callback for status updates
        
    Returns:
        Dict mapping service_name to list of owner names
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from sfi_reporter.data import get_client
    
    if not service_names:
        return {}
    
    service_owners: dict[str, list[str]] = {}
    
    def fetch_owner(service_name: str) -> tuple[str, list[str]]:
        """Fetch owner for a single service."""
        try:
            client = get_client()
            results = client.search(service_name)
            # Find exact match for service
            for result in results:
                if result.get('Group') == 'Service' and result.get('Name') == service_name:
                    owners_json = result.get('Owners')
                    owners = parse_owners_field(owners_json)
                    
                    # Special case: if service is "X's Team" and has no owners, use "X"
                    if not owners and "'s Team" in service_name:
                        team_owner = service_name.replace("'s Team", "")
                        owners = [team_owner]
                    
                    return service_name, owners
            
            # Service not found - check if it's a team pattern
            if "'s Team" in service_name:
                team_owner = service_name.replace("'s Team", "")
                return service_name, [team_owner]
            return service_name, []
        except Exception:
            # Even on error, handle team pattern
            if "'s Team" in service_name:
                team_owner = service_name.replace("'s Team", "")
                return service_name, [team_owner]
            return service_name, []
    
    if on_status:
        on_status(f"Fetching owners for {len(service_names)} services...")
    
    # Use ThreadPoolExecutor for parallel fetching
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_owner, name): name for name in service_names}
        for future in as_completed(futures):
            name, owners = future.result()
            service_owners[name] = owners
    
    return service_owners


def do_refresh(user_alias: str, on_status: Optional[callable] = None) -> Optional[dict]:
    """Fetch fresh data and write to cache with status updates.
    
    All stats are computed from detailed action items for consistency.
    """
    try:
        from sfi_reporter.data import get_user_team_info, get_action_items_summary, get_detailed_action_items, is_invalid_eta, get_all_programs, get_client
        from datetime import datetime
        
        if on_status:
            on_status("Connecting to S360...")
        
        # Get landing view to detect if user is a manager
        client = get_client()
        landing_response = client.get_default_landing_view(user_alias)
        landing_view = landing_response.get('SearchDataList', []) if landing_response else []
        is_manager = is_manager_view(landing_view)
        
        # Get services and audience IDs (supports both service owners and team views)
        services, audience_ids = get_user_team_info(user_alias)
        
        if on_status:
            if services:
                on_status(f"Retrieved {len(services)} services. Fetching programs...")
            else:
                on_status("Found team data. Fetching programs...")
        
        if not audience_ids:
            if on_status:
                on_status("No services or team found for this user")
            return {
                'services': [],
                'detailed_items': [],
                'service_stats': {},
                'program_stats': {},
                'kpi_stats': {},
                'timestamp': datetime.now().isoformat(),
            }
        
        # Fetch ALL programs from v2/Programs API for accurate name lookup
        if on_status:
            on_status("Fetching programs metadata...")
        program_names = get_all_programs()
        
        # Get action items summary to find ALL KPIs
        if on_status:
            on_status("Fetching action items summary...")
        action_items = get_action_items_summary(audience_ids) or {}
        summary_list = action_items.get('ActionItemSummaryList', [])
        kpi_ids = [item.get('Kpi', {}).get('KpiId') for item in summary_list if item.get('Kpi', {}).get('KpiId')]
        
        # Also merge in any programs from the ProgramsLookup in action items
        # (in case some programs are specific to user's services)
        programs_lookup = action_items.get('ProgramsLookup', {})
        for pid, info in programs_lookup.items():
            if pid not in program_names:
                program_names[pid] = info.get('ProgramDisplayName', pid)
        
        # Build KPI name lookup from summary
        kpi_names = {}
        for item in summary_list:
            kpi = item.get('Kpi', {})
            kpi_id = kpi.get('KpiId')
            if kpi_id:
                kpi_names[kpi_id] = kpi.get('KpiName', 'Unknown')
        
        # Fetch ALL detailed action items (includes S360_ProgramIds per item)
        detailed_items, failed_kpis = get_detailed_action_items(audience_ids, kpi_ids, on_status, kpi_names)
        
        if failed_kpis and on_status:
            names = [f['kpi_name'] for f in failed_kpis]
            on_status(f"⚠️ {len(failed_kpis)} KPI(s) failed: {', '.join(names)}")
        
        if on_status:
            on_status(f"Processing {len(detailed_items)} action items...")
        
        # Build service/kpi/program stats from detailed items (now with S360_ProgramIds)
        service_stats = {}  # {service_id: {'name': str, 'count': int, 'sla': int, 'invalid_eta': int}}
        kpi_stats = {}      # {kpi_id: {'name': str, 'count': int, 'sla': int, 'invalid_eta': int}}
        program_stats = {}  # {program_name: {'count': int, 'sla': int, 'invalid_eta': int}}
        
        for row in detailed_items:
            # Extract fields
            svc_id = row.get('S360_ServiceId', 'Unknown')
            svc_name = row.get('S360_ServiceTreeServiceName', 'Unknown')
            kpi_id = row.get('_kpi_id', 'Unknown')
            sla_type = row.get('SlaType', '')
            eta_date = row.get('EtaDate')
            program_ids = row.get('S360_ProgramIds') or []
            
            is_out_of_sla = sla_type == 'OutOfSla'
            is_invalid = is_invalid_eta(eta_date)
            
            # Update service stats
            if svc_id not in service_stats:
                service_stats[svc_id] = {'name': svc_name, 'count': 0, 'sla': 0, 'invalid_eta': 0}
            service_stats[svc_id]['count'] += 1
            if is_out_of_sla:
                service_stats[svc_id]['sla'] += 1
            if is_invalid:
                service_stats[svc_id]['invalid_eta'] += 1
            
            # Update KPI stats
            if kpi_id not in kpi_stats:
                kpi_stats[kpi_id] = {'name': kpi_names.get(kpi_id, kpi_id), 'count': 0, 'sla': 0, 'invalid_eta': 0}
            kpi_stats[kpi_id]['count'] += 1
            if is_out_of_sla:
                kpi_stats[kpi_id]['sla'] += 1
            if is_invalid:
                kpi_stats[kpi_id]['invalid_eta'] += 1
            
            # Update program stats (from S360_ProgramIds per row)
            # Use only the first program to avoid double-counting
            if program_ids:
                pid = program_ids[0]  # Take first program only
                program_name = program_names.get(pid)
                if not program_name:
                    # GUID not in lookup - show as "Other Program" instead of raw GUID
                    program_name = 'Other Program'
                if program_name not in program_stats:
                    program_stats[program_name] = {'count': 0, 'sla': 0, 'invalid_eta': 0, 'id': pid}
                program_stats[program_name]['count'] += 1
                if is_out_of_sla:
                    program_stats[program_name]['sla'] += 1
                if is_invalid:
                    program_stats[program_name]['invalid_eta'] += 1
            else:
                # Items without program assignment go to "Unassigned"
                if 'Unassigned' not in program_stats:
                    program_stats['Unassigned'] = {'count': 0, 'sla': 0, 'invalid_eta': 0, 'id': 'unassigned'}
                program_stats['Unassigned']['count'] += 1
                if is_out_of_sla:
                    program_stats['Unassigned']['sla'] += 1
                if is_invalid:
                    program_stats['Unassigned']['invalid_eta'] += 1
        
        # If manager view, fetch service owners and aggregate stats by owner
        owner_stats = {}
        level2_stats = {}
        service_owners = {}
        org_mapping = {}  # Maps each owner to OrgAncestry(level1, level2)
        if is_manager and service_stats:
            # Get manager alias from TeamGroup name (e.g., "Azure Core Insights (MURALIC)" -> "muralic")
            manager_alias = None
            manager_name = None
            for item in landing_view:
                if item.get('Group') == 'TeamGroup':
                    # Extract alias from team name - usually in format "Team Name (ALIAS)"
                    team_name = item.get('Name', '')
                    if '(' in team_name and ')' in team_name:
                        manager_alias = team_name.split('(')[-1].replace(')', '').strip().lower()
                    # Also try to get display name from Owners field
                    owners_json = item.get('Owners')
                    if owners_json:
                        manager_names = parse_owners_field(owners_json)
                        if manager_names:
                            manager_name = manager_names[0]
                    break
            
            # Get unique service names
            service_names = [stats.get('name') for stats in service_stats.values() if stats.get('name')]
            unique_names = list(set(service_names))
            
            if unique_names:
                service_owners = get_service_owners(unique_names, on_status)
                
                # Get all unique owner names across all services
                all_owners = set()
                for owners in service_owners.values():
                    all_owners.update(owners)
                
                # Get org mapping: for each owner, find their direct-report-level ancestor
                if manager_alias and all_owners:
                    org_mapping = get_org_mapping(list(all_owners), manager_alias, on_status)
                
                # Aggregate using org_mapping to roll up to directs (level-1)
                # Note: service_owners is keyed by service NAME which matches S360_ServiceTreeServiceName
                owner_stats = aggregate_by_owner(detailed_items, service_owners, 
                                                 org_mapping=org_mapping if org_mapping else None)
                
                # Compute level-2 stats for 2-level hierarchy
                if org_mapping:
                    level2_stats = aggregate_by_level2(detailed_items, service_owners, org_mapping)
        
        if on_status:
            on_status("Saving to cache...")
        
        data = {
            'services': services,
            'detailed_items': detailed_items,
            'service_stats': service_stats,
            'program_stats': program_stats,
            'kpi_stats': kpi_stats,
            'owner_stats': owner_stats,
            'level2_stats': level2_stats,
            'is_manager': is_manager,
            'service_owners': service_owners,
            'org_mapping': org_mapping,  # Maps owner -> OrgAncestry(level1, level2)
            'programs_lookup': program_names,  # Save program name lookup for cache reload
            'failed_kpis': failed_kpis,  # KPIs that failed during fetch
            'audience_ids': audience_ids,  # Needed for retry
            'kpi_names': kpi_names,  # Needed for retry
            'timestamp': datetime.now().isoformat(),
        }
        
        write_cache(user_alias, data)
        return data
    except Exception as e:
        logger.exception("Error fetching data for user")
        if on_status:
            on_status(f"Error: {e}")
        return None


# Filter functions for drill-down modal
def filter_items_by_service(items: list, service_id: str) -> list:
    """Filter items by service ID (S360_ServiceId or serviceTreeId)."""
    return [item for item in items if item.get('S360_ServiceId') == service_id or item.get('serviceTreeId') == service_id]


def filter_items_by_program(items: list, program_id: str) -> list:
    """Filter items by program ID (checks if program is in S360_ProgramIds list)."""
    return [item for item in items if program_id in (item.get('S360_ProgramIds') or [])]


def filter_items_by_id(items: list, item_id: str) -> list:
    """Filter to get a single item by its ID."""
    return [item for item in items if item.get('id') == item_id]


# Helper functions for item details formatting
def format_field_label(field_name: str) -> str:
    """Convert field name to human-readable label.
    
    Examples:
        serviceTreeId -> Service Tree Id
        S360_AssignedTo -> S360 Assigned To
        _kpi_id -> Kpi Id
    """
    import re
    # Remove leading underscores
    name = field_name.lstrip('_')
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    # Insert spaces before capital letters (camelCase)
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    # Title case
    return name.title()


def format_field_value(value) -> str:
    """Format a field value for display.
    
    Handles: strings, lists, booleans, None, numbers.
    """
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if isinstance(value, list):
        if not value:
            return ''
        return ', '.join(str(v) for v in value)
    if isinstance(value, dict):
        if not value:
            return ''
        return json.dumps(value, indent=2)
    return str(value)


def extract_urls_from_text(text: str) -> list:
    """Extract URLs from text, handling both HTML anchors and plain URLs.

    Simple two-branch logic:
    1. If the text contains <a> tags, extract (href, display_text) from each.
    2. Otherwise, find raw http(s):// URLs and use them as both link and label.

    Returns list of (url, display_text, start_pos, end_pos) tuples.
    """
    if not text or not isinstance(text, str):
        return []

    # Branch 1: HTML anchors present
    anchors = list(HTML_ANCHOR_PATTERN.finditer(text))
    if anchors:
        return [
            (m.group(1), m.group(2) or m.group(1), m.start(), m.end())
            for m in anchors
        ]

    # Branch 2: plain URLs
    return [
        (m.group(0), m.group(0), m.start(), m.end())
        for m in URL_PATTERN.finditer(text)
    ]


def clean_html_from_title(title: str) -> str:
    """Remove HTML anchor tags from title, keeping only the display text.
    
    '<a href="...">GDPR Scan Compliance</a>' -> 'GDPR Scan Compliance'
    """
    if not title or not isinstance(title, str):
        return title or ''
    return HTML_ANCHOR_PATTERN.sub(r'\2', title)


def parse_resource_uris(value) -> list:
    """Parse ResourceURIs field which may be a JSON string or list.
    
    Returns list of URLs.
    """
    if not value:
        return []
    
    if isinstance(value, list):
        return value
    
    if isinstance(value, str):
        # May be JSON array string
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        # Might be a single URL
        if value.startswith('http'):
            return [value]
    
    return []


# Field grouping definitions - comprehensive list for S360 parity
FIELD_GROUPS = {
    'identity': ['title', 'id', '_kpi_id', 'url', 'EventId'],
    'status': ['SlaType', 'classificationType', 'ActionItemType', 'myExceptionStatus', 'EtaStatus'],
    'dates': ['dueDate', 'DueDate', 'EtaDate', 'OriginalPublishTime', 'S360_TwoWayEta'],
    'ownership': ['assignedTo', 'S360_AssignedTo', 'S360_AssignedToName', 'S360_AssignedToLogic', 
                  'ActionOwnerAlias', 'ActionOwnerName', 'IsActionOwnerActiveEmployee', 'Admins'],
    'service_program': ['serviceTreeId', 'S360_ServiceId', 'S360_ServiceTreeServiceName', 'myExceptionServiceTreeId',
                        'S360_ProgramIds', 'S360_WavesMetadata', 'S360_IsShadow', 'IsServiceInAGC',
                        'XDivSecurityTeamId'],
    'subscription': ['TenantName', 'SubscriptionId', 'SubscriptionName'],
    'resources': ['Details', 'ResourceURIs'],
}


def group_item_fields(item: dict) -> dict:
    """Group item fields into logical categories.
    
    Returns dict with keys: identity, status, dates, ownership, service_program, subscription, resources, other
    Each value is a list of (field_name, formatted_value) tuples.
    """
    groups = {
        'identity': [],
        'status': [],
        'dates': [],
        'ownership': [],
        'service_program': [],
        'subscription': [],
        'resources': [],
        'other': [],
    }
    
    # Track which fields we've placed
    placed_fields = set()
    
    # Place fields into their groups
    for group_name, field_list in FIELD_GROUPS.items():
        for field in field_list:
            if field in item:
                value = item[field]
                formatted = format_field_value(value)
                # Skip empty values
                if formatted:
                    groups[group_name].append((field, formatted))
                placed_fields.add(field)
    
    # Put remaining fields in 'other'
    for field, value in item.items():
        if field not in placed_fields:
            formatted = format_field_value(value)
            if formatted:
                groups['other'].append((field, formatted))
    
    return groups


class ColumnSelectorDialog(tk.Toplevel):
    """Modal dialog for selecting which columns to display in DetailModal."""
    
    # Class variable to store column visibility across modal instances (session only)
    _visible_columns: list[str] | None = None
    
    def __init__(self, parent, available_columns: list[str], on_apply: callable = None, 
                 empty_columns: set[str] = None):
        """Initialize the column selector dialog.
        
        Args:
            parent: Parent window
            available_columns: List of column names available for selection
            on_apply: Callback function to call when user applies changes
            empty_columns: Set of column names that have empty values (will show "(empty)" suffix)
        """
        super().__init__(parent)
        self.title("Select Columns")
        self.geometry("350x450")
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 350) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 450) // 2
        self.geometry(f"+{x}+{y}")
        
        self.available_columns = available_columns
        self.on_apply = on_apply
        self._empty_columns = empty_columns or set()
        self._checkboxes: dict[str, tk.BooleanVar] = {}
        
        # Initialize visible columns from class variable or default to all
        if ColumnSelectorDialog._visible_columns is None:
            ColumnSelectorDialog._visible_columns = list(available_columns)
        
        self._create_widgets()
        
        # Bind Escape to close
        self.bind('<Escape>', lambda e: self.destroy())
        self.focus_set()
    
    def _create_widgets(self):
        """Create the dialog content."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="Select columns to display:", 
                  font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Button frame for Select All / Clear All
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(btn_frame, text="Select All", 
                   command=self._select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Clear All", 
                   command=self._clear_all).pack(side=tk.LEFT)
        
        # Container for canvas + scrollbar
        list_container = ttk.Frame(main_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable frame for checkboxes
        self._canvas = tk.Canvas(list_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self._canvas.yview)
        scrollable_frame = ttk.Frame(self._canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )
        
        self._canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        self._canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar FIRST on right, then canvas fills the rest
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mousewheel to this canvas only when mouse is over it
        self._canvas.bind("<Enter>", lambda e: self._canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self._canvas.bind("<Leave>", lambda e: self._canvas.unbind_all("<MouseWheel>"))
        
        # Create checkboxes for each column
        for col in self.available_columns:
            var = tk.BooleanVar(value=col in ColumnSelectorDialog._visible_columns)
            self._checkboxes[col] = var
            
            # Get display name, add "(empty)" suffix if column is empty for this item
            display_name = COLUMN_DISPLAY_NAMES.get(col, col)
            if col in self._empty_columns:
                display_name = f"{display_name} (empty)"
            
            # Create checkbox - disable for required columns
            cb = ttk.Checkbutton(scrollable_frame, text=display_name, variable=var)
            cb.pack(anchor=tk.W, pady=2)
            
            if col in REQUIRED_COLUMNS:
                var.set(True)  # Always checked
                cb.configure(state='disabled')
        
        # Apply/Cancel buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(action_frame, text="Apply", 
                   command=self._apply).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(action_frame, text="Cancel", 
                   command=self.destroy).pack(side=tk.RIGHT)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        self._canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _select_all(self):
        """Select all columns."""
        for col, var in self._checkboxes.items():
            var.set(True)
    
    def _clear_all(self):
        """Clear all except required columns."""
        for col, var in self._checkboxes.items():
            if col in REQUIRED_COLUMNS:
                var.set(True)
            else:
                var.set(False)
    
    def _apply(self):
        """Apply the column selection and close."""
        # Update class variable with current selection
        ColumnSelectorDialog._visible_columns = [
            col for col, var in self._checkboxes.items() if var.get()
        ]
        # Ensure required columns are always included
        ColumnSelectorDialog._visible_columns = validate_visible_columns(
            ColumnSelectorDialog._visible_columns
        )
        
        # Call callback if provided
        if self.on_apply:
            self.on_apply()
        
        self.destroy()
    
    @classmethod
    def get_visible_columns(cls) -> list[str] | None:
        """Get the current visible columns selection."""
        return cls._visible_columns
    
    @classmethod
    def reset_visible_columns(cls):
        """Reset visible columns to None (show all)."""
        cls._visible_columns = None


class DetailModal(tk.Toplevel):
    """Modal dialog showing drill-down details for action items."""

    COLUMNS = ("title", "service", "sla", "due_date", "eta_date", "eta_status", "assigned_to", "action_owner")

    def __init__(self, parent, title: str, items: list, service_names: dict = None, on_eta_complete=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("1000x500")
        self.transient(parent)  # Associate with parent
        self.grab_set()  # Make modal
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 1000) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.geometry(f"+{x}+{y}")
        
        self.service_names = service_names or {}
        self._items = items  # keep reference for refresh
        self._item_map = {}  # Store item dict by treeview iid
        self._on_eta_complete = on_eta_complete
        self._create_widgets(items)
        
        # Bind Escape to close
        self.bind('<Escape>', lambda e: self.destroy())
        self.focus_set()
    
    def _create_widgets(self, items: list):
        """Create the modal content."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._main_frame = main_frame
        if not items:
            ttk.Label(main_frame, text="No items found.", font=("Segoe UI", 12)).pack(pady=20)
        else:
            self._build_tree(main_frame, items)
        
        # Button bar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)
        
        # ETA button (enabled only when items exist)
        self.eta_btn = ttk.Button(
            btn_frame, text="\U0001f4cb Update ETAs",
            command=self._on_detail_update_etas,
        )
        self.eta_btn.pack(side=tk.RIGHT, padx=(0, 5))
        if not items:
            self.eta_btn.configure(state="disabled")
        
        # Selected-items ETA button (updates dynamically with selection count)
        self.selected_eta_btn = ttk.Button(
            btn_frame, text="\U0001f4cb Update ETAs for selected",
            command=self._on_selected_eta_update,
            state="disabled",
        )
        self.selected_eta_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Item count
        self._count_label = ttk.Label(btn_frame, text=f"{len(items)} item(s)")
        self._count_label.pack(side=tk.LEFT)

    def _build_tree(self, parent_frame, items: list):
        """Create and populate the sortable treeview."""
        columns = self.COLUMNS
        self.tree = SortableTreeview(parent_frame, columns=columns, show="headings", height=15)
        tree = self.tree
        
        tree.heading("title", text="Title")
        tree.heading("service", text="Service")
        tree.heading("sla", text="SLA Status")
        tree.heading("due_date", text="Due Date")
        tree.heading("eta_date", text="ETA Date")
        tree.heading("eta_status", text="ETA Status")
        tree.heading("assigned_to", text="Assigned To")
        tree.heading("action_owner", text="Action Owner")
        
        tree.column("title", width=220, anchor=tk.W)
        tree.column("service", width=130, anchor=tk.W)
        tree.column("sla", width=80, anchor=tk.CENTER)
        tree.column("due_date", width=85, anchor=tk.CENTER)
        tree.column("eta_date", width=85, anchor=tk.CENTER)
        tree.column("eta_status", width=100, anchor=tk.W)
        tree.column("assigned_to", width=90, anchor=tk.W)
        tree.column("action_owner", width=110, anchor=tk.W)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=tree.yview)
        x_scroll = ttk.Scrollbar(parent_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Pack with scrollbar on right
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Populate and store item references
        self._item_map.clear()
        self._populate_rows(items)
        
        # Apply default sorting: by due date ascending
        self.tree.sort_by_columns([('due_date', False)])
        
        # Bind double-click to open item details
        tree.bind('<Double-1>', self._on_item_double_click)
        # Bind right-click for LLM analysis context menu
        tree.bind('<Button-3>', self._on_item_right_click)
        # Bind selection change to update selected-items ETA button
        tree.bind('<<TreeviewSelect>>', self._on_tree_select)
    
    def _on_tree_select(self, event=None):
        """Update selected-items ETA button when tree selection changes."""
        selection = self.tree.selection()
        count = len(selection)
        if count > 0:
            self.selected_eta_btn.configure(
                text=f"\U0001f4cb Update ETAs for {count} selected",
                state="normal",
            )
        else:
            self.selected_eta_btn.configure(
                text="\U0001f4cb Update ETAs for selected",
                state="disabled",
            )

    def _on_selected_eta_update(self):
        """Open ManualEtaReviewDialog for only the selected items."""
        selection = self.tree.selection()
        if not selection:
            return
        selected_items = [self._item_map[iid] for iid in selection if iid in self._item_map]
        if not selected_items:
            return
        ManualEtaReviewDialog(
            self, selected_items,
            on_complete=self._on_detail_eta_complete,
        )

    def _on_detail_update_etas(self):
        """Open ManualEtaReviewDialog for items shown in this drill-down."""
        items = self._items
        if not items:
            return
        ManualEtaReviewDialog(
            self, items,
            on_complete=self._on_detail_eta_complete,
        )

    def _on_detail_eta_complete(self, saved, skipped, failed):
        """Refresh the detail tree after ETA edits."""
        if not saved:
            return
        # Mutate in-memory items
        for item, eta_str, notes in saved:
            item['EtaDate'] = eta_str
            if notes:
                item['EtaStatus'] = notes
        # Refresh the tree view
        self._refresh_items()
        # Notify parent so home screen refreshes too
        if self._on_eta_complete:
            self._on_eta_complete(saved, skipped, failed)

    def _refresh_items(self):
        """Repopulate the tree with current item data."""
        if hasattr(self, 'tree'):
            for child in self.tree.get_children():
                self.tree.delete(child)
            self._item_map.clear()
            self._populate_rows(self._items)
            self.tree.sort_by_columns([('due_date', False)])

    def _populate_rows(self, items: list):
        """Insert rows into the tree for each item."""
        for item in items:
            svc_id = item.get('serviceTreeId', '')
            svc_name = self.service_names.get(svc_id, svc_id[:20] + '...' if len(svc_id) > 20 else svc_id)
            raw_title = item.get('title', '')
            clean_title = clean_html_from_title(raw_title)
            iid = self.tree.insert('', tk.END, values=(
                clean_title[:60],
                svc_name,
                _resolve_sla_display(item.get('SlaType')),
                (item.get('DueDate') or item.get('dueDate', ''))[:10],
                (item.get('EtaDate') or '')[:10],
                _resolve_eta_status(item.get('EtaStatus')),
                item.get('S360_AssignedTo') or item.get('assignedTo', ''),
                item.get('ActionOwnerName') or item.get('ActionOwnerAlias', ''),
            ))
            self._item_map[iid] = item

    def _on_item_double_click(self, event):
        """Handle double-click on item row to show full details."""
        selection = self.tree.selection()
        if not selection:
            return
        
        iid = selection[0]
        item = self._item_map.get(iid)
        if not item:
            return
        
        # Open item details modal
        ItemDetailsModal(self, item)

    def _on_item_right_click(self, event):
        """Handle right-click on item row to show context menu."""
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        item = self._item_map.get(iid)
        if not item:
            return

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label="\U0001f916 Analyze with LLM",
            command=lambda: _launch_llm_analysis(self, item),
        )
        menu.tk_popup(event.x_root, event.y_root)


class ItemDetailsModal(tk.Toplevel):
    """Modal dialog showing full details for a single action item."""
    
    def __init__(self, parent, item: dict):
        super().__init__(parent)
        
        # Get title, clean HTML and truncate if needed for window title
        item_title = clean_html_from_title(item.get('title', 'Action Item Details'))
        window_title = item_title[:60] + '...' if len(item_title) > 60 else item_title
        self.title(window_title)
        
        self.geometry("800x650")
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 800) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 650) // 2
        self.geometry(f"+{x}+{y}")
        
        self._link_counter = 0  # For unique tag names
        self._item = item  # Store for column refresh
        self._create_widgets(item)
        
        # Bind Escape to close
        self.bind('<Escape>', lambda e: self.destroy())
        self.focus_set()
    
    def _open_column_selector(self):
        """Open the column selector dialog with all item columns."""
        # Get all columns from the item
        available = sorted(self._item.keys())
        # Compute which columns have empty values
        empty_cols = get_empty_columns(self._item)
        ColumnSelectorDialog(self, available, on_apply=self._on_columns_changed,
                           empty_columns=empty_cols)
    
    def _open_eta_editor(self):
        """Open the single-item ETA editor from detail view (AC-4)."""
        SingleEtaEditDialog(self, self._item, on_saved=self._on_eta_saved)
    
    def _on_eta_saved(self, item: dict, eta_date: str, notes: str):
        """Handle a single ETA save — update the in-memory item."""
        item['EtaDate'] = eta_date
        if notes:
            item['EtaStatus'] = notes
        # Refresh the detail view to reflect new values
        self._on_columns_changed()
    
    def _on_columns_changed(self):
        """Callback when column selection changes - rebuild display."""
        # Clear and rebuild content
        for widget in self._main_frame.winfo_children():
            widget.destroy()
        self._link_counter = 0
        self._build_content(self._item)
    
    def _open_url(self, url: str):
        """Open URL in system default browser."""
        import html
        webbrowser.open(html.unescape(url))
    
    def _insert_text_with_links(self, text_widget: tk.Text, content: str, base_tag: str = 'value'):
        """Insert text content, making URLs clickable.

        Uses extract_urls_from_text which picks anchors if present, else raw URLs.
        If the entire value starts with http(s):// and has no anchor tags,
        treat the whole value as a single link (handles URLs with spaces).
        """
        if not content:
            return

        stripped = content.strip()

        # If the whole value is a URL (no anchor tags), link it as one piece
        # This handles URLs with spaces in query params like "Past SLA"
        if (stripped.startswith(('http://', 'https://'))
                and '<a ' not in content.lower()):
            self._link_counter += 1
            link_tag = f'link_{self._link_counter}'
            text_widget.insert(tk.END, stripped, (link_tag, 'hyperlink'))
            text_widget.tag_bind(link_tag, '<Button-1>', lambda e, u=stripped: self._open_url(u))
            text_widget.tag_bind(link_tag, '<Enter>', lambda e: text_widget.configure(cursor='hand2'))
            text_widget.tag_bind(link_tag, '<Leave>', lambda e: text_widget.configure(cursor=''))
            return

        urls = extract_urls_from_text(content)

        if not urls:
            text_widget.insert(tk.END, content, base_tag)
            return

        last_end = 0
        for url, display_text, start, end in urls:
            # Insert plain text before this link
            if start > last_end:
                text_widget.insert(tk.END, content[last_end:start], base_tag)

            if not url:
                # Empty href anchor — render display text as plain text (skip link)
                if display_text.strip():
                    text_widget.insert(tk.END, display_text, base_tag)
            else:
                # Clickable link
                self._link_counter += 1
                link_tag = f'link_{self._link_counter}'
                text_widget.insert(tk.END, display_text, (link_tag, 'hyperlink'))
                text_widget.tag_bind(link_tag, '<Button-1>', lambda e, u=url: self._open_url(u))
                text_widget.tag_bind(link_tag, '<Enter>', lambda e: text_widget.configure(cursor='hand2'))
                text_widget.tag_bind(link_tag, '<Leave>', lambda e: text_widget.configure(cursor=''))

            last_end = end

        # Trailing text after last link
        if last_end < len(content):
            text_widget.insert(tk.END, content[last_end:], base_tag)
    
    def _insert_resource_uris(self, text_widget: tk.Text, value):
        """Insert ResourceURIs as a list of clickable links."""
        uris = parse_resource_uris(value)
        if not uris:
            text_widget.insert(tk.END, str(value), 'value')
            return
        
        text_widget.insert(tk.END, "\n", 'value')
        for uri in uris:
            self._link_counter += 1
            link_tag = f'link_{self._link_counter}'
            
            text_widget.insert(tk.END, "  • ", 'value')
            text_widget.insert(tk.END, uri, (link_tag, 'hyperlink'))
            text_widget.insert(tk.END, "\n", 'value')
            
            # Configure tag for this specific link
            text_widget.tag_bind(link_tag, '<Button-1>', lambda e, u=uri: self._open_url(u))
            text_widget.tag_bind(link_tag, '<Enter>', lambda e: text_widget.configure(cursor='hand2'))
            text_widget.tag_bind(link_tag, '<Leave>', lambda e: text_widget.configure(cursor=''))
    
    def _create_widgets(self, item: dict):
        """Create the details view content."""
        self._main_frame = ttk.Frame(self, padding=10)
        self._main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._build_content(item)
    
    def _build_content(self, item: dict):
        """Build the scrollable content area with item fields."""
        # Get visible columns or use all
        visible = ColumnSelectorDialog.get_visible_columns()
        
        # Filter item to only visible columns if set
        if visible is not None:
            display_item = {k: v for k, v in item.items() if k in visible}
            # Ensure we always have required fields for display
            for req in REQUIRED_COLUMNS:
                if req in item and req not in display_item:
                    display_item[req] = item[req]
        else:
            display_item = item
        
        # Scrollable text area
        text_frame = ttk.Frame(self._main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10), padx=10, pady=10)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar first so it's on right
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure text tags for styling
        text.tag_configure('header', font=("Segoe UI", 11, "bold"))
        text.tag_configure('separator', foreground='gray')
        text.tag_configure('label', font=("Segoe UI", 10, "bold"))
        text.tag_configure('value', font=("Consolas", 10))
        text.tag_configure('hyperlink', foreground='blue', underline=True, font=("Consolas", 10))
        
        # Group and display fields
        groups = group_item_fields(display_item)
        
        # Section indicators use colored circles for consistency with sidebar list view
        # Red (Status), Blue (Dates), Purple (Ownership), Black (Service & Program)
        group_titles = {
            'identity': '📋 Identity',
            'status': '🔴 Status',           # Red circle indicator
            'dates': '🔵 Dates',             # Blue circle indicator (changed from 📅 calendar)
            'ownership': '🟣 Ownership',     # Purple circle indicator (changed from 👤 person)
            'service_program': '⚫ Service & Program',  # Black circle indicator (changed from 🔧 wrench)
            'subscription': '☁️ Subscription',
            'resources': '🔗 Resources & Details',
            'other': '📎 Other',
        }
        
        group_order = ['identity', 'status', 'dates', 'ownership', 'service_program', 
                       'subscription', 'resources', 'other']
        
        for group_name in group_order:
            fields = groups.get(group_name, [])
            if not fields:
                continue
            
            # Group header
            text.insert(tk.END, f"\n{group_titles.get(group_name, group_name)}\n", 'header')
            text.insert(tk.END, "─" * 50 + "\n", 'separator')
            
            # Fields
            for field_name, formatted_value in fields:
                label = format_field_label(field_name)
                text.insert(tk.END, f"{label}: ", 'label')
                
                # Special handling for certain fields
                if field_name == 'ResourceURIs':
                    # Get the raw value for proper parsing
                    raw_value = item.get('ResourceURIs', formatted_value)
                    self._insert_resource_uris(text, raw_value)
                elif 'http' in formatted_value.lower() or '<a ' in formatted_value.lower():
                    # Contains a URL or anchor tag — auto-linkify
                    self._insert_text_with_links(text, formatted_value)
                    text.insert(tk.END, "\n", 'value')
                else:
                    text.insert(tk.END, f"{formatted_value}\n", 'value')
            
            text.insert(tk.END, "\n")
        
        # Make text read-only
        text.configure(state=tk.DISABLED)
        
        # Button frame with Columns, Update ETA and Close
        btn_frame = ttk.Frame(self._main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="Columns", command=self._open_column_selector).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="📅 Update ETA",
                   command=self._open_eta_editor).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)


class SortableTreeview(ttk.Treeview):
    """Treeview with sortable columns."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._sort_reverse = {}  # Track sort direction per column
    
    def heading(self, column, **kwargs):
        """Override heading to add sort on click."""
        if 'command' not in kwargs:
            kwargs['command'] = lambda c=column: self._sort_by_column(c)
        return super().heading(column, **kwargs)
    
    def sort_by_columns(self, columns: list[tuple[str, bool]]):
        """Sort treeview by multiple columns.
        
        Args:
            columns: List of (column_name, descending) tuples.
                     Applied in order, so last column is primary sort.
                     Example: [('name', False), ('count', True)] sorts by count desc, then name asc.
        """
        if not columns:
            return
        
        # Get all items
        all_items = list(self.get_children(''))
        if not all_items:
            return
        
        # Build sort key function for each column
        def get_sort_key(item, col):
            val = self.set(item, col) or ''
            # Check if numeric
            if val.replace(',', '').replace('.', '').replace('-', '').isdigit():
                try:
                    return (0, int(val.replace(',', '')))  # (type, value) tuple
                except ValueError:
                    return (1, val.lower())
            return (1, val.lower())
        
        # Sort in reverse order of columns (so first column ends up as primary)
        for col, descending in columns:
            all_items.sort(key=lambda item: get_sort_key(item, col), reverse=descending)
        
        # Rearrange items
        for index, item in enumerate(all_items):
            self.move(item, '', index)
    
    def _sort_by_column(self, col):
        """Sort treeview by column."""
        # Get all items with their values
        items = [(self.set(item, col), item) for item in self.get_children('')]
        
        # Determine sort direction
        reverse = self._sort_reverse.get(col, False)
        
        # Determine if column is numeric (check first non-empty value)
        is_numeric = False
        for val, _ in items:
            if val:
                is_numeric = val.replace(',', '').replace('.', '').isdigit()
                break
        
        # Sort based on type
        if is_numeric:
            def sort_key(x):
                try:
                    return int(x[0].replace(',', '')) if x[0] else 0
                except ValueError:
                    return 0
            items.sort(key=sort_key, reverse=reverse)
        else:
            items.sort(key=lambda x: (x[0] or '').lower(), reverse=reverse)
        
        # Rearrange items
        for index, (_, item) in enumerate(items):
            self.move(item, '', index)
        
        # Toggle sort direction for next click
        self._sort_reverse[col] = not reverse


# ---------------------------------------------------------------------------
# ETA Update Dialogs  (SFI-019)
# ---------------------------------------------------------------------------

class SingleEtaEditDialog(tk.Toplevel):
    """Small dialog for editing a single item's ETA from the detail view (AC-4)."""

    def __init__(self, parent, item: dict, on_saved=None):
        super().__init__(parent)
        self.title("Update ETA")
        self.geometry("420x260")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 420) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 260) // 2
        self.geometry(f"+{x}+{y}")

        self._item = item
        self._on_saved = on_saved
        self._create_widgets()
        self.bind('<Escape>', lambda e: self.destroy())
        self.focus_set()

    # ---- widget creation ---------------------------------------------------
    def _create_widgets(self):
        from sfi_reporter.eta_logic import propose_eta

        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        title = clean_html_from_title(self._item.get('title', ''))[:60]
        ttk.Label(frame, text=title, font=("Segoe UI", 10, "bold"),
                  wraplength=380).pack(anchor=tk.W)

        current_eta = (self._item.get('EtaDate') or 'None')[:10]
        ttk.Label(frame, text=f"Current ETA: {current_eta}",
                  foreground="gray").pack(anchor=tk.W, pady=(5, 0))

        proposed = propose_eta(
            self._item.get('dueDate') or self._item.get('DueDate'))

        # New ETA
        eta_frame = ttk.Frame(frame)
        eta_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(eta_frame, text="New ETA:").pack(side=tk.LEFT)
        self._eta_var = tk.StringVar(value=proposed)
        self._eta_entry = ttk.Entry(eta_frame, textvariable=self._eta_var,
                                     width=15)
        self._eta_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(eta_frame, text="(YYYY-MM-DD)",
                  foreground="gray").pack(side=tk.LEFT, padx=5)

        # Status / notes
        notes_frame = ttk.Frame(frame)
        notes_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(notes_frame, text="Status:").pack(side=tk.LEFT)
        self._notes_var = tk.StringVar(
            value=self._item.get('EtaStatus') or '')
        self._notes_entry = ttk.Entry(notes_frame,
                                       textvariable=self._notes_var, width=35)
        self._notes_entry.pack(side=tk.LEFT, padx=(5, 0))

        # Error label
        self._error_var = tk.StringVar()
        self._error_label = ttk.Label(frame, textvariable=self._error_var,
                                       foreground="red")
        self._error_label.pack(anchor=tk.W, pady=(5, 0))

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        self._save_btn = ttk.Button(btn_frame, text="💾 Save",
                                     command=self._on_save)
        self._save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel",
                   command=self.destroy).pack(side=tk.RIGHT)

    # ---- save logic --------------------------------------------------------
    def _on_save(self):
        from sfi_reporter.eta_logic import validate_eta_date, build_eta_update
        from sfi_reporter.data import get_client, get_current_user_alias

        date_str = self._eta_var.get().strip()
        ok, msg = validate_eta_date(date_str)
        if not ok:
            self._error_var.set(msg)
            return

        self._error_var.set("")
        self._save_btn.configure(state=tk.DISABLED)

        update = build_eta_update(
            self._item,
            date_str,
            notes=self._notes_var.get().strip(),
            fallback_alias=get_current_user_alias() or "",
        )

        def _save_bg():
            try:
                client = get_client()
                result = client.save_etas([update])
                self.after(0, lambda: self._on_save_result(result, date_str))
            except Exception as exc:
                self.after(0, lambda: self._on_save_error(str(exc)))

        threading.Thread(target=_save_bg, daemon=True).start()

    def _on_save_result(self, result, date_str: str):
        if result.success:
            logger.info("ETA saved for %s -> %s",
                        self._item.get('id'), date_str)
            if self._on_saved:
                self._on_saved(self._item, date_str,
                               self._notes_var.get().strip())
            self.destroy()
        else:
            self._save_btn.configure(state=tk.NORMAL)
            msg = result.error_message or "Unknown error"
            self._error_var.set(f"Save failed: {msg}")
            logger.warning("ETA save failed for %s: %s",
                           self._item.get('id'), msg)

    def _on_save_error(self, msg: str):
        self._save_btn.configure(state=tk.NORMAL)
        self._error_var.set(f"Error: {msg}")


class EtaModeDialog(tk.Toplevel):
    """Ask user to choose Manual or Bulk mode (AC-1)."""

    def __init__(self, parent, total_count: int, invalid_count: int, on_choice=None):
        super().__init__(parent)
        self.title("Update ETAs")
        self.geometry("400x220")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 220) // 2
        self.geometry(f"+{x}+{y}")

        self._on_choice = on_choice
        self._create_widgets(total_count, invalid_count)
        self.bind('<Escape>', lambda e: self.destroy())
        self.focus_set()

    def _create_widgets(self, total_count: int, invalid_count: int):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"\U0001f4c5 {total_count} total item(s), {invalid_count} with invalid ETAs",
                  font=("Segoe UI", 11, "bold")).pack(pady=(0, 15))

        ttk.Button(
            frame, text=f"\U0001f4dd Manual \u2014 review all {total_count} item(s)",
            command=lambda: self._choose("manual"),
        ).pack(fill=tk.X, pady=3)

        bulk_btn = ttk.Button(
            frame,
            text=f"\u26a1 Bulk \u2014 auto-fix {invalid_count} invalid ETA(s)" if invalid_count else "\u26a1 Bulk \u2014 no invalid ETAs to fix",
            command=lambda: self._choose("bulk"),
        )
        bulk_btn.pack(fill=tk.X, pady=3)
        if not invalid_count:
            bulk_btn.configure(state="disabled")

        ttk.Button(frame, text="Cancel",
                   command=self.destroy).pack(fill=tk.X, pady=(10, 0))

    def _choose(self, mode: str):
        self._on_choice(mode)
        self.destroy()


class ManualEtaReviewDialog(tk.Toplevel):
    """Step through items one-at-a-time for manual ETA review (AC-2)."""

    def __init__(self, parent, items: list[dict], on_complete=None):
        super().__init__(parent)
        self.title("Manual ETA Review")
        self.geometry("520x340")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 520) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 340) // 2
        self.geometry(f"+{x}+{y}")

        self._items = items
        self._index = 0
        self._saved: list[tuple[dict, str, str]] = []   # (item, eta, notes)
        self._skipped: list[dict] = []
        self._failed: list[tuple[dict, str]] = []
        self._on_complete = on_complete

        self._frame = ttk.Frame(self, padding=15)
        self._frame.pack(fill=tk.BOTH, expand=True)
        self._show_current()

        self.bind('<Escape>', lambda e: self._cancel())
        self.focus_set()

    # ---- per-item view -----------------------------------------------------
    def _show_current(self):
        from sfi_reporter.eta_logic import propose_eta

        for w in self._frame.winfo_children():
            w.destroy()

        if self._index >= len(self._items):
            self._show_summary()
            return

        item = self._items[self._index]
        n = self._index + 1
        total = len(self._items)

        ttk.Label(self._frame, text=f"Item {n} of {total}",
                  font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        title = clean_html_from_title(item.get('title', ''))[:80]
        ttk.Label(self._frame, text=title,
                  wraplength=480).pack(anchor=tk.W, pady=(5, 0))

        info_text = (
            f"Service: {item.get('S360_ServiceTreeServiceName', 'N/A')}\n"
            f"Current ETA: {(item.get('EtaDate') or 'None')[:10]}\n"
            f"Due Date: "
            f"{(item.get('dueDate') or item.get('DueDate') or 'N/A')[:10]}"
        )
        ttk.Label(self._frame, text=info_text,
                  foreground="gray").pack(anchor=tk.W, pady=(5, 0))

        proposed = propose_eta(item.get('dueDate') or item.get('DueDate'))

        # ETA entry
        eta_f = ttk.Frame(self._frame)
        eta_f.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(eta_f, text="New ETA:").pack(side=tk.LEFT)
        self._eta_var = tk.StringVar(value=proposed)
        ttk.Entry(eta_f, textvariable=self._eta_var,
                  width=15).pack(side=tk.LEFT, padx=5)

        notes_f = ttk.Frame(self._frame)
        notes_f.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(notes_f, text="Status:").pack(side=tk.LEFT)
        self._notes_var = tk.StringVar(
            value=item.get('EtaStatus') or '')
        ttk.Entry(notes_f, textvariable=self._notes_var,
                  width=35).pack(side=tk.LEFT, padx=5)

        self._error_var = tk.StringVar()
        ttk.Label(self._frame, textvariable=self._error_var,
                  foreground="red").pack(anchor=tk.W, pady=(5, 0))

        btn_f = ttk.Frame(self._frame)
        btn_f.pack(fill=tk.X, pady=(10, 0))
        self._accept_btn = ttk.Button(btn_f, text="✅ Accept",
                                       command=self._accept)
        self._accept_btn.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_f, text="⏭️ Skip",
                   command=self._skip).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_f, text="🔍 View Details",
                   command=self._view_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_f, text="❌ Cancel",
                   command=self._cancel).pack(side=tk.RIGHT)

    # ---- view details -------------------------------------------------------
    def _view_details(self):
        """Open ItemDetailsModal for the current item."""
        if self._index < len(self._items):
            item = self._items[self._index]
            ItemDetailsModal(self, item)

    # ---- accept / skip / cancel -------------------------------------------
    def _accept(self):
        from sfi_reporter.eta_logic import validate_eta_date, build_eta_update
        from sfi_reporter.data import get_client, get_current_user_alias

        date_str = self._eta_var.get().strip()
        ok, msg = validate_eta_date(date_str)
        if not ok:
            self._error_var.set(msg)
            return

        self._accept_btn.configure(state=tk.DISABLED)
        item = self._items[self._index]
        update = build_eta_update(
            item, date_str,
            notes=self._notes_var.get().strip(),
            fallback_alias=get_current_user_alias() or "",
        )

        def _save_bg():
            try:
                client = get_client()
                result = client.save_etas([update])
                self.after(0, lambda: self._on_result(result, item, date_str))
            except Exception as exc:
                self.after(0, lambda: self._on_error(item, str(exc)))

        threading.Thread(target=_save_bg, daemon=True).start()

    def _on_result(self, result, item, date_str):
        if result.success:
            logger.info("Manual ETA saved for %s -> %s",
                        item.get('id'), date_str)
            self._saved.append(
                (item, date_str, self._notes_var.get().strip()))
        else:
            msg = result.error_message or "Unknown"
            logger.warning("Manual ETA failed for %s: %s",
                           item.get('id'), msg)
            self._failed.append((item, msg))
        self._index += 1
        self._show_current()

    def _on_error(self, item, msg):
        logger.warning("Manual ETA error for %s: %s",
                       item.get('id'), msg)
        self._failed.append((item, msg))
        self._index += 1
        self._show_current()

    def _skip(self):
        self._skipped.append(self._items[self._index])
        self._index += 1
        self._show_current()

    def _cancel(self):
        self._skipped.extend(self._items[self._index:])
        self._show_summary()

    # ---- summary -----------------------------------------------------------
    def _show_summary(self):
        for w in self._frame.winfo_children():
            w.destroy()

        ttk.Label(self._frame, text="📊 Manual Update Summary",
                  font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))
        ttk.Label(self._frame,
                  text=f"✅ Saved: {len(self._saved)}").pack(anchor=tk.W)
        ttk.Label(self._frame,
                  text=f"⏭️ Skipped: {len(self._skipped)}").pack(anchor=tk.W)
        ttk.Label(self._frame,
                  text=f"❌ Failed: {len(self._failed)}").pack(anchor=tk.W)

        if self._failed:
            ttk.Label(self._frame, text="\nFailed items:",
                      foreground="red").pack(anchor=tk.W)
            for item, msg in self._failed[:5]:
                ttk.Label(
                    self._frame,
                    text=f"  • {item.get('id', '?')}: {msg}",
                    foreground="red", wraplength=480,
                ).pack(anchor=tk.W)

        logger.info("Manual ETA update complete: %d saved, %d skipped, "
                    "%d failed", len(self._saved), len(self._skipped),
                    len(self._failed))

        ttk.Button(self._frame, text="Close",
                   command=self._finish).pack(pady=(15, 0))

    def _finish(self):
        if self._on_complete:
            self._on_complete(self._saved, self._skipped, self._failed)
        self.destroy()


class BulkEtaProgressDialog(tk.Toplevel):
    """Show progress during bulk ETA update (AC-3)."""

    def __init__(self, parent, items: list[dict], on_complete=None):
        super().__init__(parent)
        self.title("Bulk ETA Update")
        self.geometry("450x220")
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 450) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 220) // 2
        self.geometry(f"+{x}+{y}")

        self._items = items
        self._on_complete = on_complete
        self._saved: list[tuple[dict, str, str]] = []
        self._failed: list[tuple[dict, str]] = []

        self._frame = ttk.Frame(self, padding=15)
        self._frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self._frame, text=f"⚡ Updating {len(items)} item(s)…",
                  font=("Segoe UI", 11, "bold")).pack(pady=(0, 10))

        self._progress_var = tk.IntVar(value=0)
        self._progress = ttk.Progressbar(
            self._frame, maximum=len(items),
            variable=self._progress_var, length=400)
        self._progress.pack(fill=tk.X, pady=5)

        self._status_var = tk.StringVar(value="Starting…")
        ttk.Label(self._frame,
                  textvariable=self._status_var).pack(anchor=tk.W)

        # Prevent close while running
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self.after(100, self._start)

    def _start(self):
        threading.Thread(target=self._run_bulk, daemon=True).start()

    def _run_bulk(self):
        from sfi_reporter.eta_logic import propose_eta, build_eta_update
        from sfi_reporter.data import get_client, get_current_user_alias

        client = get_client()
        alias = get_current_user_alias() or ""

        # Save items one-at-a-time for per-item error tracking
        for i, item in enumerate(self._items):
            eta_str = propose_eta(
                item.get('dueDate') or item.get('DueDate'))
            update = build_eta_update(item, eta_str, fallback_alias=alias)

            self.after(0, lambda idx=i, it=item: self._status_var.set(
                f"Saving {idx + 1}/{len(self._items)}: "
                f"{it.get('id', '?')[:30]}"
            ))

            try:
                result = client.save_etas([update])
                if result.success:
                    self._saved.append((item, eta_str, ""))
                    logger.info("Bulk ETA saved for %s -> %s",
                                item.get('id'), eta_str)
                else:
                    msg = result.error_message or "Unknown"
                    self._failed.append((item, msg))
                    logger.warning("Bulk ETA failed for %s: %s",
                                   item.get('id'), msg)
            except Exception as exc:
                self._failed.append((item, str(exc)))
                logger.warning("Bulk ETA error for %s: %s",
                               item.get('id'), exc)

            self.after(0, lambda idx=i: self._progress_var.set(idx + 1))

        self.after(0, self._show_summary)

    def _show_summary(self):
        self.protocol("WM_DELETE_WINDOW", self._finish)

        for w in self._frame.winfo_children():
            w.destroy()

        ttk.Label(self._frame, text="📊 Bulk Update Summary",
                  font=("Segoe UI", 12, "bold")).pack(pady=(0, 10))
        ttk.Label(self._frame,
                  text=f"✅ Saved: {len(self._saved)}").pack(anchor=tk.W)
        ttk.Label(self._frame,
                  text=f"❌ Failed: {len(self._failed)}").pack(anchor=tk.W)

        if self._failed:
            ttk.Label(self._frame, text="\nFailed items:",
                      foreground="red").pack(anchor=tk.W)
            for item, msg in self._failed[:5]:
                ttk.Label(
                    self._frame,
                    text=f"  • {item.get('id', '?')}: {msg}",
                    foreground="red", wraplength=400,
                ).pack(anchor=tk.W)

        logger.info("Bulk ETA update complete: %d saved, %d failed",
                    len(self._saved), len(self._failed))

        ttk.Button(self._frame, text="Close",
                   command=self._finish).pack(pady=(15, 0))

    def _finish(self):
        if self._on_complete:
            self._on_complete(self._saved, [], self._failed)
        self.destroy()


class SubscriptionPickerDialog(tk.Toplevel):
    """Modal dialog to pick one Azure subscription from a list."""

    def __init__(self, parent, choices: list[str]):
        super().__init__(parent)
        self.title("Select Subscription")
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)
        self.result: str | None = None

        # Parse "display_name  (sub_id)" into (name, sub_id, original)
        rows: list[tuple[str, str, str]] = []
        for c in choices:
            # Split on last '(' to separate name from id
            if "(" in c:
                idx = c.rfind("(")
                name = c[:idx].strip()
                sub_id = c[idx + 1:].rstrip(")")
            else:
                name = c
                sub_id = ""
            rows.append((name, sub_id, c))

        # Sort by subscription name (case-insensitive)
        rows.sort(key=lambda r: r[0].lower())

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Choose a subscription to scan:").pack(anchor=tk.W, pady=(0, 8))

        # Two-column treeview
        tree_frame = ttk.Frame(frm)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self._tree = ttk.Treeview(
            tree_frame,
            columns=("name", "sub_id"),
            show="headings",
            selectmode="browse",
            height=min(len(rows), 15),
        )
        self._tree.heading("name", text="Subscription Name")
        self._tree.heading("sub_id", text="Subscription ID")
        self._tree.column("name", width=280, minwidth=150)
        self._tree.column("sub_id", width=300, minwidth=200)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Store original choice string as iid tag for retrieval
        self._iid_to_choice: dict[str, str] = {}
        for i, (name, sub_id, original) in enumerate(rows):
            iid = str(i)
            self._tree.insert("", tk.END, iid=iid, values=(name, sub_id))
            self._iid_to_choice[iid] = original

        # Select first row
        if rows:
            self._tree.selection_set("0")
            self._tree.focus("0")

        self._tree.bind("<Double-Button-1>", lambda _: self._on_ok())

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(pady=(10, 0))
        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).pack(side=tk.LEFT, padx=5)

        # Center on parent
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window()

    def _on_ok(self):
        sel = self._tree.selection()
        if sel:
            self.result = self._iid_to_choice[sel[0]]
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()


class ConfigureLLMDialog(tk.Toplevel):
    """Modal dialog for configuring Azure OpenAI LLM settings.

    Allows manual entry of endpoint, deployment, and API version,
    or auto-detection via ``llm_extender.discover_azure_configs()``.
    """

    _DEFAULT_DEPLOYMENT = "gpt-4o"
    _DEFAULT_API_VERSION = "2024-10-21"

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configure LLM")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self._discovered_configs: list = []

        # --- Field variables ---
        self._endpoint_var = tk.StringVar(
            value=_load_setting("llm_endpoint", "") or ""
        )
        self._deployment_var = tk.StringVar(
            value=_load_setting("llm_deployment", self._DEFAULT_DEPLOYMENT) or self._DEFAULT_DEPLOYMENT
        )
        self._api_version_var = tk.StringVar(
            value=_load_setting("llm_api_version", self._DEFAULT_API_VERSION) or self._DEFAULT_API_VERSION
        )

        self._build_ui()

        # Center on parent after UI is built
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        pad = dict(padx=10, pady=4)
        frm = ttk.Frame(self, padding=15)
        frm.pack(fill=tk.BOTH, expand=True)

        # Endpoint
        ttk.Label(frm, text="Endpoint:").grid(row=0, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self._endpoint_var, width=55).grid(
            row=0, column=1, columnspan=2, sticky=tk.EW, **pad
        )

        # Deployment
        ttk.Label(frm, text="Deployment:").grid(row=1, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self._deployment_var, width=30).grid(
            row=1, column=1, columnspan=2, sticky=tk.EW, **pad
        )

        # API Version
        ttk.Label(frm, text="API Version:").grid(row=2, column=0, sticky=tk.W, **pad)
        ttk.Entry(frm, textvariable=self._api_version_var, width=30).grid(
            row=2, column=1, columnspan=2, sticky=tk.EW, **pad
        )

        # Detect section
        detect_frame = ttk.LabelFrame(frm, text="Detect from Azure CLI", padding=8)
        detect_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=(10, 4), padx=10)

        self._detect_btn = ttk.Button(
            detect_frame, text="\U0001f50d Detect", command=self._on_auto_detect
        )
        self._detect_btn.pack(side=tk.LEFT, padx=(0, 10))

        self._config_combo = ttk.Combobox(
            detect_frame, state="readonly", width=60
        )
        self._config_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._config_combo.bind("<<ComboboxSelected>>", self._on_config_selected)

        # Buttons row
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=(15, 0))

        ttk.Button(btn_frame, text="Save", command=self._on_save).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Clear", command=self._on_clear).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(
            side=tk.LEFT, padx=5
        )

    # --- Detect --------------------------------------------------------------

    def _on_auto_detect(self):
        """Phase 1: enumerate subscriptions, then show picker."""
        self._detect_btn.configure(text="Loading subs...", state="disabled")
        root = self.winfo_toplevel()

        def _list_subs():
            try:
                import logging
                for _az in ("azure.core", "azure.identity", "azure.mgmt"):
                    logging.getLogger(_az).setLevel(logging.WARNING)
                from llm_extender.discovery import _ensure_azure_sdk, SubscriptionClient, AzureCliCredential
                _ensure_azure_sdk()
                # Re-import after _ensure_azure_sdk populates the module globals
                import llm_extender.discovery as disc
                cred = disc.AzureCliCredential()
                sub_client = disc.SubscriptionClient(cred)
                subs = list(sub_client.subscriptions.list())
                root.after(0, lambda: self._on_subs_loaded(subs))
            except Exception as exc:
                root.after(0, lambda e=exc: self._on_detect_error(e))

        threading.Thread(target=_list_subs, daemon=True).start()

    def _on_subs_loaded(self, subs: list):
        """Phase 1 complete: show subscription picker."""
        self._detect_btn.configure(text="\U0001f50d Detect", state="normal")
        if not subs:
            messagebox.showinfo(
                "No Subscriptions",
                "No Azure subscriptions found.\n\n"
                "Ensure you are logged in with `az login`.",
                parent=self,
            )
            return

        # Build label → sub_id mapping
        choices = {f"{s.display_name}  ({s.subscription_id})": s.subscription_id for s in subs}

        picked = SubscriptionPickerDialog(self, list(choices.keys()))
        if not picked.result:
            return  # user cancelled

        selected_sub_id = choices[picked.result]
        self._scan_subscription(selected_sub_id)

    def _scan_subscription(self, subscription_id: str):
        """Phase 2: scan the chosen subscription for OpenAI deployments."""
        self._detect_btn.configure(text="Scanning...", state="disabled")
        root = self.winfo_toplevel()

        def _do_scan():
            try:
                import logging
                for _az in ("azure.core", "azure.identity", "azure.mgmt"):
                    logging.getLogger(_az).setLevel(logging.WARNING)
                from llm_extender import discover_azure_configs
                configs = discover_azure_configs(subscription_id=subscription_id)
                root.after(0, lambda: self._on_detect_complete(configs))
            except Exception as exc:
                root.after(0, lambda e=exc: self._on_detect_error(e))

        threading.Thread(target=_do_scan, daemon=True).start()

    def _on_detect_complete(self, configs: list):
        """Handle successful discovery (main thread)."""
        self._detect_btn.configure(text="\U0001f50d Detect", state="normal")
        self._discovered_configs = configs
        if not configs:
            self._config_combo["values"] = []
            messagebox.showinfo(
                "No Results",
                "No Azure OpenAI deployments found in the selected subscription.",
                parent=self,
            )
            return
        labels = [
            f"{c.base_url}  \u2014  {c.deployment} ({c.model})"
            for c in configs
        ]
        self._config_combo["values"] = labels
        self._config_combo.current(0)
        self._on_config_selected(None)

    def _on_detect_error(self, error: Exception):
        """Handle discovery failure (main thread)."""
        self._detect_btn.configure(text="\U0001f50d Detect", state="normal")
        if isinstance(error, ImportError):
            messagebox.showerror(
                "Azure SDK Not Installed",
                "Azure discovery SDK is not available.\n\n"
                "Install with:\n  pip install llm-extender[azure-discover]",
                parent=self,
            )
        else:
            messagebox.showerror(
                "Detection Failed",
                f"Discovery error: {error}",
                parent=self,
            )

    def _on_config_selected(self, _event):
        """Populate fields from the selected discovered config."""
        idx = self._config_combo.current()
        if idx < 0 or idx >= len(self._discovered_configs):
            return
        cfg = self._discovered_configs[idx]
        self._endpoint_var.set(cfg.base_url)
        self._deployment_var.set(cfg.deployment)
        self._api_version_var.set(cfg.api_version)

    # --- Save / Clear / Cancel -----------------------------------------------

    def _on_save(self):
        """Validate and persist the config."""
        endpoint = self._endpoint_var.get().strip()
        deploy = self._deployment_var.get().strip()
        api_ver = self._api_version_var.get().strip()

        if not endpoint.startswith("https://"):
            messagebox.showerror(
                "Invalid Endpoint",
                "Endpoint must start with https://",
                parent=self,
            )
            return

        _save_setting("llm_endpoint", endpoint)
        _save_setting("llm_deployment", deploy or self._DEFAULT_DEPLOYMENT)
        _save_setting("llm_api_version", api_ver or self._DEFAULT_API_VERSION)
        logger.info("LLM config saved: endpoint=%s deployment=%s api_version=%s",
                    endpoint, deploy, api_ver)
        self.destroy()

    def _on_clear(self):
        """Remove saved LLM config and reset fields to defaults."""
        _save_setting("llm_endpoint", "")
        _save_setting("llm_deployment", "")
        _save_setting("llm_api_version", "")
        self._endpoint_var.set("")
        self._deployment_var.set(self._DEFAULT_DEPLOYMENT)
        self._api_version_var.set(self._DEFAULT_API_VERSION)
        logger.info("LLM config cleared.")


def _load_llm_config() -> LLMConfig:
    """Load LLM config: saved settings first, then env vars.

    Returns:
        A configured LLMConfig instance.

    Raises:
        LLMConfigError: If no config source is available.
    """
    endpoint = _load_setting("llm_endpoint", "") or ""
    if endpoint.strip():
        # Saved config exists — use it.
        return LLMConfig(
            endpoint=endpoint.strip(),
            deployment=(_load_setting("llm_deployment", "") or "gpt-4o").strip(),
            api_version=(_load_setting("llm_api_version", "") or "2024-10-21").strip(),
        )
    # No saved config — fall back to env vars.
    return LLMConfig.from_env()


class SFIReporterApp:
    """Main application class."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SFI Reporter")
        self.root.geometry("1200x750")
        
        self.current_data: dict = {}
        self._unfiltered_data: dict = {}  # original data before any filter
        self.detected_alias = get_current_user_alias() or ""
        
        # Mappings for drill-down (populated when data loads)
        self._service_id_map: dict = {}  # row iid -> service ID
        self._service_name_map: dict = {}  # service ID -> service name
        self._program_id_map: dict = {}  # row iid -> program ID
        self._kpi_id_map: dict = {}  # row iid -> KPI ID
        
        self._last_filter_clauses: list = []   # last applied QueryClause list
        self._last_filter_ussec: bool = False       # last USSec toggle state

        self._build_ui()
        self._load_cached_data()
    
    def _build_ui(self):
        """Build the UI components."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="📊 SFI Reporter", font=("Segoe UI", 20, "bold"))
        header_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(main_frame, text="View SFI/QEI action items for your services", foreground="gray")
        subtitle_label.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(controls_frame, text="User Alias:").pack(side=tk.LEFT)
        
        self.alias_var = tk.StringVar(value=self.detected_alias)
        self.alias_entry = ttk.Entry(controls_frame, textvariable=self.alias_var, width=30)
        self.alias_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Bind Enter key to load cache for the entered alias
        self.alias_entry.bind('<Return>', lambda e: self._load_cached_data())
        self.alias_entry.bind('<FocusOut>', lambda e: self._load_cached_data())
        
        self.refresh_btn = ttk.Button(controls_frame, text="🔄 Refresh Data", command=self._on_refresh)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(controls_frame, text="🗑️ Clear Cache", command=self._on_clear_cache)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.retry_btn = tk.Button(controls_frame, text="🔁 Retry Failed KPIs",
                                    command=self._on_retry_failed,
                                    bg="#d9534f", fg="white", activebackground="#c9302c",
                                    activeforeground="white", font=("Segoe UI", 9, "bold"),
                                    relief=tk.RAISED, padx=8, pady=2)
        # Hidden until there are failures
        
        self.query_btn = ttk.Button(controls_frame, text="🔍 Filter", command=self._on_query, state="disabled")
        self.query_btn.pack(side=tk.LEFT, padx=5)
        
        self.eta_btn = ttk.Button(controls_frame, text="📋 Update ETAs",
                                   command=self._on_update_etas, state="disabled")
        self.eta_btn.pack(side=tk.LEFT, padx=5)

        self.llm_config_btn = ttk.Button(
            controls_frame, text="⚙️ Configure LLM",
            command=lambda: ConfigureLLMDialog(self.root),
        )
        self.llm_config_btn.pack(side=tk.LEFT, padx=5)

        # "Re-apply filter after refresh" checkbox — persisted across sessions
        self._reapply_filter_var = tk.BooleanVar(
            value=_load_setting('reapply_filter_after_refresh', False)
        )
        self._reapply_filter_var.trace_add(
            'write',
            lambda *_: _save_setting('reapply_filter_after_refresh',
                                     self._reapply_filter_var.get()),
        )
        self._reapply_cb = ttk.Checkbutton(
            controls_frame,
            text="Re-apply filter after refresh",
            variable=self._reapply_filter_var,
        )
        self._reapply_cb.pack(side=tk.LEFT, padx=(10, 0))
        
        # State for retry
        self._failed_kpis: list[dict] = []
        self._audience_ids: list[str] = []
        self._kpi_names: dict = {}
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.cache_age_var = tk.StringVar()
        self.cache_age_label = ttk.Label(status_frame, textvariable=self.cache_age_var, foreground="green")
        self.cache_age_label.pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Top section: Services (left) and Program Summary (right)
        top_section = ttk.Frame(main_frame)
        top_section.pack(fill=tk.X, pady=5)
        
        # Services section (left side)
        services_container = ttk.Frame(top_section)
        services_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(services_container, text="🔧 Services", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        
        services_frame = ttk.Frame(services_container)
        services_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Use "tree headings" to show hierarchy (tree column + data columns)
        self.services_tree = SortableTreeview(services_frame, columns=("name", "count", "sla", "invalid_eta"), show="tree headings", height=6)
        self.services_tree.heading("#0", text="")  # Tree column (for expand/collapse)
        self.services_tree.heading("name", text="Name")
        self.services_tree.heading("count", text="Total")
        self.services_tree.heading("sla", text="Out of SLA")
        self.services_tree.heading("invalid_eta", text="Invalid ETA")
        self.services_tree.column("#0", width=20, stretch=False)  # Narrow tree column
        self.services_tree.column("name", width=180, anchor=tk.W)
        self.services_tree.column("count", width=60, anchor=tk.CENTER)
        self.services_tree.column("sla", width=80, anchor=tk.CENTER)
        self.services_tree.column("invalid_eta", width=80, anchor=tk.CENTER)
        
        # Store owner ID mapping for drill-down
        self._owner_id_map = {}   # iid -> owner_name (level1)
        self._owner_l2_map = {}   # iid -> owner_name (level2)
        
        services_scroll = ttk.Scrollbar(services_frame, orient=tk.VERTICAL, command=self.services_tree.yview)
        self.services_tree.configure(yscrollcommand=services_scroll.set)
        
        self.services_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        services_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click for drill-down
        self.services_tree.bind('<Double-1>', self._on_service_double_click)
        
        # Program Summary section (right side)
        program_container = ttk.Frame(top_section)
        program_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(program_container, text="📈 Program Summary", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        
        program_frame = ttk.Frame(program_container)
        program_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.program_tree = SortableTreeview(program_frame, columns=("program", "count", "sla", "invalid_eta"), show="headings", height=6)
        self.program_tree.heading("program", text="Program")
        self.program_tree.heading("count", text="Total")
        self.program_tree.heading("sla", text="Out of SLA")
        self.program_tree.heading("invalid_eta", text="Invalid ETA")
        self.program_tree.column("program", width=230, anchor=tk.W)
        self.program_tree.column("count", width=60, anchor=tk.CENTER)
        self.program_tree.column("sla", width=70, anchor=tk.CENTER)
        self.program_tree.column("invalid_eta", width=70, anchor=tk.CENTER)
        
        program_scroll = ttk.Scrollbar(program_frame, orient=tk.VERTICAL, command=self.program_tree.yview)
        self.program_tree.configure(yscrollcommand=program_scroll.set)
        
        self.program_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        program_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click for drill-down
        self.program_tree.bind('<Double-1>', self._on_program_double_click)
        
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Action Items section
        ttk.Label(main_frame, text="📋 Action Items", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(5, 0))
        
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.action_tree = SortableTreeview(
            action_frame, 
            columns=("name", "count", "sla", "invalid_eta"), 
            show="headings"
        )
        self.action_tree.heading("name", text="Action Item (KPI)")
        self.action_tree.heading("count", text="Total")
        self.action_tree.heading("sla", text="Out of SLA")
        self.action_tree.heading("invalid_eta", text="Invalid ETA")
        self.action_tree.column("name", width=450, anchor=tk.W)
        self.action_tree.column("count", width=80, anchor=tk.CENTER)
        self.action_tree.column("sla", width=80, anchor=tk.CENTER)
        self.action_tree.column("invalid_eta", width=80, anchor=tk.CENTER)
        
        action_scroll = ttk.Scrollbar(action_frame, orient=tk.VERTICAL, command=self.action_tree.yview)
        self.action_tree.configure(yscrollcommand=action_scroll.set)
        
        self.action_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        action_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click for drill-down
        self.action_tree.bind('<Double-1>', self._on_action_double_click)
        # Bind right-click for LLM analysis context menu
        self.action_tree.bind('<Button-3>', self._on_kpi_right_click)
    
    def _load_cached_data(self, user_alias: str = None):
        """Load cached data for a user.
        
        Args:
            user_alias: User alias to load cache for. If None, uses current alias field value.
        """
        alias = user_alias or self.alias_var.get().strip()
        if alias:
            cached = read_cache(alias)
            if cached and is_cache_valid(cached):
                self._update_tables(cached)
                age = get_cache_age_minutes(cached)
                if age is not None:
                    self.cache_age_var.set(f"Cache: {age} minutes old")
                    color = "orange" if age > 30 else "green"
                    self.cache_age_label.configure(foreground=color)
                return True
        return False
    
    def _on_alias_change(self, *args):
        """Handle alias field change - load cached data for new alias."""
        alias = self.alias_var.get().strip()
        if alias:
            self._load_cached_data(alias)
    
    def _update_tables(self, data: dict, *, is_filtered: bool = False):
        """Update tables with data."""
        self.current_data = data
        if not is_filtered:
            self._unfiltered_data = data
        
        # Enable filter button now that data is loaded
        if data.get('detailed_items'):
            self.query_btn.configure(state="normal")
            self.eta_btn.configure(state="normal")
        
        # Clear existing rows and mappings
        for item in self.services_tree.get_children():
            self.services_tree.delete(item)
        for item in self.action_tree.get_children():
            self.action_tree.delete(item)
        for item in self.program_tree.get_children():
            self.program_tree.delete(item)
        
        self._service_id_map.clear()
        self._service_name_map.clear()
        self._program_id_map.clear()
        self._kpi_id_map.clear()
        self._owner_id_map.clear()
        self._owner_l2_map.clear()
        
        # Get pre-computed stats if available
        service_stats = data.get('service_stats', {})
        program_stats = data.get('program_stats', {})
        kpi_stats = data.get('kpi_stats', {})
        owner_stats = data.get('owner_stats', {})
        is_manager = data.get('is_manager', False)
        service_owners = data.get('service_owners', {})
        
        # Update program summary table
        for program_name, stats in sorted(program_stats.items(), key=lambda x: x[1].get('count', 0), reverse=True):
            iid = self.program_tree.insert("", tk.END, values=(
                program_name,
                stats.get('count', 0),
                stats.get('sla', 0),
                stats.get('invalid_eta', 0),
            ))
            # Store program ID mapping
            program_id = stats.get('id', program_name)  # Use name as fallback
            self._program_id_map[iid] = program_id
        
        # Update services table - hierarchical view for managers, flat for ICs
        services = data.get('services', [])
        
        if is_manager and owner_stats and service_stats:
            # Manager view: Group services by owner (pivot table style)
            # Get org_mapping from cached data
            org_mapping = data.get('org_mapping', {})
            level2_stats = data.get('level2_stats', {})
            
            # Detect if this is a 2-level hierarchy
            has_level2 = any(
                isinstance(m, OrgAncestry) and m.level2 is not None
                for m in org_mapping.values()
            )
            
            # Build service mapping: for each service, determine (level1, level2)
            # Structure: {level1: {level2_or_None: [(svc_id, svc_name, stats)]}}
            hierarchy: dict[str, dict[Optional[str], list[tuple[str, str, dict]]]] = {}
            
            for svc_id, stats in service_stats.items():
                svc_name = stats.get('name', svc_id)
                owners = service_owners.get(svc_name, None)
                
                if owners is None:
                    level1, level2 = 'Unknown Owner', None
                elif len(owners) == 0:
                    level1, level2 = 'No Owner', None
                elif org_mapping:
                    level1, level2 = None, None
                    for owner in owners:
                        mapped = org_mapping.get(owner)
                        if isinstance(mapped, OrgAncestry):
                            if mapped.level1 and mapped.level1 != 'Unknown Owner':
                                level1 = mapped.level1
                                level2 = mapped.level2
                                break
                        elif mapped and mapped != 'Unknown Owner':
                            level1 = mapped
                            break
                    if level1 is None:
                        level1 = 'Unknown Owner'
                else:
                    level1, level2 = owners[0], None
                
                if level1 not in hierarchy:
                    hierarchy[level1] = {}
                if level2 not in hierarchy[level1]:
                    hierarchy[level1][level2] = []
                hierarchy[level1][level2].append((svc_id, svc_name, stats))
            
            # Insert treeview rows
            for owner_name, owner_stat in sorted(owner_stats.items(), key=lambda x: x[1].get('count', 0), reverse=True):
                # Insert Level-1 parent row
                owner_iid = self.services_tree.insert("", tk.END, values=(
                    f"👤 {owner_name}",
                    owner_stat.get('count', 0),
                    owner_stat.get('sla', 0),
                    owner_stat.get('invalid_eta', 0),
                ), open=True)
                self._owner_id_map[owner_iid] = owner_name
                
                l2_dict = hierarchy.get(owner_name, {})
                
                if has_level2 and any(k is not None for k in l2_dict.keys()):
                    # 2-level mode: insert Level-2 sub-rows, then services under each
                    
                    # First, insert services with level2=None directly under level1
                    direct_svcs = l2_dict.get(None, [])
                    for svc_id, svc_name, stats in sorted(direct_svcs, key=lambda x: x[2].get('count', 0), reverse=True):
                        child_iid = self.services_tree.insert(owner_iid, tk.END, values=(
                            svc_name,
                            stats.get('count', 0),
                            stats.get('sla', 0),
                            stats.get('invalid_eta', 0),
                        ))
                        self._service_id_map[child_iid] = svc_id
                        self._service_name_map[svc_id] = svc_name
                    
                    # Then, insert Level-2 sub-rows with their services
                    for l2_name in sorted(
                        (k for k in l2_dict if k is not None),
                        key=lambda n: level2_stats.get((owner_name, n), {}).get('count', 0),
                        reverse=True
                    ):
                        l2_stat = level2_stats.get((owner_name, l2_name), {})
                        l2_iid = self.services_tree.insert(owner_iid, tk.END, values=(
                            f"👤 {l2_name}",
                            l2_stat.get('count', 0),
                            l2_stat.get('sla', 0),
                            l2_stat.get('invalid_eta', 0),
                        ), open=True)
                        self._owner_l2_map[l2_iid] = l2_name
                        
                        svc_list = l2_dict[l2_name]
                        for svc_id, svc_name, stats in sorted(svc_list, key=lambda x: x[2].get('count', 0), reverse=True):
                            child_iid = self.services_tree.insert(l2_iid, tk.END, values=(
                                svc_name,
                                stats.get('count', 0),
                                stats.get('sla', 0),
                                stats.get('invalid_eta', 0),
                            ))
                            self._service_id_map[child_iid] = svc_id
                            self._service_name_map[svc_id] = svc_name
                else:
                    # 1-level mode: services directly under level1 (existing behavior)
                    all_svcs = []
                    for svc_list in l2_dict.values():
                        all_svcs.extend(svc_list)
                    for svc_id, svc_name, stats in sorted(all_svcs, key=lambda x: x[2].get('count', 0), reverse=True):
                        child_iid = self.services_tree.insert(owner_iid, tk.END, values=(
                            svc_name,
                            stats.get('count', 0),
                            stats.get('sla', 0),
                            stats.get('invalid_eta', 0),
                        ))
                        self._service_id_map[child_iid] = svc_id
                        self._service_name_map[svc_id] = svc_name
        elif services:
            # IC view: User owns services - show them flat
            for s in services:
                svc_id = s.get('Id', '')
                stats = service_stats.get(svc_id, {})
                iid = self.services_tree.insert("", tk.END, values=(
                    s.get('Name', 'Unknown'),
                    stats.get('count', 0),
                    stats.get('sla', 0),
                    stats.get('invalid_eta', 0),
                ))
                self._service_id_map[iid] = svc_id
                self._service_name_map[svc_id] = s.get('Name', 'Unknown')
        elif service_stats:
            # Fallback: Team view without owner info - show services flat
            for svc_id, stats in sorted(service_stats.items(), key=lambda x: x[1].get('count', 0), reverse=True):
                iid = self.services_tree.insert("", tk.END, values=(
                    stats.get('name', svc_id),
                    stats.get('count', 0),
                    stats.get('sla', 0),
                    stats.get('invalid_eta', 0),
                ))
                self._service_id_map[iid] = svc_id
                self._service_name_map[svc_id] = stats.get('name', svc_id)
        
        # Update action items table (now from kpi_stats)
        kpi_stats = data.get('kpi_stats', {})
        
        for kpi_id, stats in sorted(kpi_stats.items(), key=lambda x: x[1].get('count', 0), reverse=True):
            iid = self.action_tree.insert("", tk.END, values=(
                stats.get('name', kpi_id),
                stats.get('count', 0),
                stats.get('sla', 0),
                stats.get('invalid_eta', 0),
            ))
            self._kpi_id_map[iid] = kpi_id
        
        # Apply default sorting to program and action tables
        # Note: Services table uses hierarchical view when manager, don't re-sort
        self.program_tree.sort_by_columns([('program', False), ('count', True), ('sla', True), ('invalid_eta', True)])
        self.action_tree.sort_by_columns([('name', False), ('count', True), ('sla', True), ('invalid_eta', True)])
        
        # Update cache age
        age = get_cache_age_minutes(data)
        if age is not None:
            self.cache_age_var.set(f"Cache: {age} minutes old")
            color = "orange" if age > 30 else "green"
            self.cache_age_label.configure(foreground=color)
        else:
            self.cache_age_var.set("")
    
    def _on_service_double_click(self, event):
        """Handle double-click on service or owner row."""
        selection = self.services_tree.selection()
        if not selection:
            return
        
        iid = selection[0]
        
        # Check Level-2 owner rows first (takes precedence over Level-1)
        l2_owner_name = self._owner_l2_map.get(iid)
        if l2_owner_name:
            service_owners_data = self.current_data.get('service_owners', {})
            org_mapping = self.current_data.get('org_mapping', {})
            
            matching_svcs = collect_services_for_owner(
                l2_owner_name, "level2", service_owners_data, org_mapping
            )
            items = [
                item for item in self.current_data.get('detailed_items', [])
                if item.get('S360_ServiceTreeServiceName') in matching_svcs
            ]
            
            DetailModal(
                self.root,
                f"Action Items for {l2_owner_name}",
                items,
                self._service_name_map,
                on_eta_complete=self._on_eta_update_complete,
            )
            return
        
        # Check Level-1 owner rows
        owner_name = self._owner_id_map.get(iid)
        if owner_name:
            service_owners_data = self.current_data.get('service_owners', {})
            org_mapping = self.current_data.get('org_mapping', {})
            
            # Special cases for Unknown/No Owner
            if owner_name == 'Unknown Owner':
                known_services = set(service_owners_data.keys())
                items = [
                    item for item in self.current_data.get('detailed_items', [])
                    if item.get('S360_ServiceTreeServiceName') not in known_services
                ]
            elif owner_name == 'No Owner':
                empty_owner_services = {svc for svc, owners in service_owners_data.items() if not owners}
                items = [
                    item for item in self.current_data.get('detailed_items', [])
                    if item.get('S360_ServiceTreeServiceName') in empty_owner_services
                ]
            else:
                # Use collect_services_for_owner to get entire subtree
                matching_svcs = collect_services_for_owner(
                    owner_name, "level1", service_owners_data, org_mapping
                )
                items = [
                    item for item in self.current_data.get('detailed_items', [])
                    if item.get('S360_ServiceTreeServiceName') in matching_svcs
                ]
            
            DetailModal(
                self.root,
                f"Action Items for {owner_name}",
                items,
                self._service_name_map,
                on_eta_complete=self._on_eta_update_complete,
            )
            return
        
        # Service row
        service_id = self._service_id_map.get(iid)
        if not service_id:
            return
        
        service_name = self._service_name_map.get(service_id, service_id)
        items = filter_items_by_service(
            self.current_data.get('detailed_items', []),
            service_id
        )
        
        DetailModal(
            self.root,
            f"Action Items for {service_name}",
            items,
            self._service_name_map,
            on_eta_complete=self._on_eta_update_complete,
        )
    
    def _on_program_double_click(self, event):
        """Handle double-click on program row."""
        selection = self.program_tree.selection()
        if not selection:
            return
        
        iid = selection[0]
        program_id = self._program_id_map.get(iid)
        if not program_id:
            return
        
        # Get program name from the row values
        values = self.program_tree.item(iid, 'values')
        program_name = values[0] if values else program_id
        
        # Handle "Unassigned" specially - items with no program
        if program_id == 'unassigned':
            items = [
                item for item in self.current_data.get('detailed_items', [])
                if not (item.get('S360_ProgramIds') or [])
            ]
        else:
            items = filter_items_by_program(
                self.current_data.get('detailed_items', []),
                program_id
            )
        
        DetailModal(
            self.root,
            f"Action Items for {program_name}",
            items,
            self._service_name_map,
            on_eta_complete=self._on_eta_update_complete,
        )
    
    def _on_action_double_click(self, event):
        """Handle double-click on action item (KPI) row."""
        selection = self.action_tree.selection()
        if not selection:
            return
        
        iid = selection[0]
        kpi_id = self._kpi_id_map.get(iid)
        if not kpi_id:
            return
        
        # Get KPI name from the row values
        values = self.action_tree.item(iid, 'values')
        kpi_name = values[0] if values else kpi_id
        
        # Filter by KPI ID
        items = [
            item for item in self.current_data.get('detailed_items', [])
            if item.get('_kpi_id') == kpi_id
        ]
        
        DetailModal(
            self.root,
            f"Action Items: {kpi_name}",
            items,
            self._service_name_map,
            on_eta_complete=self._on_eta_update_complete,
        )

    def _on_kpi_right_click(self, event):
        """Handle right-click on KPI row to show LLM analysis context menu."""
        iid = self.action_tree.identify_row(event.y)
        if not iid:
            return
        self.action_tree.selection_set(iid)
        kpi_id = self._kpi_id_map.get(iid)
        if not kpi_id:
            return

        # Get the first matching action item for this KPI
        items = [
            item for item in self.current_data.get('detailed_items', [])
            if item.get('_kpi_id') == kpi_id
        ]
        if not items:
            return

        # Use the first item as representative for analysis
        item = items[0]

        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(
            label="\U0001f916 Analyze with LLM",
            command=lambda: _launch_llm_analysis(self.root, item),
        )
        menu.tk_popup(event.x_root, event.y_root)

    def _update_status(self, message: str, color: str = "black"):
        """Update status label (thread-safe)."""
        self.root.after(0, lambda: self._do_update_status(message, color))
    
    def _do_update_status(self, message: str, color: str):
        """Actually update status (must be called from main thread)."""
        self.status_var.set(message)
        self.status_label.configure(foreground=color)
    
    def _on_update_etas(self):
        """Handle 'Update ETAs' button click.

        Shows a mode-selection dialog. Manual mode passes ALL items
        (sorted invalid-first). Bulk mode passes only invalid items.
        """
        from sfi_reporter.eta_logic import get_items_needing_eta_update
        from sfi_reporter.data import is_invalid_eta

        items = (self.current_data or {}).get('detailed_items', [])
        if not items:
            return

        invalid = get_items_needing_eta_update(items)

        # Sort all items: invalid ETAs first
        sorted_all = sorted(items, key=lambda it: (
            0 if is_invalid_eta(it.get('EtaDate')) else 1
        ))

        def on_mode(mode: str):
            if mode == "manual":
                ManualEtaReviewDialog(
                    self.root, sorted_all,
                    on_complete=self._on_eta_update_complete)
            else:
                BulkEtaProgressDialog(
                    self.root, invalid,
                    on_complete=self._on_eta_update_complete)

        EtaModeDialog(self.root, len(items), len(invalid), on_choice=on_mode)

    def _on_eta_update_complete(self, saved, skipped, failed):
        """Post-save callback — mutate cache and re-render tables (AC-5)."""
        from sfi_reporter.data import is_invalid_eta
        from datetime import datetime

        if not saved:
            return

        # Mutate the in-memory items
        for item, eta_str, notes in saved:
            item['EtaDate'] = eta_str
            if notes:
                item['EtaStatus'] = notes

        # Recompute invalid_eta stats from current data
        data = self.current_data
        if data:
            detailed = data.get('detailed_items', [])
            for stats_dict in (data.get('service_stats', {}),
                               data.get('kpi_stats', {}),
                               data.get('program_stats', {})):
                for key in stats_dict:
                    stats_dict[key]['invalid_eta'] = 0

            for row in detailed:
                if is_invalid_eta(row.get('EtaDate')):
                    svc_id = row.get('S360_ServiceId', 'Unknown')
                    kpi_id = row.get('_kpi_id', 'Unknown')
                    if svc_id in data.get('service_stats', {}):
                        data['service_stats'][svc_id]['invalid_eta'] += 1
                    if kpi_id in data.get('kpi_stats', {}):
                        data['kpi_stats'][kpi_id]['invalid_eta'] += 1

                    pid_list = row.get('S360_ProgramIds') or []
                    if pid_list:
                        programs_lookup = data.get('programs_lookup', {})
                        pname = programs_lookup.get(pid_list[0], 'Other Program')
                        if pname in data.get('program_stats', {}):
                            data['program_stats'][pname]['invalid_eta'] += 1

            # Recompute owner stats for manager view
            if data.get('is_manager') and data.get('owner_stats'):
                svc_owners = data.get('service_owners', {})
                org_map = data.get('org_mapping', {})
                data['owner_stats'] = aggregate_by_owner(
                    detailed, svc_owners,
                    org_mapping=org_map if org_map else None,
                )

            self._update_tables(data, is_filtered=bool(
                self._unfiltered_data and
                self._unfiltered_data is not data))

            # Persist updated items back to disk cache
            alias = self.alias_var.get().strip()
            if alias:
                data['timestamp'] = datetime.now().isoformat()
                write_cache(alias, data)

        n = len(saved)
        self._update_status(
            f"✅ {n} ETA(s) updated successfully!", "green")

    def _on_refresh(self):
        """Handle refresh button click."""
        alias = self.alias_var.get().strip()
        if not alias:
            messagebox.showwarning("Warning", "Please enter a user alias")
            return
        
        # Disable buttons during refresh
        self.refresh_btn.configure(state=tk.DISABLED)
        self.clear_btn.configure(state=tk.DISABLED)
        self._update_status("Starting...", "blue")
        
        def fetch_in_background():
            def on_status(msg):
                self._update_status(msg, "blue")
            
            data = do_refresh(alias, on_status=on_status)
            
            # Update UI on main thread
            self.root.after(0, lambda: self._on_refresh_complete(data))
        
        threading.Thread(target=fetch_in_background, daemon=True).start()
    
    def _on_refresh_complete(self, data: Optional[dict]):
        """Handle refresh completion (called on main thread)."""
        self.refresh_btn.configure(state=tk.NORMAL)
        self.clear_btn.configure(state=tk.NORMAL)
        
        if data:
            self._update_tables(data)

            # Re-apply last filter if checkbox is checked
            if (self._reapply_filter_var.get()
                    and self._last_filter_clauses):
                self._reapply_last_filter()

            # Track failed KPIs for retry
            failed = data.get('failed_kpis', [])
            self._failed_kpis = failed
            self._audience_ids = data.get('audience_ids', [])
            self._kpi_names = data.get('kpi_names', {})
            
            if failed:
                self.retry_btn.pack(side=tk.LEFT, padx=5)
                names = [f['kpi_name'] for f in failed]
                self._update_status(
                    f"⚠️ {len(failed)} KPI(s) failed: {', '.join(names)}", "orange"
                )
            else:
                self.retry_btn.pack_forget()
                services = data.get('services', [])
                detailed_items = data.get('detailed_items', [])
                kpi_stats = data.get('kpi_stats', {})
                has_data = bool(services or detailed_items or kpi_stats)
                if not has_data:
                    self._update_status("⚠️ No action items found for this user", "orange")
                else:
                    self._update_status("✅ Data refreshed!", "green")
        else:
            self.retry_btn.pack_forget()
            self._update_status("❌ Error fetching data", "red")
    
    def _on_retry_failed(self):
        """Retry only the KPIs that failed on the last refresh."""
        if not self._failed_kpis or not self._audience_ids:
            return
        
        failed_ids = [f['kpi_id'] for f in self._failed_kpis]
        logger.info("Retrying %d failed KPIs: %s", len(failed_ids),
                    [f['kpi_name'] for f in self._failed_kpis])
        
        self.refresh_btn.configure(state=tk.DISABLED)
        self.clear_btn.configure(state=tk.DISABLED)
        self.retry_btn.configure(state=tk.DISABLED)
        self._update_status(f"Retrying {len(failed_ids)} failed KPI(s)...", "blue")
        
        audience_ids = self._audience_ids
        kpi_names = self._kpi_names
        alias = self.alias_var.get().strip()
        
        def retry_in_background():
            from sfi_reporter.data import get_detailed_action_items, is_invalid_eta
            from datetime import datetime
            
            def on_status(msg):
                self._update_status(msg, "blue")
            
            new_rows, still_failed = get_detailed_action_items(
                audience_ids, failed_ids, on_status, kpi_names
            )
            
            # Merge new rows into the existing cached data
            self.root.after(0, lambda: self._on_retry_complete(new_rows, still_failed, alias))
        
        threading.Thread(target=retry_in_background, daemon=True).start()
    
    def _on_retry_complete(self, new_rows: list, still_failed: list, alias: str):
        """Handle retry completion — merge new rows into cached data and re-render."""
        from sfi_reporter.data import is_invalid_eta
        from datetime import datetime
        
        self.refresh_btn.configure(state=tk.NORMAL)
        self.clear_btn.configure(state=tk.NORMAL)
        self.retry_btn.configure(state=tk.NORMAL)
        
        if not new_rows and still_failed:
            # Everything still failed
            self._failed_kpis = still_failed
            names = [f['kpi_name'] for f in still_failed]
            self._update_status(
                f"❌ Retry failed — {len(still_failed)} KPI(s) still failing: {', '.join(names)}",
                "red"
            )
            return
        
        # Read current cache and merge in the new rows
        cached = read_cache(alias)
        if not cached:
            self._update_status("❌ Cache missing — do a full refresh", "red")
            return
        
        existing_items = cached.get('detailed_items', [])
        existing_items.extend(new_rows)
        cached['detailed_items'] = existing_items
        
        # Recompute stats for newly added KPIs
        kpi_stats = cached.get('kpi_stats', {})
        kpi_names = cached.get('kpi_names', self._kpi_names)
        for row in new_rows:
            kpi_id = row.get('_kpi_id', 'Unknown')
            sla_type = row.get('SlaType', '')
            eta_date = row.get('EtaDate')
            if kpi_id not in kpi_stats:
                kpi_stats[kpi_id] = {'name': kpi_names.get(kpi_id, kpi_id), 'count': 0, 'sla': 0, 'invalid_eta': 0}
            kpi_stats[kpi_id]['count'] += 1
            if sla_type == 'OutOfSla':
                kpi_stats[kpi_id]['sla'] += 1
            if is_invalid_eta(eta_date):
                kpi_stats[kpi_id]['invalid_eta'] += 1
        
        cached['kpi_stats'] = kpi_stats
        cached['failed_kpis'] = still_failed
        cached['timestamp'] = datetime.now().isoformat()
        
        write_cache(alias, cached)
        self._update_tables(cached)
        
        self._failed_kpis = still_failed
        self._audience_ids = cached.get('audience_ids', self._audience_ids)
        
        if still_failed:
            self.retry_btn.pack(side=tk.LEFT, padx=5)
            names = [f['kpi_name'] for f in still_failed]
            self._update_status(
                f"✅ Recovered {len(new_rows)} items — ⚠️ {len(still_failed)} KPI(s) still failing: {', '.join(names)}",
                "orange"
            )
        else:
            self.retry_btn.pack_forget()
            self._update_status(
                f"✅ Retry successful — recovered {len(new_rows)} items!", "green"
            )
    
    def _on_clear_cache(self):
        """Handle clear cache button click."""
        alias = self.alias_var.get().strip()
        if alias and clear_cache(alias):
            # Clear tables
            for item in self.services_tree.get_children():
                self.services_tree.delete(item)
            for item in self.action_tree.get_children():
                self.action_tree.delete(item)
            for item in self.program_tree.get_children():
                self.program_tree.delete(item)
            
            self.cache_age_var.set("")
            self._update_status("Cache cleared", "blue")

    def _on_query(self):
        """Open the filter builder window."""
        from sfi_reporter.query_builder import QueryBuilder

        # Always filter against the original unfiltered data
        source = self._unfiltered_data or self.current_data
        action_items = source.get('detailed_items', [])
        program_names = source.get('programs_lookup', {})
        service_names = {
            s.get('Id', ''): s.get('Name', '')
            for s in source.get('services', [])
        }
        is_manager = source.get('is_manager', False)
        service_owners = source.get('service_owners', {})

        QueryBuilder(
            self.root,
            action_items=action_items,
            program_names=program_names,
            service_names=service_names,
            is_manager=is_manager,
            service_owners=service_owners,
            on_apply=self._on_filter_applied,
        )

    def _reapply_last_filter(self):
        """Re-evaluate the last filter clauses against current (refreshed) data."""
        from sfi_reporter.query_builder import evaluate_clauses
        source = self._unfiltered_data or self.current_data
        items = source.get('detailed_items', [])
        if not items:
            return
        filtered = evaluate_clauses(
            items, self._last_filter_clauses,
            include_ussec=self._last_filter_ussec,
        )
        self._on_filter_applied(filtered, self._last_filter_clauses)

    def _on_filter_applied(self, filtered_items: list, clauses: list):
        """Handle filter applied from QueryBuilder — rebuild tables with filtered data."""
        # Remember clauses for re-apply-after-refresh
        self._last_filter_clauses = clauses
        # Grab USSec toggle from the clause cache (saved just before this callback)
        from sfi_reporter.query_builder import load_clause_cache
        _, ussec = load_clause_cache()
        self._last_filter_ussec = ussec

        # No active clauses — restore original unfiltered view
        if not clauses:
            original = self._unfiltered_data or self.current_data
            self.query_btn.configure(text="🔍 Filter")
            self._update_tables(original)
            return

        # Build a filtered copy of the *original* data with the filtered items
        from sfi_reporter.data import is_invalid_eta
        data = dict(self._unfiltered_data or self.current_data)
        data['detailed_items'] = filtered_items

        # Recompute stats from filtered items
        program_names = data.get('programs_lookup', {})
        service_stats = {}
        kpi_stats = {}
        program_stats = {}
        kpi_names = data.get('kpi_names', {})

        for row in filtered_items:
            svc_id = row.get('S360_ServiceId', 'Unknown')
            svc_name = row.get('S360_ServiceTreeServiceName', 'Unknown')
            kpi_id = row.get('_kpi_id', 'Unknown')
            sla_type = row.get('SlaType', '')
            eta_date = row.get('EtaDate')
            pid_list = row.get('S360_ProgramIds') or []

            is_out_of_sla = sla_type == 'OutOfSla'
            is_invalid = is_invalid_eta(eta_date)

            if svc_id not in service_stats:
                service_stats[svc_id] = {'name': svc_name, 'count': 0, 'sla': 0, 'invalid_eta': 0}
            service_stats[svc_id]['count'] += 1
            if is_out_of_sla:
                service_stats[svc_id]['sla'] += 1
            if is_invalid:
                service_stats[svc_id]['invalid_eta'] += 1

            if kpi_id not in kpi_stats:
                kpi_stats[kpi_id] = {'name': kpi_names.get(kpi_id, kpi_id), 'count': 0, 'sla': 0, 'invalid_eta': 0}
            kpi_stats[kpi_id]['count'] += 1
            if is_out_of_sla:
                kpi_stats[kpi_id]['sla'] += 1
            if is_invalid:
                kpi_stats[kpi_id]['invalid_eta'] += 1

            if pid_list:
                pid = pid_list[0]
                pname = program_names.get(pid, 'Other Program')
                if pname not in program_stats:
                    program_stats[pname] = {'count': 0, 'sla': 0, 'invalid_eta': 0, 'id': pid}
                program_stats[pname]['count'] += 1
                if is_out_of_sla:
                    program_stats[pname]['sla'] += 1
                if is_invalid:
                    program_stats[pname]['invalid_eta'] += 1
            else:
                if 'Unassigned' not in program_stats:
                    program_stats['Unassigned'] = {'count': 0, 'sla': 0, 'invalid_eta': 0, 'id': 'unassigned'}
                program_stats['Unassigned']['count'] += 1
                if is_out_of_sla:
                    program_stats['Unassigned']['sla'] += 1
                if is_invalid:
                    program_stats['Unassigned']['invalid_eta'] += 1

        data['service_stats'] = service_stats
        data['kpi_stats'] = kpi_stats
        data['program_stats'] = program_stats

        # Recompute owner stats if manager
        if data.get('is_manager') and service_stats:
            svc_owners = data.get('service_owners', {})
            org_map = data.get('org_mapping', {})
            data['owner_stats'] = aggregate_by_owner(
                filtered_items, svc_owners,
                org_mapping=org_map if org_map else None,
            )

        # Update filter button text to show active filter
        n = len(filtered_items)
        self.query_btn.configure(text=f"🔍 Filter ({n})")

        self._update_tables(data, is_filtered=True)


# ---------------------------------------------------------------------------
# LLM Analysis UI Components
# ---------------------------------------------------------------------------

class AnalysisProgressModal(tk.Toplevel):
    """Modal progress dialog shown while LLM analysis is in flight."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Analyzing...")
        self.geometry("350x120")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Prevent closing while in progress
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 350) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 120) // 2
        self.geometry(f"+{x}+{y}")

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(frame, text="Preparing analysis...", font=("Segoe UI", 10))
        self.status_label.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(frame, mode="indeterminate", length=280)
        self.progress.pack()
        self.progress.start(15)

    def update_status(self, text: str):
        """Update the status label (call from main thread only)."""
        self.status_label.configure(text=text)

    def close(self):
        """Stop progress and destroy."""
        self.progress.stop()
        self.grab_release()
        self.destroy()


class AnalysisModal(tk.Toplevel):
    """Modal dialog displaying the LLM analysis result."""

    def __init__(self, parent, result: AnalysisResult):
        super().__init__(parent)

        title_text = result.title[:60] + "..." if len(result.title) > 60 else result.title
        self.title(f"LLM Analysis: {title_text}")
        self.geometry("800x650")
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 800) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 650) // 2
        self.geometry(f"+{x}+{y}")

        self._result = result
        self._create_widgets()

        self.bind("<Escape>", lambda e: self.destroy())
        self.focus_set()

    def _create_widgets(self):
        """Build the analysis display."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollable text widget
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        y_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self.text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            yscrollcommand=y_scroll.set,
            padx=12,
            pady=8,
        )
        y_scroll.configure(command=self.text.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure tags
        self.text.tag_configure("header", font=("Segoe UI", 13, "bold"), spacing1=12, spacing3=4)
        self.text.tag_configure("section", font=("Segoe UI", 10), lmargin1=10, lmargin2=10)
        self.text.tag_configure("disclaimer", font=("Segoe UI", 8, "italic"), foreground="#888888")
        self.text.tag_configure("meta", font=("Segoe UI", 8), foreground="#666666")

        r = self._result

        sections = [
            ("\U0001f3af Mission", r.mission or "(No mission section parsed)"),
            ("\u2705 Steps to Done", r.steps_to_done or "(No steps section parsed)"),
            ("\U0001f527 Resources Needing Repair", r.resources or "(No resources section parsed)"),
            ("\u26a0\ufe0f Risk of Delay", r.risk_of_delay or "(No risk section parsed)"),
        ]

        for heading, body in sections:
            self.text.insert(tk.END, f"{heading}\n", "header")
            self.text.insert(tk.END, f"{body}\n\n", "section")

        # Separator
        self.text.insert(tk.END, "\n" + "\u2500" * 60 + "\n\n", "meta")

        # Metadata footer
        ts = r.timestamp[:19].replace("T", " ") if r.timestamp else "unknown"
        meta = f"Model: {r.model}  |  Analyzed: {ts} UTC  |  Tokens: {r.prompt_tokens} in / {r.completion_tokens} out"
        self.text.insert(tk.END, meta + "\n", "meta")
        self.text.insert(tk.END, "\nAI-generated analysis \u2014 verify before acting.\n", "disclaimer")

        self.text.configure(state=tk.DISABLED)

        # Button bar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="\U0001f4cb Copy to Clipboard", command=self._copy_to_clipboard).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)

    def _copy_to_clipboard(self):
        """Copy the full analysis text to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(self._result.analysis_text)
        # Brief flash feedback
        original = self.title()
        self.title("Copied to clipboard!")
        self.after(1500, lambda: self.title(original))


def _launch_llm_analysis(parent, item: dict):
    """Launch LLM analysis for an action item (shared by KPI tree and DrillDownModal).

    Args:
        parent: The parent tkinter widget (for modal positioning).
        item: The action item data dict.
    """
    # Validate config before spawning thread
    try:
        config = _load_llm_config()
    except LLMConfigError as e:
        messagebox.showerror("LLM Configuration Required", str(e), parent=parent)
        return

    # Get the root window for after() calls
    root = parent.winfo_toplevel()

    progress = AnalysisProgressModal(parent)

    def do_analysis():
        try:
            root.after(0, lambda: progress.update_status("Fetching URL context..."))
            url_content = fetch_action_item_urls(item)

            root.after(0, lambda: progress.update_status("Calling Azure OpenAI..."))
            result = analyze_item(item, config, url_content=url_content or None)

            root.after(0, lambda: progress.update_status("Saving result..."))
            try:
                save_analysis(result)
            except OSError as e:
                logger.warning("Failed to save analysis: %s", e)

            root.after(0, lambda: _on_analysis_complete(root, progress, result))

        except LLMError as e:
            msg = str(e)
            root.after(0, lambda m=msg: _on_analysis_error(root, progress, m))
        except Exception as e:
            msg = f"Unexpected error: {e}"
            logger.error("Unexpected error during LLM analysis: %s", e)
            root.after(0, lambda m=msg: _on_analysis_error(root, progress, m))

    threading.Thread(target=do_analysis, daemon=True).start()


def _on_analysis_complete(root, progress: AnalysisProgressModal, result: AnalysisResult):
    """Handle successful analysis completion (main thread)."""
    progress.close()
    AnalysisModal(root, result)


def _on_analysis_error(root, progress: AnalysisProgressModal, error_msg: str):
    """Handle analysis error (main thread)."""
    progress.close()
    messagebox.showerror("LLM Analysis Failed", error_msg, parent=root)


def main():
    """Main entry point."""
    setup_logging()
    patch_subprocess_windows()
    logger.info("SFI Reporter starting — log file: %s", get_log_path())

    root = tk.Tk()
    
    # Set theme
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    
    app = SFIReporterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
