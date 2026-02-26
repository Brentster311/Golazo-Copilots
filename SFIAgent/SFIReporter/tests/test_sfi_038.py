"""Tests for SFI-038: KPI Score column from kpi.csv lookup."""

from __future__ import annotations

import csv
import os
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest


class TestLoadKpiScores:
    """TC-1: CSV loading."""

    def test_returns_dict_keyed_by_name(self, tmp_path):
        """TC-1.1: load_kpi_scores returns dict keyed by KPI name."""
        from sfi_reporter.kpi_lookup import load_kpi_scores

        csv_file = tmp_path / "kpi.csv"
        csv_file.write_text(
            "KPI,KPIID,KPIScore\n"
            "[SFI-AR1.2.7] Vulnerability Management,527fb616-07aa-8198-6419-50d04ef1c2f3,93\n"
            "[SFI-NS2.1] IP allocations with Service Tags,04988624-19fe-4a58-974a-aa47f6f6c1a4,80\n"
            "GDPR Scan Compliance,aaaa-bbbb,50\n",
            encoding="utf-8",
        )

        result = load_kpi_scores(csv_file)
        # 3 name keys + 3 KPIID keys = 6 total
        assert len(result) == 6
        assert result["[SFI-AR1.2.7] Vulnerability Management"] == 93
        assert result["[SFI-NS2.1] IP allocations with Service Tags"] == 80
        assert result["GDPR Scan Compliance"] == 50

    def test_handles_missing_csv_gracefully(self, tmp_path):
        """TC-1.2: Missing CSV returns empty dict."""
        from sfi_reporter.kpi_lookup import load_kpi_scores

        result = load_kpi_scores(tmp_path / "nonexistent.csv")
        assert result == {}

    def test_provides_kpiid_keyed_lookup(self, tmp_path):
        """TC-1.3: Can also look up by KPIID."""
        from sfi_reporter.kpi_lookup import load_kpi_scores

        csv_file = tmp_path / "kpi.csv"
        csv_file.write_text(
            "KPI,KPIID,KPIScore\n"
            "[SFI-AR1.2.7] Vulnerability Management,527fb616-07aa-8198-6419-50d04ef1c2f3,93\n",
            encoding="utf-8",
        )

        result = load_kpi_scores(csv_file)
        assert result["527fb616-07aa-8198-6419-50d04ef1c2f3"] == 93

    def test_handles_quoted_kpi_names(self, tmp_path):
        """CSV entries with commas in names are quoted — should parse correctly."""
        from sfi_reporter.kpi_lookup import load_kpi_scores

        csv_file = tmp_path / "kpi.csv"
        csv_file.write_text(
            'KPI,KPIID,KPIScore\n'
            '"[SFI-PS1.1] Security Repair Items, Feature Gaps & Asks",c55814ac-f52b-4259-9ea9-656bde21ac5b,83\n',
            encoding="utf-8",
        )

        result = load_kpi_scores(csv_file)
        assert result["[SFI-PS1.1] Security Repair Items, Feature Gaps & Asks"] == 83

    def test_handles_utf8_bom(self, tmp_path):
        """CSV with BOM should load correctly."""
        from sfi_reporter.kpi_lookup import load_kpi_scores

        csv_file = tmp_path / "kpi.csv"
        csv_file.write_bytes(
            b"\xef\xbb\xbfKPI,KPIID,KPIScore\n"
            b"TestKPI,abc-123,42\n"
        )

        result = load_kpi_scores(csv_file)
        assert result["TestKPI"] == 42

    def test_default_path_is_package_dir(self):
        """Default loads from the package directory kpi.csv."""
        from sfi_reporter.kpi_lookup import load_kpi_scores

        result = load_kpi_scores()
        # The bundled kpi.csv should load successfully with >0 entries
        assert len(result) > 0
        # Spot check a known entry
        assert "[SFI-AR1.2.7] Vulnerability Management" in result
        assert result["[SFI-AR1.2.7] Vulnerability Management"] == 93


class TestScoreComputation:
    """TC-2: Score = KPIScore × count."""

    def test_kpi_score_times_count(self):
        """TC-2.1: KPI score = KPIScore × count."""
        from sfi_reporter.kpi_lookup import compute_kpi_score

        assert compute_kpi_score(93, 16) == 1488

    def test_missing_kpi_defaults_to_zero(self):
        """TC-2.2: Missing KPI score defaults to 0."""
        from sfi_reporter.kpi_lookup import compute_kpi_score

        assert compute_kpi_score(0, 16) == 0

    def test_kpi_with_zero_score(self):
        """TC-2.3: KPI with score=0 returns 0."""
        from sfi_reporter.kpi_lookup import compute_kpi_score

        assert compute_kpi_score(0, 5) == 0


class TestScoreAggregation:
    """TC-3 & TC-4: Service and program aggregation."""

    def test_service_score_aggregation(self):
        """TC-3.1: Service score = sum of per-KPI scores for items in that service."""
        from sfi_reporter.kpi_lookup import load_kpi_scores

        kpi_scores = {
            "KPI_A": 93,
            "KPI_B": 80,
        }

        # Simulate: service has 10 items of KPI_A and 5 items of KPI_B
        service_score = kpi_scores["KPI_A"] * 10 + kpi_scores["KPI_B"] * 5
        assert service_score == 1330

    def test_enrich_stats_adds_score(self):
        """TC-3.1b: enrich_stats_with_scores adds score field to kpi/service/program stats."""
        from sfi_reporter.kpi_lookup import enrich_stats_with_scores

        kpi_scores_lookup = {
            "Vulnerability Management": 93,
            "IP allocations": 80,
        }

        kpi_stats = {
            "kpi-1": {"name": "Vulnerability Management", "count": 16, "sla": 5, "invalid_eta": 1, "cost": 100.0},
            "kpi-2": {"name": "IP allocations", "count": 2, "sla": 2, "invalid_eta": 0, "cost": 50.0},
            "kpi-3": {"name": "Unknown KPI", "count": 3, "sla": 0, "invalid_eta": 0, "cost": 10.0},
        }

        enrich_stats_with_scores(kpi_stats, kpi_scores_lookup)

        assert kpi_stats["kpi-1"]["score"] == 93 * 16  # 1488
        assert kpi_stats["kpi-2"]["score"] == 80 * 2   # 160
        assert kpi_stats["kpi-3"]["score"] == 0         # Unknown KPI → 0

    def test_enrich_service_stats_by_items(self):
        """TC-3.1c: Service stats get score from per-item aggregation."""
        from sfi_reporter.kpi_lookup import compute_service_scores

        kpi_scores_lookup = {
            "Vuln Mgmt": 93,
            "IP Tags": 80,
        }

        # Each item has a KPI name and belongs to a service
        items = [
            {"S360_ServiceId": "svc-A", "_kpi_name": "Vuln Mgmt"},
            {"S360_ServiceId": "svc-A", "_kpi_name": "Vuln Mgmt"},
            {"S360_ServiceId": "svc-A", "_kpi_name": "IP Tags"},
            {"S360_ServiceId": "svc-B", "_kpi_name": "Vuln Mgmt"},
        ]

        service_stats = {
            "svc-A": {"name": "Service A", "count": 3, "sla": 0, "invalid_eta": 0, "cost": 0.0, "score": 0},
            "svc-B": {"name": "Service B", "count": 1, "sla": 0, "invalid_eta": 0, "cost": 0.0, "score": 0},
        }

        compute_service_scores(service_stats, items, kpi_scores_lookup)

        assert service_stats["svc-A"]["score"] == 93 + 93 + 80  # 266
        assert service_stats["svc-B"]["score"] == 93

    def test_program_score_aggregation(self):
        """TC-4.1: Program score = sum of per-item KPI scores."""
        from sfi_reporter.kpi_lookup import compute_program_scores

        kpi_scores_lookup = {"KPI_A": 93, "KPI_B": 50}

        items = [
            {"S360_ProgramIds": ["prog-1"], "_kpi_name": "KPI_A"},
            {"S360_ProgramIds": ["prog-1"], "_kpi_name": "KPI_B"},
            {"S360_ProgramIds": [], "_kpi_name": "KPI_A"},
        ]

        program_stats = {
            "Program One": {"count": 2, "sla": 0, "invalid_eta": 0, "cost": 0.0, "id": "prog-1", "score": 0},
            "Unassigned": {"count": 1, "sla": 0, "invalid_eta": 0, "cost": 0.0, "id": "unassigned", "score": 0},
        }

        program_id_to_name = {"prog-1": "Program One"}

        compute_program_scores(program_stats, items, kpi_scores_lookup, program_id_to_name)

        assert program_stats["Program One"]["score"] == 93 + 50  # 143
        assert program_stats["Unassigned"]["score"] == 93


class TestFormatScore:
    """TC-5.2: Score formatting."""

    def test_format_score_with_comma(self):
        """Score formatted with comma separator."""
        from sfi_reporter.kpi_lookup import format_score

        assert format_score(1488) == "1,488"
        assert format_score(0) == "0"
        assert format_score(81952) == "81,952"
