"""Data module for SFI Reporter.

Provides functions to interact with Services 360 API via accia-s360.
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from threading import Lock
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from accia_s360 import S360Client
except ImportError:
    S360Client = None  # type: ignore

# Max concurrent workers for parallel KPI fetching
MAX_KPI_WORKERS = 25

# Essential columns that must always be requested
ESSENTIAL_COLUMNS = ['S360_ProgramIds', 'url', 'id']

# Lock for thread-safe column cache access
_column_cache_lock = Lock()


def get_column_cache_path() -> str:
    """Get the path to the column metadata cache file.
    
    Returns:
        Absolute path to column_metadata.json in $TEMP/sfireporter/
    """
    cache_dir = os.path.join(os.environ.get('TEMP', '/tmp'), 'sfireporter')
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, 'column_metadata.json')


def load_column_cache() -> dict:
    """Load the column metadata cache from disk.
    
    Returns:
        Cache dictionary with 'version' and 'kpis' keys.
        Returns empty cache if file doesn't exist or is corrupt.
    """
    path = get_column_cache_path()
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                # Validate structure
                if isinstance(cache, dict) and 'version' in cache and 'kpis' in cache:
                    return cache
    except (json.JSONDecodeError, IOError):
        pass
    return {"version": 1, "kpis": {}}


def save_column_cache(cache: dict) -> None:
    """Save the column metadata cache to disk atomically.
    
    Uses temp file + rename for atomic write (thread-safe).
    
    Args:
        cache: The cache dictionary to save.
    """
    path = get_column_cache_path()
    temp_path = path + '.tmp'
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
        os.replace(temp_path, path)  # Atomic on Windows & POSIX
    except IOError as e:
        logger.error("Error saving column cache: %s", e)


def get_cached_columns(kpi_id: str) -> Optional[list[str]]:
    """Get cached columns for a KPI.
    
    Args:
        kpi_id: The KPI ID to look up.
        
    Returns:
        List of column names or None if not cached.
    """
    with _column_cache_lock:
        cache = load_column_cache()
        kpi_entry = cache.get("kpis", {}).get(kpi_id)
        if kpi_entry:
            return kpi_entry.get("columns")
    return None


def cache_kpi_columns(kpi_id: str, columns: list[str]) -> None:
    """Cache the columns for a KPI.
    
    Args:
        kpi_id: The KPI ID.
        columns: List of column names to cache.
    """
    with _column_cache_lock:
        cache = load_column_cache()
        cache["kpis"][kpi_id] = {
            "columns": columns,
            "discovered_at": datetime.now(timezone.utc).isoformat()
        }
        save_column_cache(cache)
        logger.debug("Cached %d columns for KPI %s", len(columns), kpi_id)


def merge_columns_with_essentials(columns: list[str]) -> list[str]:
    """Merge discovered columns with essential columns.
    
    Ensures S360_ProgramIds and url are always included.
    
    Args:
        columns: List of discovered columns.
        
    Returns:
        List with essential columns guaranteed to be included.
    """
    result = list(columns)
    for essential in ESSENTIAL_COLUMNS:
        if essential not in result:
            result.append(essential)
    return result


_client_instance: Any = None


def get_client() -> Any:
    """Get a shared S360Client instance (singleton).
    
    The client is thread-safe for read operations and reuses
    a single AzureCliCredential so tokens are cached rather
    than re-acquired on every API call.
    
    Returns:
        S360Client instance.
        
    Raises:
        ImportError: If accia-s360 is not installed.
    """
    global _client_instance
    if S360Client is None:
        raise ImportError("accia-s360 package is not installed")
    if _client_instance is None:
        _client_instance = S360Client()
    return _client_instance


def get_current_user_alias() -> Optional[str]:
    """Get the current user's alias from Azure CLI credentials.
    
    Returns:
        User alias or None if unavailable.
    """
    try:
        client = get_client()
        user = client.get_current_user()
        if user and hasattr(user, 'alias'):
            return user.alias
        return None
    except Exception:
        return None


def get_user_team_info(user_alias: str) -> tuple[list[dict], list[str]]:
    """Get services and audience IDs for a user.
    
    This looks up the user's TeamGroup and hierarchy to get all relevant audience IDs
    for fetching action items (not just owned services).
    
    Args:
        user_alias: The user's alias.
        
    Returns:
        Tuple of (services list, audience_ids list).
    """
    try:
        client = get_client()
        
        # First try to get services from default landing view
        response = client.get_default_landing_view(user_alias)
        services = []
        if response and 'SearchDataList' in response:
            services = [
                item for item in response['SearchDataList']
                if item.get('Group') == 'Service'
            ]
        
        # If user owns services, use those service IDs as audience
        if services:
            audience_ids = [s.get('Id') for s in services if s.get('Id')]
            return services, audience_ids
        
        # Otherwise, search for user's TeamGroup
        search_results = client.search(user_alias)
        
        # Find TeamGroup for this user
        team_group = None
        for result in search_results:
            if result.get('Group') == 'TeamGroup' and user_alias.lower() in result.get('Name', '').lower():
                team_group = result
                break
        
        if not team_group:
            # No TeamGroup found, return empty
            return [], []
        
        team_group_id = team_group.get('Id')
        
        # Query people hierarchy to get team ID
        hierarchy = client._extended.query_people_hierarchy([team_group_id])
        nodes = hierarchy.get('PeopleHierarchyNodes', [])
        
        # Build audience from TeamGroup ID + team IDs
        audience_ids = [team_group_id]
        for node in nodes:
            team_id = node.get('TeamId')
            if team_id:
                audience_ids.append(team_id)
        
        # Return empty services list but with audience IDs
        return [], audience_ids
        
    except Exception as e:
        logger.error("Error in get_user_team_info: %s", e, exc_info=True)
        return [], []


def get_user_services(user_alias: str) -> list[dict]:
    """Get services owned by a user.
    
    Args:
        user_alias: The user's alias.
        
    Returns:
        List of service dictionaries.
    """
    try:
        client = get_client()
        response = client.get_default_landing_view(user_alias)
        
        if not response or 'SearchDataList' not in response:
            return []
        
        # Filter to services
        services = [
            item for item in response['SearchDataList']
            if item.get('Group') == 'Service'
        ]
        return services
    except Exception:
        return []


def get_action_items_summary(service_ids: list[str]) -> Optional[dict]:
    """Get action items summary for given services.
    
    Args:
        service_ids: List of service IDs.
        
    Returns:
        Action items summary or None/empty dict on error.
    """
    if not service_ids:
        return {}
    
    try:
        client = get_client()
        logger.info("Fetching action items for %d services: %s...", len(service_ids), service_ids[:3])
        result = client.get_action_items_summary(service_ids)
        logger.debug("Action items result keys: %s", list(result.keys()) if isinstance(result, dict) else type(result))
        return result
    except TimeoutError:
        logger.error("Timeout fetching action items")
        return {}
    except Exception as e:
        logger.error("Error fetching action items: %s", e, exc_info=True)
        return None


def get_all_columns(service_ids: list[str], kpi_id: str) -> list[str]:
    """Fetch all available column names from the S360 API.
    
    Makes a single grid request to get the AllColumns metadata.
    
    Args:
        service_ids: List of service IDs for the audience.
        kpi_id: A KPI ID to use for the query.
        
    Returns:
        List of all available column names.
    """
    try:
        client = get_client()
        grid = client.get_action_items_grid(
            kpi_id=kpi_id,
            audience=service_ids,
            sla_type_filter=3,
            columns=[],  # Empty to get AllColumns metadata
        )
        return grid.get("AllColumns", [])
    except Exception as e:
        logger.error("Error fetching AllColumns: %s", e, exc_info=True)
        return []


# Curated list of most useful columns to request
# The API returns HTTP 500 if we request too many columns at once
# So we request a subset that covers the main use cases
REQUESTED_COLUMNS = [
    # Essential for app features
    'S360_ProgramIds',       # Program summary
    'url',                   # Hyperlinks
    'ActionWikiLink',        # Wiki links
    
    # Identity
    'id',
    'title',
    'S360_ActionItemId',
    
    # Service/Assignment
    'S360_ServiceTreeServiceName',
    'S360_ServiceId',
    'S360_AssignedToName',
    'ActionOwnerName',
    'ActionOwnerAlias',
    
    # Dates
    'dueDate',
    'EtaDate',
    'EtaStatus',
    'createdDate',
    'closedDate',
    
    # Status
    'SlaType',
    'ActionItemStatus',
    
    # Hierarchy
    'S360_ServiceTreeDivisionName',
    'S360_ServiceTreeGroupName',
    'S360_ServiceTreeOrganizationName',
    
    # Cloud/Environment
    'Clouds',
    'Environments',
    
    # Assets
    'AssetType0',
    'AssetType1',
    'AssetType2',
    'AssetTypeLink0',
    'AssetTypeLink1',
    'AssetTypeLink2',
    
    # Custom grouping
    'CustomGroupingLink',
    
    # Exception/Remediation
    'Remediation',
    
    # Waves
    'S360_WavesMetadata',
]


def get_detailed_action_items(service_ids: list[str], kpi_ids: list[str], on_status: Optional[callable] = None, kpi_names: Optional[dict] = None) -> tuple[list[dict], list[dict]]:
    """Get detailed action items grid data for calculating Invalid ETA and program stats.
    
    Uses per-KPI column discovery with caching:
    - On cache hit: Single API call with cached columns
    - On cache miss: Discovery call + data call, then cache columns for next time
    
    Args:
        service_ids: List of service IDs.
        kpi_ids: List of KPI IDs to fetch.
        on_status: Optional callback for progress updates.
        kpi_names: Optional dict mapping KPI ID to KPI name for status messages.
        
    Returns:
        Tuple of (rows, failed_kpis) where rows is a list of action item dicts
        and failed_kpis is a list of {"kpi_id", "kpi_name", "error"} dicts.
    """
    if not service_ids or not kpi_ids:
        return [], []
    
    kpi_names = kpi_names or {}
    total = len(kpi_ids)
    
    # Thread-safe progress tracking
    completed_count = [0]  # Using list for mutable in closure
    failed_kpis: list[dict] = []  # Track KPIs that fail during fetch
    status_lock = Lock()
    
    def fetch_kpi_grid(kpi_id: str) -> list[dict]:
        """Fetch grid data for a single KPI with column cache."""
        try:
            client = get_client()
            
            # Check cache for this KPI's columns
            cached_columns = get_cached_columns(kpi_id)
            
            if cached_columns:
                # Cache hit - single API call
                columns_to_use = merge_columns_with_essentials(cached_columns)
                logger.debug("Using %d cached columns for KPI %s", len(columns_to_use), kpi_id)
            else:
                # Cache miss - discovery required
                # First call: get default columns from response
                discovery_grid = client.get_action_items_grid(
                    kpi_id=kpi_id,
                    audience=service_ids,
                    sla_type_filter=3,
                    columns=[],  # Empty to get default Columns
                )
                
                # Get the KPI's configured default columns (NOT AllColumns which causes HTTP 500)
                # Columns is a list of objects with 'Identifier' field
                columns_raw = discovery_grid.get("Columns", [])
                
                if columns_raw and isinstance(columns_raw[0], dict):
                    # Extract identifiers from column objects
                    discovered_columns = [col.get("Identifier") for col in columns_raw if col.get("Identifier")]
                else:
                    # Already a list of strings (shouldn't happen but handle it)
                    discovered_columns = columns_raw
                
                if not discovered_columns:
                    # Fallback to curated list if no columns discovered
                    logger.warning("No columns discovered for KPI %s, using fallback", kpi_id)
                    discovered_columns = REQUESTED_COLUMNS
                
                # Cache for next time
                cache_kpi_columns(kpi_id, discovered_columns)
                columns_to_use = merge_columns_with_essentials(discovered_columns)
            
            # Fetch data with the columns
            grid = client.get_action_items_grid(
                kpi_id=kpi_id,
                audience=service_ids,
                sla_type_filter=3,
                columns=columns_to_use,
            )
            
            rows = grid.get("Rows", [])
            for row in rows:
                row['_kpi_id'] = kpi_id  # Tag with KPI for reference
            
            # Thread-safe status update
            if on_status:
                with status_lock:
                    completed_count[0] += 1
                    on_status(f"Fetching KPIs: {completed_count[0]}/{total} complete")
            
            return rows
        except Exception as e:
            logger.error("Error fetching grid for KPI %s: %s", kpi_id, e)
            # Record the failure
            with status_lock:
                failed_kpis.append({
                    "kpi_id": kpi_id,
                    "kpi_name": kpi_names.get(kpi_id, kpi_id),
                    "error": str(e),
                })
                completed_count[0] += 1
                if on_status:
                    on_status(f"Fetching KPIs: {completed_count[0]}/{total} complete")
            return []
    
    try:
        if on_status:
            on_status(f"Fetching {total} KPIs in parallel...")
        
        all_rows = []
        
        # Use ThreadPoolExecutor for parallel I/O-bound fetching
        with ThreadPoolExecutor(max_workers=min(MAX_KPI_WORKERS, total)) as executor:
            # Submit all KPI fetch tasks
            futures = {executor.submit(fetch_kpi_grid, kpi_id): kpi_id for kpi_id in kpi_ids}
            
            # Collect results as they complete
            for future in as_completed(futures):
                rows = future.result()
                all_rows.extend(rows)
        
        if failed_kpis:
            names = [f.get('kpi_name', f.get('kpi_id')) for f in failed_kpis]
            logger.warning("%d KPI(s) failed: %s", len(failed_kpis), names)
        
        return all_rows, failed_kpis
    except Exception as e:
        logger.error("Error in get_detailed_action_items: %s", e, exc_info=True)
        return [], failed_kpis


def is_invalid_eta(eta_date: Optional[str]) -> bool:
    """Check if an ETA is invalid (empty or in the past).
    
    Args:
        eta_date: ETA date string in ISO format.
        
    Returns:
        True if invalid (empty or past), False otherwise.
    """
    if not eta_date:
        return True
    
    try:
        eta = datetime.fromisoformat(eta_date.replace('Z', '+00:00'))
        now = datetime.now(eta.tzinfo) if eta.tzinfo else datetime.now()
        return eta < now
    except (ValueError, TypeError):
        return True


def get_all_programs() -> dict[str, str]:
    """Get all programs and build a program ID to name lookup.
    
    Fetches from the v2/Programs API which returns all available programs
    with their metadata.
    
    Returns:
        Dict mapping program ID to program display name.
    """
    try:
        client = get_client()
        result = client.get_programs()  # Get all programs
        
        program_names = {}
        programs = result.get('Programs', [])
        
        for program in programs:
            # Each program has ProgramId and DisplayName at top level
            pid = program.get('ProgramId')
            display_name = program.get('DisplayName')
            if pid and display_name:
                program_names[pid] = display_name
                
        logger.info("Loaded %d programs from API", len(program_names))
        return program_names
    except Exception as e:
        logger.error("Error fetching programs: %s", e, exc_info=True)
        return {}


def fetch_full_data(user_alias: str) -> dict:
    """Fetch all data for a user and return with timestamp.
    
    Args:
        user_alias: The user's alias.
        
    Returns:
        Dictionary with services, action_items, and timestamp.
    """
    services = get_user_services(user_alias)
    service_ids = [s.get('Id') for s in services if s.get('Id')]
    
    action_items = get_action_items_summary(service_ids) or {}
    
    return {
        'services': services,
        'action_items': action_items,
        'timestamp': datetime.now().isoformat(),
    }
