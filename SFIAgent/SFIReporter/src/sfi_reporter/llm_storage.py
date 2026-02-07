"""Persistent storage for LLM analysis results.

Saves and loads analysis JSON files under %LOCALAPPDATA%/sfireporter/analyses/.
"""
import json
import logging
import os
import re
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from sfi_reporter.llm_client import AnalysisResult

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1


def get_analyses_dir() -> Path:
    """Get the analyses storage directory, creating it if needed.

    Uses %LOCALAPPDATA%/sfireporter/analyses/ on Windows,
    ~/.local/share/sfireporter/analyses/ on POSIX.

    Returns:
        Path to the analyses directory.
    """
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    analyses_dir = base / "sfireporter" / "analyses"
    analyses_dir.mkdir(parents=True, exist_ok=True)
    return analyses_dir


def _sanitize_filename(action_item_id: str) -> str:
    """Sanitize an action item ID for use as a filename."""
    return re.sub(r'[^\w\-.]', '_', str(action_item_id))


def get_analysis_path(action_item_id: str) -> Path:
    """Get the file path for a saved analysis.

    Args:
        action_item_id: The action item ID.

    Returns:
        Path to the analysis JSON file.
    """
    return get_analyses_dir() / f"{_sanitize_filename(action_item_id)}.json"


def save_analysis(result: AnalysisResult) -> Path:
    """Save an analysis result to disk using atomic write.

    Args:
        result: The analysis result to save.

    Returns:
        Path to the saved file.
    """
    file_path = get_analysis_path(result.action_item_id)
    data = asdict(result)
    data["schema_version"] = SCHEMA_VERSION

    # Atomic write: write to temp file, then rename
    tmp_path = file_path.with_suffix(".tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(str(tmp_path), str(file_path))
        logger.info("Saved analysis for %s to %s", result.action_item_id, file_path)
        return file_path
    except OSError:
        # Clean up temp file on failure
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def load_analysis(action_item_id: str) -> Optional[AnalysisResult]:
    """Load a saved analysis from disk.

    Args:
        action_item_id: The action item ID.

    Returns:
        AnalysisResult if found and valid, None otherwise.
    """
    file_path = get_analysis_path(action_item_id)
    if not file_path.exists():
        return None

    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Remove schema_version before constructing AnalysisResult
        data.pop("schema_version", None)

        return AnalysisResult(**data)
    except (json.JSONDecodeError, TypeError, KeyError, OSError) as e:
        logger.warning("Failed to load analysis for %s: %s", action_item_id, e)
        return None


def analysis_exists(action_item_id: str) -> bool:
    """Check if a saved analysis exists for an action item.

    Args:
        action_item_id: The action item ID.

    Returns:
        True if a saved analysis file exists.
    """
    return get_analysis_path(action_item_id).exists()
