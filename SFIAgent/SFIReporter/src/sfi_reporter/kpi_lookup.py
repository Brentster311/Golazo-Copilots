"""KPI score lookup from bundled kpi.csv.

Loads the CSV once and provides helper functions for computing and
aggregating KPI-weighted scores across services, programs, and KPIs.
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_CSV = Path(__file__).parent / "kpi.csv"


def load_kpi_scores(path: Path | None = None) -> dict[str, int]:
    """Load kpi.csv and return a lookup dict.

    Keys are **both** the KPI name (``KPI`` column) and the KPI ID
    (``KPIID`` column), so callers can look up by either one.

    Args:
        path: Path to the CSV file.  Defaults to the bundled ``kpi.csv``
              next to this module.

    Returns:
        ``{kpi_name_or_id: score}`` dict.  Empty dict on any load error.
    """
    if path is None:
        path = _DEFAULT_CSV

    lookup: dict[str, int] = {}
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                name = row.get("KPI", "").strip()
                kpi_id = row.get("KPIID", "").strip()
                try:
                    score = int(row.get("KPIScore", 0))
                except (ValueError, TypeError):
                    score = 0
                if name:
                    lookup[name] = score
                if kpi_id:
                    lookup[kpi_id] = score
    except FileNotFoundError:
        logger.warning("kpi.csv not found at %s — all scores will be 0", path)
    except Exception:
        logger.exception("Failed to load kpi.csv from %s", path)

    return lookup


def compute_kpi_score(kpi_score: int, count: int) -> int:
    """Compute the weighted score for a single KPI row.

    Args:
        kpi_score: The KPI weight from kpi.csv (e.g. 93).
        count: Number of action items for this KPI.

    Returns:
        ``kpi_score * count``.
    """
    return kpi_score * count


def enrich_stats_with_scores(
    kpi_stats: dict[str, dict[str, Any]],
    kpi_scores_lookup: dict[str, int],
) -> None:
    """Add a ``score`` field to each entry in *kpi_stats*.

    ``score = lookup[name] * count``.  Missing KPIs default to 0.
    """
    for _kpi_id, stats in kpi_stats.items():
        name = stats.get("name", "")
        kpi_score = kpi_scores_lookup.get(name, 0)
        if kpi_score == 0:
            # Try by KPI ID as fallback
            kpi_score = kpi_scores_lookup.get(_kpi_id, 0)
        stats["score"] = compute_kpi_score(kpi_score, stats.get("count", 0))


def compute_service_scores(
    service_stats: dict[str, dict[str, Any]],
    items: list[dict[str, Any]],
    kpi_scores_lookup: dict[str, int],
) -> None:
    """Aggregate per-item KPI scores into service_stats.

    Each item contributes its KPI score (looked up by ``_kpi_name``)
    to the service identified by ``S360_ServiceId``.
    """
    for item in items:
        svc_id = item.get("S360_ServiceId", "Unknown")
        kpi_name = item.get("_kpi_name", "")
        kpi_score = kpi_scores_lookup.get(kpi_name, 0)
        if svc_id in service_stats:
            service_stats[svc_id]["score"] = service_stats[svc_id].get("score", 0) + kpi_score


def compute_program_scores(
    program_stats: dict[str, dict[str, Any]],
    items: list[dict[str, Any]],
    kpi_scores_lookup: dict[str, int],
    program_id_to_name: dict[str, str],
) -> None:
    """Aggregate per-item KPI scores into program_stats.

    Each item contributes its KPI score to the program identified by
    ``S360_ProgramIds[0]``.  Items without programs go to 'Unassigned'.
    """
    for item in items:
        kpi_name = item.get("_kpi_name", "")
        kpi_score = kpi_scores_lookup.get(kpi_name, 0)
        program_ids = item.get("S360_ProgramIds") or []

        if program_ids:
            pid = program_ids[0]
            prog_name = program_id_to_name.get(pid)
            if prog_name and prog_name in program_stats:
                program_stats[prog_name]["score"] = program_stats[prog_name].get("score", 0) + kpi_score
        else:
            if "Unassigned" in program_stats:
                program_stats["Unassigned"]["score"] = program_stats["Unassigned"].get("score", 0) + kpi_score


def format_score(value: int) -> str:
    """Format score for Treeview display with comma separators."""
    return f"{value:,}"
