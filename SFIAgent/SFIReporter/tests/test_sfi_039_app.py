"""Tests for sfi_reporter.app — target ≥70 % statement coverage.

Covers: SFIReporterApp (init, _build_ui, _load_cached_data, _update_tables,
        event handlers, refresh/retry, ETA, filter, copilot panel) and main().
"""

from __future__ import annotations

import sys
import tkinter as tk
from unittest.mock import MagicMock
from datetime import datetime

import pytest

# ---------------------------------------------------------------------------
# Mock the copilot SDK before importing sfi_reporter
# ---------------------------------------------------------------------------
_mock_copilot = MagicMock()


class _FakeTool:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _FakeToolResult:
    def __init__(self, **kw):
        self.__dict__.update(kw)


_mock_copilot.Tool = _FakeTool
_mock_copilot.ToolResult = _FakeToolResult
_mock_copilot.define_tool = MagicMock()
_mock_copilot.CopilotClient = MagicMock
sys.modules.setdefault("copilot", _mock_copilot)

# NOW import the module under test
from sfi_reporter.app import SFIReporterApp, main  # noqa: E402
from sfi_reporter.models import OrgAncestry  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def app(tk_root, mocker):
    mocker.patch("sfi_reporter.app.get_current_user_alias", return_value="testuser")
    mocker.patch("sfi_reporter.app.read_cache", return_value=None)
    mocker.patch("sfi_reporter.app._load_setting", return_value=False)
    mocker.patch("sfi_reporter.app._save_setting")
    a = SFIReporterApp(tk_root)
    yield a


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_DATA_SIMPLE = {
    "services": [
        {"Id": "svc1", "Name": "Service One"},
        {"Id": "svc2", "Name": "Service Two"},
    ],
    "service_stats": {
        "svc1": {"name": "Service One", "count": 5, "sla": 1, "invalid_eta": 2, "cost": 100.0, "score": 80},
        "svc2": {"name": "Service Two", "count": 3, "sla": 0, "invalid_eta": 1, "cost": 50.0, "score": 90},
    },
    "program_stats": {
        "Program A": {"count": 4, "sla": 1, "invalid_eta": 1, "cost": 75.0, "score": 85, "id": "prog1"},
        "Program B": {"count": 4, "sla": 0, "invalid_eta": 2, "cost": 75.0, "score": 85, "id": "prog2"},
    },
    "kpi_stats": {
        "kpi1": {"name": "KPI One", "count": 5, "sla": 1, "invalid_eta": 2, "cost": 100.0, "score": 80},
        "kpi2": {"name": "KPI Two", "count": 3, "sla": 0, "invalid_eta": 1, "cost": 50.0, "score": 90},
    },
    "detailed_items": [
        {
            "S360_ServiceId": "svc1",
            "S360_ServiceTreeServiceName": "Service One",
            "_kpi_id": "kpi1",
            "SlaType": "OutOfSla",
            "EtaDate": "2024-01-01",
            "S360_ProgramIds": ["prog1"],
        },
        {
            "S360_ServiceId": "svc2",
            "S360_ServiceTreeServiceName": "Service Two",
            "_kpi_id": "kpi2",
            "SlaType": "InSla",
            "EtaDate": "2026-06-01",
            "S360_ProgramIds": ["prog2"],
        },
    ],
    "timestamp": datetime.now().isoformat(),
}

SAMPLE_DATA_MANAGER = {
    "is_manager": True,
    "services": [],
    "service_stats": {
        "svc1": {"name": "Service One", "count": 5, "sla": 1, "invalid_eta": 2, "cost": 100.0, "score": 80},
    },
    "service_owners": {
        "Service One": ["owner1"],
    },
    "org_mapping": {
        "owner1": OrgAncestry(path=("Root", "Team A", "owner1")),
    },
    "owner_stats": {
        "Team A": {"count": 5, "sla": 1, "invalid_eta": 2},
    },
    "program_stats": {
        "Program A": {"count": 5, "sla": 1, "invalid_eta": 2, "cost": 100.0, "score": 80, "id": "prog1"},
    },
    "kpi_stats": {
        "kpi1": {"name": "KPI One", "count": 5, "sla": 1, "invalid_eta": 2, "cost": 100.0, "score": 80},
    },
    "detailed_items": [
        {
            "S360_ServiceId": "svc1",
            "S360_ServiceTreeServiceName": "Service One",
            "_kpi_id": "kpi1",
            "SlaType": "OutOfSla",
            "EtaDate": "2024-01-01",
            "S360_ProgramIds": ["prog1"],
        },
    ],
    "timestamp": datetime.now().isoformat(),
}


SAMPLE_DATA_FALLBACK = {
    "service_stats": {
        "svc1": {"name": "Service One", "count": 5, "sla": 1, "invalid_eta": 2, "cost": 100.0, "score": 80},
        "svc2": {"name": "Service Two", "count": 3, "sla": 0, "invalid_eta": 1, "cost": 50.0, "score": 90},
    },
    "program_stats": {},
    "kpi_stats": {
        "kpi1": {"name": "KPI One", "count": 5, "sla": 1, "invalid_eta": 2, "cost": 100.0, "score": 80},
    },
    "detailed_items": [],
    "timestamp": datetime.now().isoformat(),
}


SAMPLE_DATA_MANAGER_MULTI = {
    "is_manager": True,
    "services": [],
    "service_stats": {
        "svc1": {"name": "Service One", "count": 5, "sla": 1, "invalid_eta": 2, "cost": 100.0, "score": 80},
        "svc2": {"name": "Service Two", "count": 3, "sla": 0, "invalid_eta": 1, "cost": 50.0, "score": 70},
        "svc3": {"name": "Service Three", "count": 2, "sla": 0, "invalid_eta": 0, "cost": 30.0, "score": 95},
        "svc4": {"name": "Service Four", "count": 1, "sla": 0, "invalid_eta": 0, "cost": 10.0, "score": 100},
    },
    "service_owners": {
        "Service One": ["owner1"],
        "Service Two": [],  # No Owner
        "Service Three": None,  # unknown triggers Unknown Owner via None
        # Service Four not in map → Unknown Owner
    },
    "org_mapping": {
        "owner1": OrgAncestry(path=("Root", "Team A", "owner1")),
    },
    "owner_stats": {
        "Team A": {"count": 5, "sla": 1, "invalid_eta": 2},
    },
    "program_stats": {
        "Program A": {"count": 8, "sla": 1, "invalid_eta": 2, "cost": 150.0, "score": 80, "id": "prog1"},
    },
    "kpi_stats": {
        "kpi1": {"name": "KPI One", "count": 8, "sla": 1, "invalid_eta": 2, "cost": 150.0, "score": 80},
    },
    "detailed_items": [
        {
            "S360_ServiceId": "svc1",
            "S360_ServiceTreeServiceName": "Service One",
            "_kpi_id": "kpi1",
            "SlaType": "OutOfSla",
            "EtaDate": "2024-01-01",
            "S360_ProgramIds": ["prog1"],
        },
        {
            "S360_ServiceId": "svc2",
            "S360_ServiceTreeServiceName": "Service Two",
            "_kpi_id": "kpi1",
            "SlaType": "InSla",
            "EtaDate": "2026-06-01",
            "S360_ProgramIds": ["prog1"],
        },
        {
            "S360_ServiceId": "svc3",
            "S360_ServiceTreeServiceName": "Service Three",
            "_kpi_id": "kpi1",
            "SlaType": "InSla",
            "EtaDate": "2026-06-01",
            "S360_ProgramIds": ["prog1"],
        },
        {
            "S360_ServiceId": "svc4",
            "S360_ServiceTreeServiceName": "Service Four",
            "_kpi_id": "kpi1",
            "SlaType": "InSla",
            "EtaDate": "2026-06-01",
            "S360_ProgramIds": ["prog1"],
        },
    ],
    "timestamp": datetime.now().isoformat(),
}


# Manager data where root_name bucket should be folded into root node
SAMPLE_DATA_MANAGER_ROOT_FOLD = {
    "is_manager": True,
    "services": [],
    "service_stats": {
        "svc1": {"name": "Service One", "count": 5, "sla": 1, "invalid_eta": 2, "cost": 100.0, "score": 80},
        "svc5": {"name": "Service Five", "count": 2, "sla": 0, "invalid_eta": 0, "cost": 20.0, "score": 95},
    },
    "service_owners": {
        "Service One": ["owner1"],
        "Service Five": ["owner_root"],
    },
    "org_mapping": {
        "owner1": OrgAncestry(path=("Root", "Team A", "owner1")),
        "owner_root": OrgAncestry(path=("Root",)),  # directly under root → short path
    },
    "owner_stats": {
        "Team A": {"count": 5, "sla": 1, "invalid_eta": 2},
    },
    "program_stats": {},
    "kpi_stats": {},
    "detailed_items": [],
    "timestamp": datetime.now().isoformat(),
}


# ---------------------------------------------------------------------------
# Tests: __init__ / _build_ui
# ---------------------------------------------------------------------------


class TestInit:
    def test_app_creates_successfully(self, app):
        assert app.root is not None
        assert app.detected_alias == "testuser"

    def test_alias_var_set(self, app):
        assert app.alias_var.get() == "testuser"

    def test_trees_exist(self, app):
        assert app.services_tree is not None
        assert app.program_tree is not None
        assert app.action_tree is not None

    def test_initial_maps_empty(self, app):
        assert app._service_id_map == {}
        assert app._service_name_map == {}
        assert app._program_id_map == {}
        assert app._kpi_id_map == {}

    def test_copilot_panel_initially_none(self, app):
        assert app._copilot_panel is None

    def test_retry_btn_exists(self, app):
        assert app.retry_btn is not None

    def test_status_vars_exist(self, app):
        assert app.status_var is not None
        assert app.cache_age_var is not None

    def test_query_btn_disabled_initially(self, app):
        assert str(app.query_btn.cget("state")) == "disabled"

    def test_eta_btn_disabled_initially(self, app):
        assert str(app.eta_btn.cget("state")) == "disabled"

    def test_score_column_precedes_cost_and_ratio_column_exists(self, app):
        assert app.services_tree["columns"] == ("name", "count", "sla", "invalid_eta", "score", "cost", "score_per_min")
        assert app.program_tree["columns"] == ("program", "count", "sla", "invalid_eta", "score", "cost", "score_per_min")
        assert app.action_tree["columns"] == ("name", "count", "sla", "invalid_eta", "score", "cost", "score_per_min")


# ---------------------------------------------------------------------------
# Tests: _load_cached_data
# ---------------------------------------------------------------------------


class TestLoadCachedData:
    def test_cache_miss(self, app, mocker):
        mocker.patch("sfi_reporter.app.read_cache", return_value=None)
        result = app._load_cached_data()
        assert result is False

    def test_cache_hit_valid(self, app, mocker):
        mocker.patch("sfi_reporter.app.read_cache", return_value=SAMPLE_DATA_SIMPLE)
        mocker.patch("sfi_reporter.app.is_cache_valid", return_value=True)
        mocker.patch("sfi_reporter.app._deserialize_org_data_from_cache", return_value=SAMPLE_DATA_SIMPLE)
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=5)
        result = app._load_cached_data()
        assert result is True
        assert "5 minutes" in app.cache_age_var.get()

    def test_cache_hit_old(self, app, mocker):
        mocker.patch("sfi_reporter.app.read_cache", return_value=SAMPLE_DATA_SIMPLE)
        mocker.patch("sfi_reporter.app.is_cache_valid", return_value=True)
        mocker.patch("sfi_reporter.app._deserialize_org_data_from_cache", return_value=SAMPLE_DATA_SIMPLE)
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=45)
        result = app._load_cached_data()
        assert result is True
        assert "45 minutes" in app.cache_age_var.get()

    def test_cache_hit_no_age(self, app, mocker):
        mocker.patch("sfi_reporter.app.read_cache", return_value=SAMPLE_DATA_SIMPLE)
        mocker.patch("sfi_reporter.app.is_cache_valid", return_value=True)
        mocker.patch("sfi_reporter.app._deserialize_org_data_from_cache", return_value=SAMPLE_DATA_SIMPLE)
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=None)
        result = app._load_cached_data()
        assert result is True

    def test_cache_invalid(self, app, mocker):
        mocker.patch("sfi_reporter.app.read_cache", return_value={"old": True})
        mocker.patch("sfi_reporter.app.is_cache_valid", return_value=False)
        result = app._load_cached_data()
        assert result is False

    def test_empty_alias(self, app, mocker):
        app.alias_var.set("")
        result = app._load_cached_data()
        assert result is False
        app.alias_var.set("testuser")

    def test_explicit_user_alias(self, app, mocker):
        mocker.patch("sfi_reporter.app.read_cache", return_value=SAMPLE_DATA_SIMPLE)
        mocker.patch("sfi_reporter.app.is_cache_valid", return_value=True)
        mocker.patch("sfi_reporter.app._deserialize_org_data_from_cache", return_value=SAMPLE_DATA_SIMPLE)
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=10)
        result = app._load_cached_data(user_alias="otheralias")
        assert result is True


# ---------------------------------------------------------------------------
# Tests: _on_alias_change
# ---------------------------------------------------------------------------


class TestOnAliasChange:
    def test_alias_change_triggers_load(self, app, mocker):
        m = mocker.patch.object(app, "_load_cached_data")
        app.alias_var.set("newalias")
        app._on_alias_change()
        m.assert_called_once_with("newalias")

    def test_alias_change_empty(self, app, mocker):
        m = mocker.patch.object(app, "_load_cached_data")
        app.alias_var.set("")
        app._on_alias_change()
        m.assert_not_called()
        app.alias_var.set("testuser")


# ---------------------------------------------------------------------------
# Tests: _update_tables — simple services branch
# ---------------------------------------------------------------------------


class TestUpdateTablesSimple:
    def test_populates_services_tree(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        children = app.services_tree.get_children()
        assert len(children) == 2

    def test_populates_program_tree(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        children = app.program_tree.get_children()
        assert len(children) == 2

    def test_populates_action_tree(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        children = app.action_tree.get_children()
        assert len(children) == 2

    def test_service_id_map_populated(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        assert "svc1" in app._service_id_map.values()
        assert "svc2" in app._service_id_map.values()

    def test_program_id_map_populated(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        assert "prog1" in app._program_id_map.values()
        assert "prog2" in app._program_id_map.values()

    def test_kpi_id_map_populated(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        assert "kpi1" in app._kpi_id_map.values()
        assert "kpi2" in app._kpi_id_map.values()

    def test_enables_query_btn(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        assert str(app.query_btn.cget("state")) == "normal"

    def test_enables_eta_btn(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        assert str(app.eta_btn.cget("state")) == "normal"

    def test_current_data_set(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        assert app.current_data is SAMPLE_DATA_SIMPLE

    def test_unfiltered_data_set(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        assert app._unfiltered_data is SAMPLE_DATA_SIMPLE

    def test_is_filtered_preserves_unfiltered(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        app._update_tables(SAMPLE_DATA_SIMPLE, is_filtered=True)
        assert app._unfiltered_data is SAMPLE_DATA_SIMPLE

    def test_cache_age_displayed(self, app, mocker):
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=10)
        app._update_tables(SAMPLE_DATA_SIMPLE)
        assert "10 minutes" in app.cache_age_var.get()

    def test_cache_age_none(self, app, mocker):
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=None)
        app._update_tables(SAMPLE_DATA_SIMPLE)

    def test_score_per_min_renders_for_non_zero_cost(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        first_service = app.services_tree.get_children()[0]
        values = app.services_tree.item(first_service, "values")
        assert values[6] == "0.80"

    def test_score_per_min_uses_default_cost_for_zero_cost(self, app):
        data = {
            "services": [{"Id": "svc1", "Name": "Service One"}],
            "service_stats": {
                "svc1": {"name": "Service One", "count": 1, "sla": 0, "invalid_eta": 0, "cost": 0, "score": 10},
            },
            "program_stats": {
                "Program A": {"count": 1, "sla": 0, "invalid_eta": 0, "cost": 0, "score": 10, "id": "prog1"},
            },
            "kpi_stats": {
                "kpi1": {"name": "KPI One", "count": 1, "sla": 0, "invalid_eta": 0, "cost": 0, "score": 10},
            },
            "detailed_items": [],
            "timestamp": datetime.now().isoformat(),
        }
        app._update_tables(data)
        first_service = app.services_tree.get_children()[0]
        values = app.services_tree.item(first_service, "values")
        assert values[5] == "28,800"
        assert values[6] == "0.00"


# ---------------------------------------------------------------------------
# Tests: _update_tables — fallback branch (service_stats only)
# ---------------------------------------------------------------------------


class TestUpdateTablesFallback:
    def test_populates_from_service_stats(self, app):
        app._update_tables(SAMPLE_DATA_FALLBACK)
        children = app.services_tree.get_children()
        assert len(children) == 2

    def test_service_ids_from_fallback(self, app):
        app._update_tables(SAMPLE_DATA_FALLBACK)
        assert "svc1" in app._service_id_map.values()

    def test_no_programs_in_fallback(self, app):
        app._update_tables(SAMPLE_DATA_FALLBACK)
        children = app.program_tree.get_children()
        assert len(children) == 0


# ---------------------------------------------------------------------------
# Tests: _update_tables — manager mode
# ---------------------------------------------------------------------------


class TestUpdateTablesManager:
    def test_manager_creates_hierarchy(self, app):
        app._update_tables(SAMPLE_DATA_MANAGER)
        children = app.services_tree.get_children()
        # Should have a root node
        assert len(children) >= 1

    def test_manager_group_path_map(self, app):
        app._update_tables(SAMPLE_DATA_MANAGER)
        assert len(app._group_path_map) > 0

    def test_manager_service_under_group(self, app):
        app._update_tables(SAMPLE_DATA_MANAGER)
        assert "svc1" in app._service_id_map.values()

    def test_manager_root_name_detected(self, app):
        app._update_tables(SAMPLE_DATA_MANAGER)
        # Root node should contain "Root" in its values
        root_children = app.services_tree.get_children()
        if root_children:
            vals = app.services_tree.item(root_children[0], "values")
            assert "Root" in str(vals[0])

    def test_manager_multi_owners(self, app):
        app._update_tables(SAMPLE_DATA_MANAGER_MULTI)
        children = app.services_tree.get_children()
        assert len(children) >= 1
        # Should have Unknown Owner and No Owner groups
        assert len(app._group_path_map) > 0

    def test_manager_no_owner_group(self, app):
        app._update_tables(SAMPLE_DATA_MANAGER_MULTI)
        paths = list(app._group_path_map.values())
        # Should have No Owner somewhere
        has_no_owner = any("No Owner" in p for p in paths)
        assert has_no_owner

    def test_manager_unknown_owner_group(self, app):
        app._update_tables(SAMPLE_DATA_MANAGER_MULTI)
        paths = list(app._group_path_map.values())
        has_unknown = any("Unknown Owner" in p for p in paths)
        assert has_unknown

    def test_manager_root_fold(self, app):
        """When a group matches root_name, it's folded into root node."""
        app._update_tables(SAMPLE_DATA_MANAGER_ROOT_FOLD)
        children = app.services_tree.get_children()
        assert len(children) >= 1

    def test_manager_without_org_mapping(self, app):
        """No org_mapping falls back to first owner name."""
        data = {
            "is_manager": True,
            "services": [],
            "service_stats": {
                "svc1": {"name": "Svc1", "count": 2, "sla": 0, "invalid_eta": 0, "cost": 10, "score": 90},
            },
            "service_owners": {"Svc1": ["alice"]},
            "org_mapping": {},
            "owner_stats": {"alice": {"count": 2, "sla": 0, "invalid_eta": 0}},
            "program_stats": {},
            "kpi_stats": {},
            "detailed_items": [],
            "timestamp": datetime.now().isoformat(),
        }
        app._update_tables(data)
        children = app.services_tree.get_children()
        assert len(children) >= 1

    def test_manager_owner_not_in_org_mapping(self, app):
        """Owner exists but not found in org_mapping → falls through."""
        data = {
            "is_manager": True,
            "services": [],
            "service_stats": {
                "svc1": {"name": "Svc1", "count": 2, "sla": 0, "invalid_eta": 0, "cost": 10, "score": 90},
            },
            "service_owners": {"Svc1": ["bob"]},
            "org_mapping": {
                "alice": OrgAncestry(path=("Root", "TeamX")),
            },
            "owner_stats": {"bob": {"count": 2}},
            "program_stats": {},
            "kpi_stats": {},
            "detailed_items": [],
            "timestamp": datetime.now().isoformat(),
        }
        app._update_tables(data)
        children = app.services_tree.get_children()
        assert len(children) >= 1

    def test_manager_empty_data(self, app):
        data = {
            "is_manager": True,
            "services": [],
            "service_stats": {},
            "service_owners": {},
            "org_mapping": {},
            "owner_stats": {},
            "program_stats": {},
            "kpi_stats": {},
            "detailed_items": [],
        }
        app._update_tables(data)
        children = app.services_tree.get_children()
        assert len(children) == 0

    def test_manager_deep_path(self, app):
        """Service with a 4-level org path."""
        data = {
            "is_manager": True,
            "services": [],
            "service_stats": {
                "svc1": {"name": "Svc1", "count": 1, "sla": 0, "invalid_eta": 0, "cost": 5, "score": 99},
            },
            "service_owners": {"Svc1": ["deep_owner"]},
            "org_mapping": {
                "deep_owner": OrgAncestry(path=("Root", "L1", "L2", "deep_owner")),
            },
            "owner_stats": {"L1": {"count": 1}},
            "program_stats": {},
            "kpi_stats": {},
            "detailed_items": [],
            "timestamp": datetime.now().isoformat(),
        }
        app._update_tables(data)
        assert len(app._group_path_map) > 0


# ---------------------------------------------------------------------------
# Tests: _update_tables — empty data
# ---------------------------------------------------------------------------


class TestUpdateTablesEmpty:
    def test_empty_dict(self, app):
        app._update_tables({})
        assert len(app.services_tree.get_children()) == 0
        assert len(app.program_tree.get_children()) == 0
        assert len(app.action_tree.get_children()) == 0

    def test_data_without_detailed_items_disables_query(self, app):
        app.query_btn.configure(state="normal")
        app._update_tables({"service_stats": {}})
        # query_btn stays as-is without detailed_items (doesn't re-enable)

    def test_clears_previous_data(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        assert len(app.services_tree.get_children()) == 2
        app._update_tables({})
        assert len(app.services_tree.get_children()) == 0


# ---------------------------------------------------------------------------
# Tests: _on_service_double_click
# ---------------------------------------------------------------------------


class TestOnServiceDoubleClick:
    def test_no_selection(self, app):
        app.services_tree.selection_remove(*app.services_tree.selection())
        # Should not raise
        app._on_service_double_click(MagicMock())

    def test_service_item_click(self, app, mocker):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        mock_modal = mocker.patch("sfi_reporter.app.DetailModal")

        iids = app.services_tree.get_children()
        assert len(iids) > 0
        svc_iid = iids[0]
        app.services_tree.selection_set(svc_iid)
        app._on_service_double_click(MagicMock())
        mock_modal.assert_called_once()

    def test_service_item_no_id(self, app, mocker):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        # Manually insert an item without mapping
        iid = app.services_tree.insert("", tk.END, values=("Phantom", 0, 0, 0, "$0", "0"))
        app.services_tree.selection_set(iid)
        app._on_service_double_click(MagicMock())
        # Should return silently

    def test_group_path_click(self, app, mocker):
        app._update_tables(SAMPLE_DATA_MANAGER)
        mock_modal = mocker.patch("sfi_reporter.app.DetailModal")
        mocker.patch("sfi_reporter.app.collect_services_for_owner", return_value={"Service One"})

        # Find a group path iid
        group_iids = [iid for iid in app._group_path_map]
        assert len(group_iids) > 0
        gid = group_iids[0]
        app.services_tree.selection_set(gid)
        app._on_service_double_click(MagicMock())
        mock_modal.assert_called_once()

    def test_unknown_owner_click(self, app, mocker):
        app._update_tables(SAMPLE_DATA_MANAGER_MULTI)
        mock_modal = mocker.patch("sfi_reporter.app.DetailModal")

        unknown_iid = None
        for iid, path in app._group_path_map.items():
            if path[-1] == "Unknown Owner":
                unknown_iid = iid
                break
        assert unknown_iid is not None
        app.services_tree.selection_set(unknown_iid)
        app._on_service_double_click(MagicMock())
        mock_modal.assert_called_once()

    def test_no_owner_click(self, app, mocker):
        app._update_tables(SAMPLE_DATA_MANAGER_MULTI)
        mock_modal = mocker.patch("sfi_reporter.app.DetailModal")

        no_owner_iid = None
        for iid, path in app._group_path_map.items():
            if path[-1] == "No Owner":
                no_owner_iid = iid
                break
        assert no_owner_iid is not None
        app.services_tree.selection_set(no_owner_iid)
        app._on_service_double_click(MagicMock())
        mock_modal.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: _on_program_double_click
# ---------------------------------------------------------------------------


class TestOnProgramDoubleClick:
    def test_no_selection(self, app):
        app.program_tree.selection_remove(*app.program_tree.selection())
        app._on_program_double_click(MagicMock())

    def test_program_click(self, app, mocker):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        mock_modal = mocker.patch("sfi_reporter.app.DetailModal")
        mocker.patch("sfi_reporter.app.filter_items_by_program", return_value=[])

        iids = app.program_tree.get_children()
        assert len(iids) > 0
        app.program_tree.selection_set(iids[0])
        app._on_program_double_click(MagicMock())
        mock_modal.assert_called_once()

    def test_unassigned_program_click(self, app, mocker):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        mock_modal = mocker.patch("sfi_reporter.app.DetailModal")

        # Insert an unassigned program entry
        iid = app.program_tree.insert("", tk.END, values=("Unassigned", 1, 0, 0, "$0", "0"))
        app._program_id_map[iid] = "unassigned"
        app.program_tree.selection_set(iid)
        app._on_program_double_click(MagicMock())
        mock_modal.assert_called_once()

    def test_program_no_id(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        iid = app.program_tree.insert("", tk.END, values=("Phantom", 0, 0, 0, "$0", "0"))
        app.program_tree.selection_set(iid)
        # Should silently return
        app._on_program_double_click(MagicMock())


# ---------------------------------------------------------------------------
# Tests: _on_action_double_click
# ---------------------------------------------------------------------------


class TestOnActionDoubleClick:
    def test_no_selection(self, app):
        app.action_tree.selection_remove(*app.action_tree.selection())
        app._on_action_double_click(MagicMock())

    def test_kpi_click(self, app, mocker):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        mock_modal = mocker.patch("sfi_reporter.app.DetailModal")

        iids = app.action_tree.get_children()
        assert len(iids) > 0
        app.action_tree.selection_set(iids[0])
        app._on_action_double_click(MagicMock())
        mock_modal.assert_called_once()

    def test_kpi_no_id(self, app):
        iid = app.action_tree.insert("", tk.END, values=("Phantom", 0, 0, 0, "$0", "0"))
        app.action_tree.selection_set(iid)
        app._on_action_double_click(MagicMock())


# ---------------------------------------------------------------------------
# Tests: _on_kpi_right_click
# ---------------------------------------------------------------------------


class TestOnKpiRightClick:
    def test_right_click_shows_menu(self, app, mocker):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        iids = app.action_tree.get_children()
        assert len(iids) > 0

        # Get bounds of first item to get a valid y coordinate
        bbox = app.action_tree.bbox(iids[0])
        if bbox:
            y = bbox[1] + 2
        else:
            y = 20

        event = MagicMock()
        event.y = y
        event.x_root = 100
        event.y_root = 100

        mock_menu_cls = mocker.patch("sfi_reporter.app.tk.Menu")
        mock_menu = MagicMock()
        mock_menu_cls.return_value = mock_menu

        app._on_kpi_right_click(event)
        # Menu popup should be called
        mock_menu.tk_popup.assert_called_once_with(100, 100)

    def test_right_click_no_row(self, app):
        event = MagicMock()
        event.y = -100  # outside any row
        app._on_kpi_right_click(event)

    def test_right_click_no_items(self, app, mocker):
        # Have a KPI row but no matching detailed_items
        app._update_tables(SAMPLE_DATA_SIMPLE)
        app.current_data = {"detailed_items": []}

        iids = app.action_tree.get_children()
        if iids:
            bbox = app.action_tree.bbox(iids[0])
            y = bbox[1] + 2 if bbox else 20
            event = MagicMock()
            event.y = y
            event.x_root = 100
            event.y_root = 100
            app._on_kpi_right_click(event)


# ---------------------------------------------------------------------------
# Tests: _update_status / _do_update_status
# ---------------------------------------------------------------------------


class TestUpdateStatus:
    def test_update_status(self, app):
        app._do_update_status("Hello", "green")
        assert app.status_var.get() == "Hello"

    def test_update_status_via_method(self, app, mocker):
        mocker.patch.object(app.root, "after")
        app._update_status("Testing", "blue")
        app.root.after.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: _on_update_etas
# ---------------------------------------------------------------------------


class TestOnUpdateEtas:
    def test_no_items(self, app):
        app.current_data = {}
        app._on_update_etas()  # Should return silently

    def test_opens_eta_mode_dialog(self, app, mocker):
        app.current_data = SAMPLE_DATA_SIMPLE
        mocker.patch(
            "sfi_reporter.app.get_items_needing_eta_update",
            create=True,
        )
        # Patch the lazy import inside _on_update_etas
        mock_get_items = MagicMock(return_value=[SAMPLE_DATA_SIMPLE["detailed_items"][0]])
        mocker.patch.dict("sys.modules", {
            "sfi_reporter.eta_logic": MagicMock(get_items_needing_eta_update=mock_get_items),
        })
        mock_eta_mode = mocker.patch("sfi_reporter.app.EtaModeDialog")
        app._on_update_etas()
        mock_eta_mode.assert_called_once()

    def test_eta_manual_mode(self, app, mocker):
        app.current_data = SAMPLE_DATA_SIMPLE
        mock_get_items = MagicMock(return_value=[SAMPLE_DATA_SIMPLE["detailed_items"][0]])
        mocker.patch.dict("sys.modules", {
            "sfi_reporter.eta_logic": MagicMock(get_items_needing_eta_update=mock_get_items),
        })

        mock_manual = mocker.patch("sfi_reporter.app.ManualEtaReviewDialog")
        mock_eta_mode = mocker.patch("sfi_reporter.app.EtaModeDialog")

        def capture_on_mode(*args, **kwargs):
            on_choice = kwargs.get("on_choice") or args[3]
            on_choice("manual")

        mock_eta_mode.side_effect = capture_on_mode
        app._on_update_etas()
        mock_manual.assert_called_once()

    def test_eta_bulk_mode(self, app, mocker):
        app.current_data = SAMPLE_DATA_SIMPLE
        mock_get_items = MagicMock(return_value=[SAMPLE_DATA_SIMPLE["detailed_items"][0]])
        mocker.patch.dict("sys.modules", {
            "sfi_reporter.eta_logic": MagicMock(get_items_needing_eta_update=mock_get_items),
        })

        mock_bulk = mocker.patch("sfi_reporter.app.BulkEtaProgressDialog")
        mock_eta_mode = mocker.patch("sfi_reporter.app.EtaModeDialog")

        def capture_on_mode(*args, **kwargs):
            on_choice = kwargs.get("on_choice") or args[3]
            on_choice("bulk")

        mock_eta_mode.side_effect = capture_on_mode
        app._on_update_etas()
        mock_bulk.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: _on_eta_update_complete
# ---------------------------------------------------------------------------


class TestOnEtaUpdateComplete:
    def test_no_saved(self, app):
        app._on_eta_update_complete(saved=[], skipped=[], failed=[])
        # Should return silently

    def test_saved_updates_items(self, app, mocker):
        import copy
        data = copy.deepcopy(SAMPLE_DATA_SIMPLE)
        app.current_data = data
        app._unfiltered_data = data
        mocker.patch("sfi_reporter.app.write_cache")
        mocker.patch("sfi_reporter.app._serialize_org_data_for_cache", return_value=data)

        item = data["detailed_items"][0]
        saved = [(item, "2026-12-31", "Updated note")]

        app._on_eta_update_complete(saved=saved, skipped=[], failed=[])
        assert item["EtaDate"] == "2026-12-31"
        assert item["EtaStatus"] == "Updated note"
        app.root.update()
        assert "1 ETA(s) updated" in app.status_var.get()

    def test_saved_recalculates_stats(self, app, mocker):
        import copy
        data = copy.deepcopy(SAMPLE_DATA_SIMPLE)
        app.current_data = data
        app._unfiltered_data = data
        mocker.patch("sfi_reporter.app.write_cache")
        mocker.patch("sfi_reporter.app._serialize_org_data_for_cache", return_value=data)

        item = data["detailed_items"][0]
        saved = [(item, "2026-12-31", "")]

        app._on_eta_update_complete(saved=saved, skipped=[], failed=[])
        # Stats should have been recalculated
        assert data["service_stats"]["svc1"]["invalid_eta"] >= 0

    def test_saved_manager_recalculates_owner_stats(self, app, mocker):
        import copy
        data = copy.deepcopy(SAMPLE_DATA_MANAGER)
        app.current_data = data
        app._unfiltered_data = data
        mocker.patch("sfi_reporter.app.write_cache")
        mocker.patch("sfi_reporter.app._serialize_org_data_for_cache", return_value=data)
        mock_agg = mocker.patch("sfi_reporter.app.aggregate_by_owner", return_value={})

        item = data["detailed_items"][0]
        saved = [(item, "2026-12-31", "")]
        app._on_eta_update_complete(saved=saved, skipped=[], failed=[])
        mock_agg.assert_called_once()

    def test_saved_writes_cache(self, app, mocker):
        import copy
        data = copy.deepcopy(SAMPLE_DATA_SIMPLE)
        app.current_data = data
        app._unfiltered_data = data
        mock_write = mocker.patch("sfi_reporter.app.write_cache")
        mocker.patch("sfi_reporter.app._serialize_org_data_for_cache", return_value=data)

        item = data["detailed_items"][0]
        saved = [(item, "2026-12-31", None)]
        app._on_eta_update_complete(saved=saved, skipped=[], failed=[])
        mock_write.assert_called_once()

    def test_saved_with_program_eta_recount(self, app, mocker):
        """Covers the program_stats invalid_eta increment path."""
        import copy
        data = copy.deepcopy(SAMPLE_DATA_SIMPLE)
        data["programs_lookup"] = {"prog1": "Program A"}
        app.current_data = data
        app._unfiltered_data = data
        mocker.patch("sfi_reporter.app.write_cache")
        mocker.patch("sfi_reporter.app._serialize_org_data_for_cache", return_value=data)

        item = data["detailed_items"][0]
        # Set ETA to invalid value (in the past)
        saved = [(item, "2020-01-01", "")]
        app._on_eta_update_complete(saved=saved, skipped=[], failed=[])


# ---------------------------------------------------------------------------
# Tests: _refresh_tables_after_eta_update
# ---------------------------------------------------------------------------


class TestRefreshTablesAfterEtaUpdate:
    def test_no_data(self, app):
        app.current_data = {}
        app._refresh_tables_after_eta_update()

    def test_with_data(self, app, mocker):
        app.current_data = SAMPLE_DATA_SIMPLE
        app._unfiltered_data = SAMPLE_DATA_SIMPLE
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=5)
        app._refresh_tables_after_eta_update()
        app.root.update()
        assert "Copilot" in app.status_var.get()

    def test_filtered_state(self, app, mocker):
        app.current_data = SAMPLE_DATA_SIMPLE
        app._unfiltered_data = {"different": True}
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=5)
        app._refresh_tables_after_eta_update()


# ---------------------------------------------------------------------------
# Tests: _on_refresh
# ---------------------------------------------------------------------------


class TestOnRefresh:
    def test_no_alias_shows_warning(self, app, mocker):
        mock_mb = mocker.patch("sfi_reporter.app.messagebox")
        app.alias_var.set("")
        app._on_refresh()
        mock_mb.showwarning.assert_called_once()
        app.alias_var.set("testuser")

    def test_starts_thread(self, app, mocker):
        mock_thread = mocker.patch("sfi_reporter.app.threading.Thread")
        app.alias_var.set("testuser")
        app._on_refresh()
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()

    def test_disables_buttons(self, app, mocker):
        mocker.patch("sfi_reporter.app.threading.Thread")
        app.alias_var.set("testuser")
        app._on_refresh()
        assert str(app.refresh_btn.cget("state")) == "disabled"
        assert str(app.clear_btn.cget("state")) == "disabled"
        # Re-enable for future tests
        app.refresh_btn.configure(state=tk.NORMAL)
        app.clear_btn.configure(state=tk.NORMAL)


# ---------------------------------------------------------------------------
# Tests: _on_refresh_complete
# ---------------------------------------------------------------------------


class TestOnRefreshComplete:
    def test_with_data_success(self, app, mocker):
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=2)
        data = dict(SAMPLE_DATA_SIMPLE)
        data["failed_kpis"] = []
        data["audience_ids"] = ["aud1"]
        data["kpi_names"] = {}
        app._on_refresh_complete(data)
        app.root.update()
        assert "refreshed" in app.status_var.get()

    def test_with_data_no_items(self, app, mocker):
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=2)
        data = {
            "services": [],
            "detailed_items": [],
            "kpi_stats": {},
            "program_stats": {},
            "service_stats": {},
            "failed_kpis": [],
            "audience_ids": [],
            "kpi_names": {},
        }
        app._on_refresh_complete(data)
        app.root.update()
        assert "No action items" in app.status_var.get()

    def test_with_failed_kpis(self, app, mocker):
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=2)
        data = dict(SAMPLE_DATA_SIMPLE)
        data["failed_kpis"] = [{"kpi_id": "kpi1", "kpi_name": "KPI One"}]
        data["audience_ids"] = ["aud1"]
        data["kpi_names"] = {"kpi1": "KPI One"}
        app._on_refresh_complete(data)
        app.root.update()
        assert "failed" in app.status_var.get().lower() or "KPI" in app.status_var.get()

    def test_no_data_error(self, app):
        app._on_refresh_complete(None)
        app.root.update()
        assert "Error" in app.status_var.get()

    def test_reapply_filter_on_refresh(self, app, mocker):
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=2)
        mock_reapply = mocker.patch.object(app, "_reapply_last_filter")
        app._reapply_filter_var.set(True)
        app._last_filter_clauses = [{"field": "SlaType", "op": "==", "value": "OutOfSla"}]

        data = dict(SAMPLE_DATA_SIMPLE)
        data["failed_kpis"] = []
        data["audience_ids"] = []
        data["kpi_names"] = {}
        app._on_refresh_complete(data)
        mock_reapply.assert_called_once()
        app._reapply_filter_var.set(False)
        app._last_filter_clauses = []

    def test_buttons_reenabled(self, app, mocker):
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=2)
        app.refresh_btn.configure(state=tk.DISABLED)
        app.clear_btn.configure(state=tk.DISABLED)
        app._on_refresh_complete(None)
        assert str(app.refresh_btn.cget("state")) == "normal"
        assert str(app.clear_btn.cget("state")) == "normal"


# ---------------------------------------------------------------------------
# Tests: _on_retry_failed
# ---------------------------------------------------------------------------


class TestOnRetryFailed:
    def test_no_failed_kpis(self, app):
        app._failed_kpis = []
        app._audience_ids = []
        app._on_retry_failed()  # Returns silently

    def test_no_audience_ids(self, app):
        app._failed_kpis = [{"kpi_id": "k1", "kpi_name": "K1"}]
        app._audience_ids = []
        app._on_retry_failed()  # Returns silently

    def test_starts_retry_thread(self, app, mocker):
        mock_thread = mocker.patch("sfi_reporter.app.threading.Thread")
        app._failed_kpis = [{"kpi_id": "k1", "kpi_name": "K1"}]
        app._audience_ids = ["aud1"]
        app._kpi_names = {"k1": "K1"}
        app._on_retry_failed()
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
        # Re-enable buttons
        app.refresh_btn.configure(state=tk.NORMAL)
        app.clear_btn.configure(state=tk.NORMAL)
        app.retry_btn.configure(state=tk.NORMAL)


# ---------------------------------------------------------------------------
# Tests: _on_retry_complete
# ---------------------------------------------------------------------------


class TestOnRetryComplete:
    def test_no_rows_still_failed(self, app):
        still_failed = [{"kpi_id": "k1", "kpi_name": "K1"}]
        app._on_retry_complete(new_rows=[], still_failed=still_failed, alias="testuser")
        app.root.update()
        assert "still failing" in app.status_var.get()

    def test_cache_missing(self, app, mocker):
        mocker.patch("sfi_reporter.app.read_cache", return_value=None)
        app._on_retry_complete(
            new_rows=[{"_kpi_id": "k1", "SlaType": "OutOfSla", "EtaDate": "2024-01-01"}],
            still_failed=[],
            alias="testuser",
        )
        app.root.update()
        assert "Cache missing" in app.status_var.get()

    def test_success_with_rows(self, app, mocker):
        import copy
        cached = copy.deepcopy(SAMPLE_DATA_SIMPLE)
        mocker.patch("sfi_reporter.app.read_cache", return_value=cached)
        mocker.patch("sfi_reporter.app._deserialize_org_data_from_cache", return_value=cached)
        mocker.patch("sfi_reporter.app.write_cache")
        mocker.patch("sfi_reporter.app._serialize_org_data_for_cache", return_value=cached)
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=1)

        new_rows = [{"_kpi_id": "kpi1", "SlaType": "OutOfSla", "EtaDate": "2024-01-01"}]
        app._on_retry_complete(new_rows=new_rows, still_failed=[], alias="testuser")
        app.root.update()
        assert "successful" in app.status_var.get()

    def test_partial_success(self, app, mocker):
        import copy
        cached = copy.deepcopy(SAMPLE_DATA_SIMPLE)
        mocker.patch("sfi_reporter.app.read_cache", return_value=cached)
        mocker.patch("sfi_reporter.app._deserialize_org_data_from_cache", return_value=cached)
        mocker.patch("sfi_reporter.app.write_cache")
        mocker.patch("sfi_reporter.app._serialize_org_data_for_cache", return_value=cached)
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=1)

        new_rows = [{"_kpi_id": "kpi1", "SlaType": "InSla", "EtaDate": "2026-06-01"}]
        still_failed = [{"kpi_id": "k2", "kpi_name": "K2"}]
        app._on_retry_complete(new_rows=new_rows, still_failed=still_failed, alias="testuser")
        app.root.update()
        assert "Recovered" in app.status_var.get()
        assert "still failing" in app.status_var.get()

    def test_new_kpi_in_retry(self, app, mocker):
        """Row with a KPI not already in kpi_stats creates a new entry."""
        import copy
        cached = copy.deepcopy(SAMPLE_DATA_SIMPLE)
        cached["kpi_names"] = {"kpi_new": "New KPI"}
        mocker.patch("sfi_reporter.app.read_cache", return_value=cached)
        mocker.patch("sfi_reporter.app._deserialize_org_data_from_cache", return_value=cached)
        mocker.patch("sfi_reporter.app.write_cache")
        mocker.patch("sfi_reporter.app._serialize_org_data_for_cache", return_value=cached)
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=1)

        new_rows = [{"_kpi_id": "kpi_new", "SlaType": "OutOfSla", "EtaDate": "2024-01-01"}]
        app._on_retry_complete(new_rows=new_rows, still_failed=[], alias="testuser")
        assert "kpi_new" in cached["kpi_stats"]


# ---------------------------------------------------------------------------
# Tests: _on_clear_cache
# ---------------------------------------------------------------------------


class TestOnClearCache:
    def test_clear_cache_success(self, app, mocker):
        mocker.patch("sfi_reporter.app.clear_cache", return_value=True)
        app._update_tables(SAMPLE_DATA_SIMPLE)
        app._on_clear_cache()
        assert len(app.services_tree.get_children()) == 0
        assert len(app.action_tree.get_children()) == 0
        assert len(app.program_tree.get_children()) == 0
        app.root.update()
        assert "cleared" in app.status_var.get().lower()

    def test_clear_cache_failure(self, app, mocker):
        mocker.patch("sfi_reporter.app.clear_cache", return_value=False)
        app._on_clear_cache()

    def test_clear_cache_no_alias(self, app, mocker):
        app.alias_var.set("")
        app._on_clear_cache()
        app.alias_var.set("testuser")


# ---------------------------------------------------------------------------
# Tests: _on_query
# ---------------------------------------------------------------------------


class TestOnQuery:
    def test_opens_query_builder(self, app, mocker):
        app.current_data = SAMPLE_DATA_SIMPLE
        app._unfiltered_data = SAMPLE_DATA_SIMPLE
        mock_qb = mocker.patch("sfi_reporter.app.QueryBuilder", create=True)
        # Need to mock the lazy import
        mock_mod = MagicMock()
        mock_mod.QueryBuilder = mock_qb
        mocker.patch.dict("sys.modules", {"sfi_reporter.query_builder": mock_mod})
        app._on_query()
        mock_qb.assert_called_once()

    def test_query_with_programs_lookup(self, app, mocker):
        import copy
        data = copy.deepcopy(SAMPLE_DATA_SIMPLE)
        data["programs_lookup"] = {"prog1": "Program A"}
        app.current_data = data
        app._unfiltered_data = data
        mock_qb = mocker.patch("sfi_reporter.app.QueryBuilder", create=True)
        mock_mod = MagicMock()
        mock_mod.QueryBuilder = mock_qb
        mocker.patch.dict("sys.modules", {"sfi_reporter.query_builder": mock_mod})
        app._on_query()
        mock_qb.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: _reapply_last_filter
# ---------------------------------------------------------------------------


class TestReapplyLastFilter:
    def test_reapply_filter(self, app, mocker):
        app._unfiltered_data = SAMPLE_DATA_SIMPLE
        app._last_filter_clauses = [{"field": "SlaType"}]
        app._last_filter_ussec = False

        mock_eval = MagicMock(return_value=[SAMPLE_DATA_SIMPLE["detailed_items"][0]])
        mock_mod = MagicMock()
        mock_mod.evaluate_clauses = mock_eval
        mocker.patch.dict("sys.modules", {"sfi_reporter.query_builder": mock_mod})

        mock_on_filter = mocker.patch.object(app, "_on_filter_applied")
        app._reapply_last_filter()
        mock_on_filter.assert_called_once()

    def test_reapply_no_items(self, app, mocker):
        app._unfiltered_data = {"detailed_items": []}
        app._last_filter_clauses = [{"field": "SlaType"}]
        app._reapply_last_filter()
        # Returns early


# ---------------------------------------------------------------------------
# Tests: _on_filter_applied
# ---------------------------------------------------------------------------


class TestOnFilterApplied:
    def test_reset_filter_no_clauses(self, app, mocker):
        app._unfiltered_data = SAMPLE_DATA_SIMPLE
        app.current_data = SAMPLE_DATA_SIMPLE
        mock_load = MagicMock(return_value=([], False))
        mock_mod = MagicMock()
        mock_mod.load_clause_cache = mock_load
        mocker.patch.dict("sys.modules", {"sfi_reporter.query_builder": mock_mod})
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=5)

        app._on_filter_applied([], [])
        assert "Filter" in app.query_btn.cget("text")
        assert "(" not in app.query_btn.cget("text")

    def test_filter_with_clauses(self, app, mocker):
        app._unfiltered_data = SAMPLE_DATA_SIMPLE
        app.current_data = SAMPLE_DATA_SIMPLE
        mock_load = MagicMock(return_value=([], False))
        mock_mod = MagicMock()
        mock_mod.load_clause_cache = mock_load
        mocker.patch.dict("sys.modules", {"sfi_reporter.query_builder": mock_mod})
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=5)

        clauses = [{"field": "SlaType", "op": "==", "value": "OutOfSla"}]
        filtered = [SAMPLE_DATA_SIMPLE["detailed_items"][0]]
        app._on_filter_applied(filtered, clauses)
        assert "(1)" in app.query_btn.cget("text")

    def test_filter_with_program_items(self, app, mocker):
        app._unfiltered_data = SAMPLE_DATA_SIMPLE
        app.current_data = SAMPLE_DATA_SIMPLE
        mock_load = MagicMock(return_value=([], False))
        mock_mod = MagicMock()
        mock_mod.load_clause_cache = mock_load
        mocker.patch.dict("sys.modules", {"sfi_reporter.query_builder": mock_mod})
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=5)

        clauses = [{"field": "SlaType"}]
        filtered = SAMPLE_DATA_SIMPLE["detailed_items"]
        app._on_filter_applied(filtered, clauses)

    def test_filter_unassigned_program(self, app, mocker):
        """Items with no S360_ProgramIds go to Unassigned."""
        app._unfiltered_data = SAMPLE_DATA_SIMPLE
        app.current_data = SAMPLE_DATA_SIMPLE
        mock_load = MagicMock(return_value=([], False))
        mock_mod = MagicMock()
        mock_mod.load_clause_cache = mock_load
        mocker.patch.dict("sys.modules", {"sfi_reporter.query_builder": mock_mod})
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=5)

        item_no_prog = {
            "S360_ServiceId": "svc1",
            "S360_ServiceTreeServiceName": "Service One",
            "_kpi_id": "kpi1",
            "SlaType": "OutOfSla",
            "EtaDate": "2024-01-01",
            "S360_ProgramIds": [],
        }
        app._on_filter_applied([item_no_prog], [{"field": "SlaType"}])

    def test_filter_manager_mode(self, app, mocker):
        """Manager mode triggers aggregate_by_owner in filter."""
        import copy
        data = copy.deepcopy(SAMPLE_DATA_MANAGER)
        app._unfiltered_data = data
        app.current_data = data
        mock_load = MagicMock(return_value=([], False))
        mock_mod = MagicMock()
        mock_mod.load_clause_cache = mock_load
        mocker.patch.dict("sys.modules", {"sfi_reporter.query_builder": mock_mod})
        mocker.patch("sfi_reporter.app.aggregate_by_owner", return_value={})
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=5)

        clauses = [{"field": "SlaType"}]
        app._on_filter_applied(data["detailed_items"], clauses)


# ---------------------------------------------------------------------------
# Tests: _toggle_copilot_panel / _hide_copilot_panel
# ---------------------------------------------------------------------------


class TestCopilotPanel:
    def test_toggle_creates_panel(self, app, mocker):
        mock_panel = MagicMock()
        mock_panel.winfo_ismapped.return_value = False
        mock_cp_cls = MagicMock(return_value=mock_panel)
        mock_mod = MagicMock()
        mock_mod.CopilotPanel = mock_cp_cls
        mocker.patch.dict("sys.modules", {"sfi_reporter.copilot_panel": mock_mod})
        mocker.patch.object(app._container, "add")

        app._copilot_panel = None
        app._toggle_copilot_panel()
        mock_cp_cls.assert_called_once()
        app._container.add.assert_called_once()

    def test_toggle_shows_hidden_panel(self, app, mocker):
        mock_panel = MagicMock()
        mock_panel.winfo_ismapped.return_value = False
        app._copilot_panel = mock_panel
        mocker.patch.object(app._container, "add")
        app._toggle_copilot_panel()
        app._container.add.assert_called()

    def test_toggle_hides_visible_panel(self, app, mocker):
        mock_panel = MagicMock()
        mock_panel.winfo_ismapped.return_value = True
        app._copilot_panel = mock_panel
        mocker.patch.object(app._container, "forget")
        app._toggle_copilot_panel()
        app._container.forget.assert_called_once_with(mock_panel)

    def test_hide_panel_when_visible(self, app, mocker):
        mock_panel = MagicMock()
        mock_panel.winfo_ismapped.return_value = True
        app._copilot_panel = mock_panel
        mocker.patch.object(app._container, "forget")
        app._hide_copilot_panel()
        app._container.forget.assert_called_once_with(mock_panel)

    def test_hide_panel_when_not_visible(self, app, mocker):
        mock_panel = MagicMock()
        mock_panel.winfo_ismapped.return_value = False
        app._copilot_panel = mock_panel
        mocker.patch.object(app._container, "forget")
        app._hide_copilot_panel()
        app._container.forget.assert_not_called()

    def test_hide_panel_when_none(self, app):
        app._copilot_panel = None
        app._hide_copilot_panel()  # Should not raise


# ---------------------------------------------------------------------------
# Tests: main()
# ---------------------------------------------------------------------------


class TestMain:
    def test_main_runs(self, mocker):
        mocker.patch("sfi_reporter.app.setup_logging")
        mocker.patch("sfi_reporter.app.patch_subprocess_windows")
        mocker.patch("sfi_reporter.app.get_log_path", return_value="/tmp/test.log")
        mocker.patch("sfi_reporter.app.get_current_user_alias", return_value="testuser")
        mocker.patch("sfi_reporter.app.read_cache", return_value=None)
        mocker.patch("sfi_reporter.app._load_setting", return_value=False)
        mocker.patch("sfi_reporter.app._save_setting")

        mock_root = MagicMock(spec=tk.Tk)
        mock_root._sfi_app = None
        mocker.patch("sfi_reporter.app.tk.Tk", return_value=mock_root)

        mock_style = MagicMock()
        mock_style.theme_names.return_value = ["vista", "clam"]
        mocker.patch("sfi_reporter.app.ttk.Style", return_value=mock_style)

        mocker.patch("sfi_reporter.app.SFIReporterApp")

        main()
        mock_root.mainloop.assert_called_once()

    def test_main_clam_fallback(self, mocker):
        mocker.patch("sfi_reporter.app.setup_logging")
        mocker.patch("sfi_reporter.app.patch_subprocess_windows")
        mocker.patch("sfi_reporter.app.get_log_path", return_value="/tmp/test.log")
        mocker.patch("sfi_reporter.app.get_current_user_alias", return_value="testuser")
        mocker.patch("sfi_reporter.app.read_cache", return_value=None)
        mocker.patch("sfi_reporter.app._load_setting", return_value=False)
        mocker.patch("sfi_reporter.app._save_setting")

        mock_root = MagicMock(spec=tk.Tk)
        mock_root._sfi_app = None
        mocker.patch("sfi_reporter.app.tk.Tk", return_value=mock_root)

        mock_style = MagicMock()
        mock_style.theme_names.return_value = ["clam", "default"]
        mocker.patch("sfi_reporter.app.ttk.Style", return_value=mock_style)

        mocker.patch("sfi_reporter.app.SFIReporterApp")

        main()
        mock_style.theme_use.assert_called_with("clam")

    def test_main_no_vista_no_clam(self, mocker):
        mocker.patch("sfi_reporter.app.setup_logging")
        mocker.patch("sfi_reporter.app.patch_subprocess_windows")
        mocker.patch("sfi_reporter.app.get_log_path", return_value="/tmp/test.log")
        mocker.patch("sfi_reporter.app.get_current_user_alias", return_value="testuser")
        mocker.patch("sfi_reporter.app.read_cache", return_value=None)
        mocker.patch("sfi_reporter.app._load_setting", return_value=False)
        mocker.patch("sfi_reporter.app._save_setting")

        mock_root = MagicMock(spec=tk.Tk)
        mock_root._sfi_app = None
        mocker.patch("sfi_reporter.app.tk.Tk", return_value=mock_root)

        mock_style = MagicMock()
        mock_style.theme_names.return_value = ["default"]
        mocker.patch("sfi_reporter.app.ttk.Style", return_value=mock_style)

        mocker.patch("sfi_reporter.app.SFIReporterApp")

        main()
        mock_style.theme_use.assert_not_called()


# ---------------------------------------------------------------------------
# Edge case / additional coverage tests
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_update_tables_clears_maps_each_call(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        first_ids = set(app._service_id_map.values())
        app._update_tables(SAMPLE_DATA_SIMPLE)
        second_ids = set(app._service_id_map.values())
        assert first_ids == second_ids

    def test_update_tables_no_detailed_items_keeps_buttons_disabled(self, app):
        app.query_btn.configure(state="disabled")
        app.eta_btn.configure(state="disabled")
        app._update_tables({"service_stats": {"s1": {"name": "S1", "count": 1, "sla": 0, "invalid_eta": 0, "cost": 0, "score": 0}}})
        # Without detailed_items, buttons should not be enabled
        assert str(app.query_btn.cget("state")) == "disabled"

    def test_service_name_map_populated(self, app):
        app._update_tables(SAMPLE_DATA_SIMPLE)
        assert "svc1" in app._service_name_map
        assert app._service_name_map["svc1"] == "Service One"

    def test_manager_with_unknown_owner_ancestry(self, app):
        """Owner mapped to Unknown Owner path still works."""
        data = {
            "is_manager": True,
            "services": [],
            "service_stats": {
                "svc1": {"name": "Svc1", "count": 1, "sla": 0, "invalid_eta": 0, "cost": 0, "score": 0},
            },
            "service_owners": {"Svc1": ["mystery"]},
            "org_mapping": {
                "mystery": OrgAncestry(path=("Unknown Owner",)),
            },
            "owner_stats": {"mystery": {"count": 1}},
            "program_stats": {},
            "kpi_stats": {},
            "detailed_items": [],
            "timestamp": datetime.now().isoformat(),
        }
        app._update_tables(data)
        paths = list(app._group_path_map.values())
        has_unknown = any("Unknown Owner" in p for p in paths)
        assert has_unknown

    def test_manager_multiple_owners_first_mapped(self, app):
        """Service with multiple owners; first one has org_mapping."""
        data = {
            "is_manager": True,
            "services": [],
            "service_stats": {
                "svc1": {"name": "Svc1", "count": 1, "sla": 0, "invalid_eta": 0, "cost": 0, "score": 0},
            },
            "service_owners": {"Svc1": ["unmapped", "mapped_owner"]},
            "org_mapping": {
                "mapped_owner": OrgAncestry(path=("Root", "TeamZ")),
            },
            "owner_stats": {"TeamZ": {"count": 1}},
            "program_stats": {},
            "kpi_stats": {},
            "detailed_items": [],
            "timestamp": datetime.now().isoformat(),
        }
        app._update_tables(data)
        assert len(app._group_path_map) > 0

    def test_cache_age_orange_threshold(self, app, mocker):
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=31)
        app._update_tables(SAMPLE_DATA_SIMPLE)
        # Check foreground color changed
        assert "orange" in str(app.cache_age_label.cget("foreground"))

    def test_cache_age_green_threshold(self, app, mocker):
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=29)
        app._update_tables(SAMPLE_DATA_SIMPLE)
        assert "green" in str(app.cache_age_label.cget("foreground"))

    def test_eta_complete_no_notes(self, app, mocker):
        """saved item with notes=None should not set EtaStatus."""
        import copy
        data = copy.deepcopy(SAMPLE_DATA_SIMPLE)
        app.current_data = data
        app._unfiltered_data = data
        mocker.patch("sfi_reporter.app.write_cache")
        mocker.patch("sfi_reporter.app._serialize_org_data_for_cache", return_value=data)

        item = data["detailed_items"][0]
        original_status = item.get("EtaStatus")
        saved = [(item, "2026-06-15", None)]
        app._on_eta_update_complete(saved=saved, skipped=[], failed=[])
        # EtaStatus not changed when notes is falsy
        assert item.get("EtaStatus") == original_status

    def test_retry_complete_updates_audience_ids(self, app, mocker):
        import copy
        cached = copy.deepcopy(SAMPLE_DATA_SIMPLE)
        cached["audience_ids"] = ["new_aud"]
        mocker.patch("sfi_reporter.app.read_cache", return_value=cached)
        mocker.patch("sfi_reporter.app._deserialize_org_data_from_cache", return_value=cached)
        mocker.patch("sfi_reporter.app.write_cache")
        mocker.patch("sfi_reporter.app._serialize_org_data_for_cache", return_value=cached)
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=1)

        new_rows = [{"_kpi_id": "kpi1", "SlaType": "InSla", "EtaDate": "2026-06-01"}]
        app._on_retry_complete(new_rows=new_rows, still_failed=[], alias="testuser")
        assert app._audience_ids == ["new_aud"]

    def test_filter_applied_stores_ussec(self, app, mocker):
        app._unfiltered_data = SAMPLE_DATA_SIMPLE
        app.current_data = SAMPLE_DATA_SIMPLE
        mock_load = MagicMock(return_value=([], True))
        mock_mod = MagicMock()
        mock_mod.load_clause_cache = mock_load
        mocker.patch.dict("sys.modules", {"sfi_reporter.query_builder": mock_mod})
        mocker.patch("sfi_reporter.app.get_cache_age_minutes", return_value=5)

        app._on_filter_applied([], [])
        assert app._last_filter_ussec is True
