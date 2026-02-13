"""Incident loader — file validation and text loading."""
from __future__ import annotations

from pathlib import Path

from ees.exceptions import IncidentLoadError

# 500KB threshold for large file warning
LARGE_FILE_THRESHOLD = 500 * 1024


class IncidentLoader:
    """Loads and validates incident text files."""

    def load(self, path: Path) -> str:
        """Load an incident file, returning the text content.

        Validates:
        - File exists
        - File is non-empty
        - File is valid UTF-8 text
        - Warns if file > 500KB (proceeds with user confirmation)

        Raises IncidentLoadError on validation failure.
        """
        # File not found
        if not path.exists():
            raise IncidentLoadError(f"Incident file not found: {path}")

        # Empty file
        if path.stat().st_size == 0:
            raise IncidentLoadError(f"Incident file is empty: {path}")

        # Try reading as UTF-8
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, ValueError):
            raise IncidentLoadError(f"Incident file is not valid text: {path}")

        # Large file warning
        if path.stat().st_size > LARGE_FILE_THRESHOLD:
            print(
                "Warning: Large incident file (>500KB). Proceeding may be slow.",
            )
            response = input("Continue? (y/n): ")
            if response.lower() != "y":
                raise IncidentLoadError("Aborted by user.")

        return text
