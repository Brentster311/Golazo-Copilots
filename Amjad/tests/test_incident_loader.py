"""Tests for incident loader."""
import os
import pytest
from pathlib import Path

from ees.exceptions import IncidentLoadError
from ees.incident_loader import IncidentLoader


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


class TestIncidentLoaderHappyPath:
    """TC-01 partial: Load valid incident file."""

    def test_load_valid_file(self, fixtures_dir):
        loader = IncidentLoader()
        text = loader.load(fixtures_dir / "sample_incident.txt")
        assert "WebApp01" in text
        assert "CPU usage" in text.lower() or "CPUUsage" in text.lower() or "CPU" in text
        assert len(text) > 0


class TestIncidentLoaderErrors:
    """TC-02, TC-03: Error cases for incident loading."""

    def test_file_not_found(self):
        """TC-02: File not found error."""
        loader = IncidentLoader()
        with pytest.raises(IncidentLoadError, match="Incident file not found"):
            loader.load(Path("nonexistent/path/incident.txt"))

    def test_empty_file(self, tmp_path):
        """TC-03: Empty file error."""
        empty = tmp_path / "empty.txt"
        empty.write_text("")
        loader = IncidentLoader()
        with pytest.raises(IncidentLoadError, match="Incident file is empty"):
            loader.load(empty)

    def test_binary_file(self, tmp_path):
        """Binary file (non-UTF-8) error."""
        binary = tmp_path / "binary.bin"
        binary.write_bytes(b"\x80\x81\x82\x83\xff\xfe\xfd")
        loader = IncidentLoader()
        with pytest.raises(IncidentLoadError, match="Incident file is not valid text"):
            loader.load(binary)

    def test_large_file_warning(self, tmp_path, capsys, monkeypatch):
        """TC-26: Large file (>500KB) shows warning but proceeds."""
        large = tmp_path / "large.txt"
        large.write_text("x" * (600 * 1024))  # 600KB

        # Auto-confirm the prompt
        monkeypatch.setattr("builtins.input", lambda _: "y")

        loader = IncidentLoader()
        text = loader.load(large)
        assert len(text) > 0
