"""Tests for LLM storage (llm_storage.py)."""
import json
import os
import pytest
from pathlib import Path

from sfi_reporter.llm_client import AnalysisResult
from sfi_reporter.llm_storage import (
    save_analysis,
    load_analysis,
    analysis_exists,
    get_analysis_path,
    get_analyses_dir,
    _sanitize_filename,
    SCHEMA_VERSION,
)


# ── Fixture: AnalysisResult ───────────────────────────────────────────

@pytest.fixture
def sample_result():
    return AnalysisResult(
        action_item_id="AI-12345",
        kpi_id="KPI-67890",
        title="Remediate Azure SQL TDE encryption",
        analysis_text="### 🎯 Mission\nRemediate TDE.\n\n### ✅ Steps to Done\n1. Enable.\n",
        mission="Remediate TDE.",
        steps_to_done="1. Enable.",
        resources="Azure SQL DB instance-123.",
        risk_of_delay="Out of SLA.",
        model="gpt-4o",
        timestamp="2026-02-06T14:30:00+00:00",
        prompt_tokens=450,
        completion_tokens=200,
    )


@pytest.fixture
def analyses_dir(tmp_path, monkeypatch):
    """Redirect analyses to a temp directory."""
    analyses = tmp_path / "sfireporter" / "analyses"
    analyses.mkdir(parents=True)
    monkeypatch.setattr("sfi_reporter.llm_storage.get_analyses_dir", lambda: analyses)
    return analyses


# ── TC-7: Save Analysis Writes Valid JSON ─────────────────────────────

class TestSaveAnalysis:
    def test_saves_valid_json(self, sample_result, analyses_dir):
        """TC-7 Step 1-2: Saves valid JSON with schema_version."""
        path = save_analysis(sample_result)
        assert path.exists()

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["schema_version"] == SCHEMA_VERSION
        assert data["action_item_id"] == "AI-12345"
        assert data["kpi_id"] == "KPI-67890"
        assert data["timestamp"] == "2026-02-06T14:30:00+00:00"
        assert data["mission"] == "Remediate TDE."
        assert data["steps_to_done"] == "1. Enable."

    def test_overwrites_existing(self, sample_result, analyses_dir):
        """TC-7 Step 3: Saving again overwrites the file."""
        save_analysis(sample_result)

        updated = AnalysisResult(
            action_item_id="AI-12345",
            kpi_id="KPI-67890",
            title="Updated title",
            analysis_text="Updated analysis.",
            mission="Updated mission.",
            steps_to_done="Updated steps.",
            resources="Updated resources.",
            risk_of_delay="Updated risk.",
            model="gpt-4o",
            timestamp="2026-02-06T15:00:00+00:00",
            prompt_tokens=500,
            completion_tokens=250,
        )
        path = save_analysis(updated)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["title"] == "Updated title"
        assert data["timestamp"] == "2026-02-06T15:00:00+00:00"


# ── TC-8: Save Analysis Uses Atomic Write ─────────────────────────────

class TestSaveAtomicWrite:
    def test_tmp_file_cleaned_on_failure(self, sample_result, analyses_dir, monkeypatch):
        """TC-8 Step 1: On os.replace failure, temp file is cleaned up."""
        original_replace = os.replace

        def failing_replace(src, dst):
            raise OSError("Disk full")

        monkeypatch.setattr("os.replace", failing_replace)

        with pytest.raises(OSError, match="Disk full"):
            save_analysis(sample_result)

        # Verify no .tmp file left behind
        tmp_files = list(analyses_dir.glob("*.tmp"))
        assert len(tmp_files) == 0


# ── TC-9: Load Analysis Returns Saved Data ────────────────────────────

class TestLoadAnalysis:
    def test_round_trip(self, sample_result, analyses_dir):
        """TC-9 Step 1: Save then load returns matching data."""
        save_analysis(sample_result)
        loaded = load_analysis("AI-12345")

        assert loaded is not None
        assert loaded.action_item_id == "AI-12345"
        assert loaded.mission == "Remediate TDE."
        assert loaded.steps_to_done == "1. Enable."
        assert loaded.prompt_tokens == 450

    def test_nonexistent_returns_none(self, analyses_dir):
        """TC-9 Step 2: Non-existent ID returns None."""
        result = load_analysis("AI-NONEXISTENT")
        assert result is None

    def test_corrupted_json_returns_none(self, analyses_dir):
        """TC-9 Step 3: Corrupted JSON returns None."""
        path = analyses_dir / "AI-CORRUPT.json"
        path.write_text("{ invalid json !!!", encoding="utf-8")

        result = load_analysis("AI-CORRUPT")
        assert result is None


# ── TC-10: Analysis Exists Check ──────────────────────────────────────

class TestAnalysisExists:
    def test_not_exists(self, analyses_dir):
        """TC-10 Step 1: No file returns False."""
        assert analysis_exists("AI-NONE") is False

    def test_exists_after_save(self, sample_result, analyses_dir):
        """TC-10 Step 2: After save, returns True."""
        save_analysis(sample_result)
        assert analysis_exists("AI-12345") is True


# ── Filename sanitization ─────────────────────────────────────────────

class TestSanitizeFilename:
    def test_normal_id(self):
        assert _sanitize_filename("AI-12345") == "AI-12345"

    def test_special_characters(self):
        result = _sanitize_filename("AI/12345\\bad:chars")
        assert "/" not in result
        assert "\\" not in result
        assert ":" not in result
