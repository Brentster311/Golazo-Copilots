"""ETA logic for proposing dates, filtering items, and building update payloads.

All pure functions — no I/O, no side effects, easy to test.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from accia_s360.models import EtaUpdate

logger = logging.getLogger(__name__)


def propose_eta(due_date_str: Optional[str] = None) -> str:
    """Propose an ETA date: end of month, at least 2 weeks from today.

    If *due_date_str* is provided and later than 2 weeks from today,
    use that month's end instead.

    Args:
        due_date_str: Optional due-date string in ISO format (``YYYY-MM-DD`` or
            ``YYYY-MM-DDThh:mm:ss``).

    Returns:
        Proposed ETA as ``YYYY-MM-DD`` string.
    """
    today = date.today()
    two_weeks = today + timedelta(weeks=2)

    baseline = two_weeks

    if due_date_str and due_date_str.strip() and due_date_str != "N/A":
        try:
            due_date = datetime.strptime(due_date_str.split("T")[0], "%Y-%m-%d").date()
            if due_date > two_weeks:
                baseline = due_date
        except (ValueError, AttributeError):
            pass

    # End of month containing *baseline*
    if baseline.month == 12:
        next_month_first = date(baseline.year + 1, 1, 1)
    else:
        next_month_first = date(baseline.year, baseline.month + 1, 1)

    end_of_month = next_month_first - timedelta(days=1)
    return end_of_month.strftime("%Y-%m-%d")


def get_items_needing_eta_update(items: list[dict]) -> list[dict]:
    """Return items whose ETA is missing or in the past.

    Uses the same ``is_invalid_eta`` logic the reporter already shows in the
    "Invalid ETA" column.

    Args:
        items: List of detailed action-item dicts (must have ``EtaDate``).

    Returns:
        Subset of *items* with invalid ETAs.
    """
    from s360_reporter.data import is_invalid_eta

    return [item for item in items if is_invalid_eta(item.get("EtaDate"))]


def validate_eta_date(date_str: str) -> tuple[bool, str]:
    """Validate a user-entered ETA date string.

    Rules (BD-6):
    * Must be ``YYYY-MM-DD`` format
    * Must be today or later (not in the past)
    * Must be within 1 year from today

    Args:
        date_str: Date string entered by the user.

    Returns:
        ``(True, "")`` if valid, ``(False, reason)`` if invalid.
    """
    try:
        parsed = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return False, "Invalid date format. Use YYYY-MM-DD."

    today = date.today()

    if parsed < today:
        return False, "ETA date must be today or in the future."

    max_date = today + timedelta(days=365)
    if parsed > max_date:
        return False, f"ETA date must be within 1 year (before {max_date})."

    return True, ""


def build_eta_update(
    item: dict,
    eta_date_str: str,
    notes: str = "",
    fallback_alias: str = "",
) -> "EtaUpdate":
    """Build an ``EtaUpdate`` from a detailed action-item dict.

    Field resolution order for ``assigned_to`` (BD-2):
        ``ActionOwnerAlias`` → ``S360_AssignedTo`` → ``assignedTo`` → *fallback_alias*

    Args:
        item: Detailed action-item dict.
        eta_date_str: New ETA date as ``YYYY-MM-DD``.
        notes: Optional status note (``UserStatus``).
        fallback_alias: Alias to use when item has no owner fields.

    Returns:
        Populated ``EtaUpdate`` dataclass ready for ``save_etas()``.
    """
    from accia_s360.models import EtaUpdate

    assigned_to = (
        item.get("ActionOwnerAlias")
        or item.get("S360_AssignedTo")
        or item.get("assignedTo")
        or fallback_alias
        or ""
    )

    sla_type = item.get("SlaType") or "InSla"

    return EtaUpdate(
        kpi_id=item.get("_kpi_id", ""),
        service_id=item.get("S360_ServiceId", ""),
        action_item_id=item.get("id", ""),
        new_eta=datetime.strptime(eta_date_str, "%Y-%m-%d"),
        notes=notes,
        assigned_to=assigned_to,
        sla_type=sla_type,
    )
