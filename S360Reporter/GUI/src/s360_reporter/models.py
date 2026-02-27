"""Data types, constants, and column utilities for S360Reporter."""
import json
import re
import tkinter as tk
from typing import NamedTuple


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

class OrgAncestry(NamedTuple):
    """Mapping of a service owner to their hierarchical ancestry path.

    path: Tuple of manager display names from root down.
        - Root (viewer) IS always path[0]
        - Path is NEVER empty for found owners
        - IC names never appear in path — only managers
        - ("Unknown Owner",) for owners not found in tree
    """
    path: tuple[str, ...]


# ---------------------------------------------------------------------------
# Regex patterns for URL extraction
# ---------------------------------------------------------------------------

# Allow single quotes in URLs (common in query params) but not at the very end
# Also allow parentheses which are common in S360 lens URLs
URL_PATTERN = re.compile(r'https?://[^\s<>"]+(?<![\'"])')
HTML_ANCHOR_PATTERN = re.compile(
    r'<a[^>]+href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>', re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Column toggle constants
# ---------------------------------------------------------------------------

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
    'eta_date': 90, 'assigned_to': 90, 'action_owner': 120,
}

# Column anchors for treeview
COLUMN_ANCHORS = {
    'title': tk.W, 'service': tk.W, 'sla': tk.CENTER,
    'due_date': tk.CENTER, 'eta_date': tk.CENTER,
    'assigned_to': tk.W, 'action_owner': tk.W,
}

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


# ---------------------------------------------------------------------------
# Display resolvers
# ---------------------------------------------------------------------------

def _resolve_sla_display(sla_type) -> str:
    """Map any SlaType value (int, str, None) to a human-readable label."""
    if sla_type is None:
        return ""
    return _SLA_DISPLAY_MAP.get(sla_type, "")


def _resolve_eta_status(eta_status) -> str:
    """Return ETA Status string, defaulting to '' for None."""
    return eta_status if eta_status else ""


# ---------------------------------------------------------------------------
# Column management utilities
# ---------------------------------------------------------------------------

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
    """Filter item to only visible columns."""
    return {k: v for k, v in item.items() if k in visible}


def select_all_columns(available: list[str]) -> list[str]:
    """Return all available columns."""
    return list(available)


def clear_all_columns(available: list[str]) -> list[str]:
    """Return only required columns."""
    return [c for c in REQUIRED_COLUMNS if c in available]


def validate_visible_columns(visible: list[str]) -> list[str]:
    """Ensure required columns are always present."""
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


__all__ = [
    # Types
    'OrgAncestry',
    # Regex
    'URL_PATTERN',
    'HTML_ANCHOR_PATTERN',
    # Constants
    'REQUIRED_COLUMNS',
    'COLUMN_DISPLAY_NAMES',
    'SLA_STATUS_MAP',
    '_SLA_DISPLAY_MAP',
    'COLUMN_ID_MAP',
    'COLUMN_WIDTHS',
    'COLUMN_ANCHORS',
    'FIELD_GROUPS',
    # Resolvers
    '_resolve_sla_display',
    '_resolve_eta_status',
    # Column utilities
    'get_available_columns',
    'filter_item_columns',
    'select_all_columns',
    'clear_all_columns',
    'validate_visible_columns',
    'get_empty_columns',
]
