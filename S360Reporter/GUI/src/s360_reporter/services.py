"""Business logic: serialization, settings, org mapping, aggregation, data refresh, and filters."""
import json
import logging
from datetime import datetime
from typing import Optional

from s360_reporter.cache import (
    clear_cache,
    get_cache_age_minutes,
    get_cache_dir,
    is_cache_valid,
    read_cache,
    write_cache,
)
from s360_reporter.models import OrgAncestry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Serialization helpers (cache ↔ OrgAncestry)
# ---------------------------------------------------------------------------

def _serialize_org_data_for_cache(data: dict) -> dict:
    """Convert OrgAncestry values and tuple keys to JSON-safe primitives."""
    out = dict(data)
    # org_mapping: {owner: OrgAncestry(path=...)} → {owner: [path_elements...]}
    om = out.get('org_mapping')
    if om and isinstance(om, dict):
        out['org_mapping'] = {
            k: (list(v.path) if isinstance(v, OrgAncestry) else
                list(v) if isinstance(v, tuple) else v)
            for k, v in om.items()
        }
    # Remove deprecated level2_stats key if present
    out.pop('level2_stats', None)
    return out


def _deserialize_org_data_from_cache(data: dict) -> dict:
    """Restore OrgAncestry values and tuple keys from JSON-safe primitives."""
    om = data.get('org_mapping')
    if om and isinstance(om, dict):
        restored = {}
        for k, v in om.items():
            if isinstance(v, (list, tuple)):
                restored[k] = OrgAncestry(path=tuple(v))
            elif isinstance(v, str):
                restored[k] = v  # legacy string mapping
            else:
                restored[k] = v
        data['org_mapping'] = restored
    # Remove deprecated level2_stats from old caches
    data.pop('level2_stats', None)
    return data


# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Manager / owner detection
# ---------------------------------------------------------------------------

def is_manager_view(landing_view: list) -> bool:
    """Detect if the user is a manager based on their landing view.

    Managers have a TeamGroup in their landing view, while ICs have
    individual Service entries.
    """
    if not landing_view:
        return False
    return any(item.get('Group') == 'TeamGroup' for item in landing_view)


def parse_owners_field(owners_json: str | None) -> list[str]:
    """Parse the Owners field from S360 search results.

    The Owners field is a JSON-encoded string like '["John Doe","Jane Smith"]'.
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


# ---------------------------------------------------------------------------
# Org tree mapping
# ---------------------------------------------------------------------------

def get_org_mapping(
    owner_names: list[str],
    manager_alias: str,
    on_status: Optional[callable] = None,
) -> dict[str, OrgAncestry]:
    """Map service owners to their hierarchical ancestry path via org tree.

    Uses a single ``get_org_tree(manager_alias)`` call and walks the tree to
    find each owner by display name (case-insensitive).

    Path semantics:
    - Root (viewer) IS always path[0]
    - Path is NEVER empty for found owners
    - IC names never appear — only managers (persons with direct_reports)
    - ("Unknown Owner",) for owners not found in tree
    """
    from s360_reporter.data import get_client

    if not owner_names:
        return {}

    if on_status:
        on_status(f"Fetching org tree for {manager_alias}...")

    cache_key = manager_alias.lower()
    client = get_client()
    try:
        tree = client.get_org_tree(cache_key)
    except Exception:
        # If tree fetch fails, all owners are unknown
        return {name: OrgAncestry(path=('Unknown Owner',)) for name in owner_names}

    # Flatten the org tree into a lookup: display_name_lower → manager path
    name_lookup: dict[str, tuple[str, ...]] = {}

    def _walk(node, parent_path: tuple[str, ...]):
        """Recursively walk tree, building name → path mapping.

        A person is a "manager" if they have direct_reports.
        Managers extend the path; ICs inherit their parent's path.
        """
        person = node.person
        is_manager_node = bool(node.direct_reports)

        if is_manager_node:
            current_path = parent_path + (person.display_name,)
        else:
            current_path = parent_path  # ICs inherit parent path

        name_lookup[person.display_name.lower()] = current_path

        for child in node.direct_reports:
            _walk(child, current_path)

    _walk(tree, ())

    if on_status:
        on_status(f"Mapping {len(owner_names)} owners...")

    # Build result mapping
    result: dict[str, OrgAncestry] = {}
    for owner_name in owner_names:
        path = name_lookup.get(owner_name.lower())
        if path:
            result[owner_name] = OrgAncestry(path=path)
        else:
            result[owner_name] = OrgAncestry(path=('Unknown Owner',))

    return result


# ---------------------------------------------------------------------------
# Direct reports & aggregation
# ---------------------------------------------------------------------------

def extract_direct_reports(service_owners: dict[str, list[str]], manager_name: Optional[str] = None) -> set[str]:
    """Extract direct report names from service_owners dict.

    Direct reports are identified ONLY by team entries like "Gowri Bhaskara's Team".
    """
    directs = set()

    # Extract from "X's Team" patterns
    for service_name in service_owners.keys():
        if "'s Team" in service_name:
            name = service_name.replace("'s Team", "")
            directs.add(name)

    # Add manager if provided
    if manager_name:
        directs.add(manager_name)

    return directs


def aggregate_by_owner(
    items: list[dict],
    service_owners: dict[str, list[str]],
    org_mapping: Optional[dict] = None,
    allowed_owners: Optional[set[str]] = None,
) -> dict:
    """Aggregate action item stats by service owner (level-1 rollup).

    When org_mapping is provided, each owner is mapped to their level-1 ancestor.
    Supports both legacy string mappings and OrgAncestry tuple mappings.
    """
    from s360_reporter.data import is_invalid_eta

    def _get_level1(mapped) -> str:
        """Extract top-level group name from OrgAncestry or legacy string."""
        if isinstance(mapped, OrgAncestry):
            path = mapped.path
            if len(path) > 1:
                return path[1]  # Direct report of root
            return path[0]  # Root itself or unknown
        return mapped  # Legacy string

    owner_stats: dict[str, dict] = {}

    for item in items:
        service_name = item.get('S360_ServiceTreeServiceName', '')
        owners = service_owners.get(service_name, None)

        # Handle missing or empty owners
        if owners is None or len(owners) == 0:
            owners = ['No Owner in ST']

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


def collect_services_for_owner(
    path_prefix: tuple[str, ...],
    service_owners: dict[str, list[str]],
    org_mapping: dict,
) -> set[str]:
    """Collect all service names whose owner's ancestry path starts with path_prefix.

    Used for drill-down: clicking a group node collects all services in its subtree.
    """
    matching_owners: set[str] = set()

    for raw_owner, mapped in org_mapping.items():
        if isinstance(mapped, OrgAncestry):
            if mapped.path[:len(path_prefix)] == path_prefix:
                matching_owners.add(raw_owner)
        else:
            # Legacy string mapping — match if string equals last element of prefix
            if len(path_prefix) == 1 and mapped == path_prefix[0]:
                matching_owners.add(raw_owner)

    # Collect services owned by any matching owner
    result: set[str] = set()
    for svc_name, owners in service_owners.items():
        if any(o in matching_owners for o in owners):
            result.add(svc_name)

    return result


# ---------------------------------------------------------------------------
# Service owner lookup
# ---------------------------------------------------------------------------

def get_service_owners(
    service_names: list[str],
    on_status: Optional[callable] = None,
) -> dict[str, list[str]]:
    """Fetch owners for each service using S360 search API in parallel."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from s360_reporter.data import get_client

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


# ---------------------------------------------------------------------------
# Main data refresh
# ---------------------------------------------------------------------------

def do_refresh(user_alias: str, on_status: Optional[callable] = None) -> Optional[dict]:
    """Fetch fresh data and write to cache with status updates.

    All stats are computed from detailed action items for consistency.
    """
    try:
        from s360_reporter.data import (
            get_user_team_info,
            get_action_items_summary,
            get_detailed_action_items,
            is_invalid_eta,
            get_all_programs,
            get_client,
        )
        from datetime import datetime

        if on_status:
            on_status("Connecting to S360...")

        # Detect manager status via Graph API (has direct reports?)
        client = get_client()
        try:
            direct_reports = client.get_direct_reports(user_alias)
            is_manager = len(direct_reports) > 0
        except Exception:
            logger.warning("Graph direct-reports lookup failed for %s; assuming IC", user_alias)
            direct_reports = []
            is_manager = False

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
            on_status(f"\u26a0\ufe0f {len(failed_kpis)} KPI(s) failed: {', '.join(names)}")

        if on_status:
            on_status(f"Processing {len(detailed_items)} action items...")

        # Build service/kpi/program stats from detailed items
        service_stats = {}
        kpi_stats = {}
        program_stats = {}

        for row in detailed_items:
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
            if program_ids:
                pid = program_ids[0]
                program_name = program_names.get(pid)
                if not program_name:
                    program_name = 'Other Program'
                if program_name not in program_stats:
                    program_stats[program_name] = {'count': 0, 'sla': 0, 'invalid_eta': 0, 'id': pid}
                program_stats[program_name]['count'] += 1
                if is_out_of_sla:
                    program_stats[program_name]['sla'] += 1
                if is_invalid:
                    program_stats[program_name]['invalid_eta'] += 1
            else:
                if 'Unassigned' not in program_stats:
                    program_stats['Unassigned'] = {'count': 0, 'sla': 0, 'invalid_eta': 0, 'id': 'unassigned'}
                program_stats['Unassigned']['count'] += 1
                if is_out_of_sla:
                    program_stats['Unassigned']['sla'] += 1
                if is_invalid:
                    program_stats['Unassigned']['invalid_eta'] += 1

        # If manager view, fetch service owners and aggregate stats by owner
        owner_stats = {}
        service_owners_map = {}
        org_mapping = {}
        if is_manager and service_stats:
            # The viewer IS the manager — alias is already known
            manager_alias_val = user_alias.lower()

            service_names_list = [stats.get('name') for stats in service_stats.values() if stats.get('name')]
            unique_names = list(set(service_names_list))

            if unique_names:
                #retrieve service owners for all services in parallel
                service_owners_map = get_service_owners(unique_names, on_status)

                all_owners = set()
                for owners in service_owners_map.values():
                    all_owners.update(owners)

                if manager_alias_val and all_owners:
                    org_mapping = get_org_mapping(
                        list(all_owners), manager_alias_val, on_status,
                    )

                owner_stats = aggregate_by_owner(
                    detailed_items, service_owners_map,
                    org_mapping=org_mapping if org_mapping else None,
                )

        if on_status:
            on_status("Saving to cache...")

        data = {
            'services': services,
            'detailed_items': detailed_items,
            'service_stats': service_stats,
            'program_stats': program_stats,
            'kpi_stats': kpi_stats,
            'owner_stats': owner_stats,
            'is_manager': is_manager,
            'service_owners': service_owners_map,
            'org_mapping': org_mapping,
            'programs_lookup': program_names,
            'failed_kpis': failed_kpis,
            'audience_ids': audience_ids,
            'kpi_names': kpi_names,
            'timestamp': datetime.now().isoformat(),
        }

        write_cache(user_alias, _serialize_org_data_for_cache(data))
        return data
    except Exception as e:
        logger.exception("Error fetching data for user")
        if on_status:
            on_status(f"Error: {e}")
        return None


# ---------------------------------------------------------------------------
# Filter helpers for drill-down
# ---------------------------------------------------------------------------

def filter_items_by_service(items: list, service_id: str) -> list:
    """Filter items by service ID (S360_ServiceId or serviceTreeId)."""
    return [
        item for item in items
        if item.get('S360_ServiceId') == service_id or item.get('serviceTreeId') == service_id
    ]


def filter_items_by_program(items: list, program_id: str) -> list:
    """Filter items by program ID (checks if program is in S360_ProgramIds list)."""
    return [item for item in items if program_id in (item.get('S360_ProgramIds') or [])]


def filter_items_by_id(items: list, item_id: str) -> list:
    """Filter to get a single item by its ID."""
    return [item for item in items if item.get('id') == item_id]


__all__ = [
    # Serialization
    '_serialize_org_data_for_cache',
    '_deserialize_org_data_from_cache',
    # Settings
    'SETTINGS_FILENAME',
    '_load_setting',
    '_save_setting',
    # Manager/owner
    'is_manager_view',
    'parse_owners_field',
    # Org mapping
    'get_org_mapping',
    'extract_direct_reports',
    'aggregate_by_owner',
    'collect_services_for_owner',
    'get_service_owners',
    # Refresh
    'do_refresh',
    # Filters
    'filter_items_by_service',
    'filter_items_by_program',
    'filter_items_by_id',
]
