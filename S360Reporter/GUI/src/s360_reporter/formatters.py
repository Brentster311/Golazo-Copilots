"""Text formatting, URL extraction, and field grouping utilities."""
import json
import re

from s360_reporter.models import (
    FIELD_GROUPS,
    HTML_ANCHOR_PATTERN,
    URL_PATTERN,
)


def format_field_label(field_name: str) -> str:
    """Convert field name to human-readable label.

    Examples:
        serviceTreeId -> Service Tree Id
        S360_AssignedTo -> S360 Assigned To
        _kpi_id -> Kpi Id
    """
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


def group_item_fields(item: dict) -> dict:
    """Group item fields into logical categories.

    Returns dict with keys: identity, status, dates, ownership,
    service_program, subscription, resources, other.
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


__all__ = [
    'format_field_label',
    'format_field_value',
    'extract_urls_from_text',
    'clean_html_from_title',
    'parse_resource_uris',
    'group_item_fields',
]
