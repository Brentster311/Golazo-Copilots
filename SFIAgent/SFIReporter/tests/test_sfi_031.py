"""Tests for SFI-031: Cache org-tree in get_org_mapping.

TDD red phase — tests written before production changes.
Tests verify:
- Cache miss → calls get_org_tree, writes cache file
- Cache hit (< 24 hr) → no API call
- Stale cache (> 24 hr) → calls get_org_tree, overwrites
- Corrupt/empty cache → fallback to API
- API failure → no cache written, all Unknown Owner
- Cache key lowercased
- Round-trip serialization fidelity
"""
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from accia_s360.models import OrgPerson, OrgTree


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _person(alias: str, display_name: str, **kw) -> OrgPerson:
    return OrgPerson(alias=alias, display_name=display_name, **kw)


def _tree(alias: str, display_name: str, children: list | None = None) -> OrgTree:
    return OrgTree(person=_person(alias, display_name), direct_reports=children or [])


def _simple_tree() -> OrgTree:
    """A 2-level tree: root → child_mgr → leaf_ic."""
    return _tree("root", "Root Manager", [
        _tree("mgr1", "Manager One", [
            _tree("ic1", "IC One"),
        ]),
        _tree("ic2", "IC Two"),
    ])


def _three_level_tree() -> OrgTree:
    """A 3-level tree for round-trip fidelity testing."""
    return _tree("top", "Top Boss", [
        _tree("mid", "Middle Manager", [
            _tree("low", "Low Manager", [
                _tree("leaf", "Leaf Worker"),
            ]),
        ]),
    ])


# ---------------------------------------------------------------------------
# Org-tree cache serialization round-trip
# ---------------------------------------------------------------------------

class TestOrgTreeCacheSerialization:
    """TC-8: Round-trip serialization fidelity."""

    def test_round_trip_simple_tree(self, tmp_path):
        """Serialize → write → read → deserialize preserves full structure."""
        from sfi_reporter.services import _serialize_org_tree, _deserialize_org_tree

        tree = _simple_tree()
        serialized = _serialize_org_tree(tree)
        restored = _deserialize_org_tree(serialized)

        assert restored.person.alias == "root"
        assert restored.person.display_name == "Root Manager"
        assert len(restored.direct_reports) == 2
        assert restored.direct_reports[0].person.alias == "mgr1"
        assert len(restored.direct_reports[0].direct_reports) == 1
        assert restored.direct_reports[0].direct_reports[0].person.alias == "ic1"

    def test_round_trip_three_level_tree(self, tmp_path):
        """3-level nesting round-trips correctly."""
        from sfi_reporter.services import _serialize_org_tree, _deserialize_org_tree

        tree = _three_level_tree()
        serialized = _serialize_org_tree(tree)
        restored = _deserialize_org_tree(serialized)

        leaf = restored.direct_reports[0].direct_reports[0].direct_reports[0]
        assert leaf.person.alias == "leaf"
        assert leaf.person.display_name == "Leaf Worker"
        assert leaf.direct_reports == []

    def test_round_trip_preserves_optional_fields(self):
        """job_title, department, object_id are preserved."""
        from sfi_reporter.services import _serialize_org_tree, _deserialize_org_tree

        tree = OrgTree(
            person=OrgPerson(
                alias="a1", display_name="Alice",
                job_title="Engineer", department="Infra", object_id="obj-123",
            ),
            direct_reports=[],
        )
        restored = _deserialize_org_tree(_serialize_org_tree(tree))
        assert restored.person.job_title == "Engineer"
        assert restored.person.department == "Infra"
        assert restored.person.object_id == "obj-123"


# ---------------------------------------------------------------------------
# Cache miss / hit / stale / corrupt tests
# ---------------------------------------------------------------------------

class TestOrgTreeCacheInGetOrgMapping:
    """Tests for org-tree caching within get_org_mapping."""

    @patch("sfi_reporter.services.get_cache_dir")
    @patch("sfi_reporter.data.get_client")
    def test_tc01_cache_miss_calls_api_and_writes_cache(self, mock_get_client, mock_cache_dir, tmp_path):
        """TC-1: No cache file → calls get_org_tree, writes cache."""
        from sfi_reporter.services import get_org_mapping

        mock_cache_dir.return_value = tmp_path
        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _simple_tree()
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["IC One"], "RootAlias")

        mock_client.get_org_tree.assert_called_once_with("rootalias")

        # Cache file should exist
        cache_file = tmp_path / "rootalias_org_tree.json"
        assert cache_file.exists(), "Expected org-tree cache file to be written on first call"

        data = json.loads(cache_file.read_text(encoding="utf-8"))
        assert "timestamp" in data
        assert "tree" in data

    @patch("sfi_reporter.services.get_cache_dir")
    @patch("sfi_reporter.data.get_client")
    def test_tc02_cache_hit_skips_api(self, mock_get_client, mock_cache_dir, tmp_path):
        """TC-2: Valid cache (< 24 hr) → no API call."""
        from sfi_reporter.services import get_org_mapping, _serialize_org_tree

        mock_cache_dir.return_value = tmp_path
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Pre-write valid cache
        cache_file = tmp_path / "rootalias_org_tree.json"
        cache_data = {
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "manager_alias": "rootalias",
            "tree": _serialize_org_tree(_simple_tree()),
        }
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")

        result = get_org_mapping(["IC One"], "RootAlias")

        mock_client.get_org_tree.assert_not_called(), "Expected cache hit to skip get_org_tree call"

    @patch("sfi_reporter.services.get_cache_dir")
    @patch("sfi_reporter.data.get_client")
    def test_tc03_stale_cache_calls_api(self, mock_get_client, mock_cache_dir, tmp_path):
        """TC-3: Cache older than 24 hours → calls API, overwrites."""
        from sfi_reporter.services import get_org_mapping, _serialize_org_tree

        mock_cache_dir.return_value = tmp_path
        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _simple_tree()
        mock_get_client.return_value = mock_client

        # Pre-write stale cache (25 hours old)
        cache_file = tmp_path / "rootalias_org_tree.json"
        cache_data = {
            "timestamp": (datetime.now() - timedelta(hours=25)).isoformat(),
            "manager_alias": "rootalias",
            "tree": _serialize_org_tree(_simple_tree()),
        }
        cache_file.write_text(json.dumps(cache_data), encoding="utf-8")

        result = get_org_mapping(["IC One"], "RootAlias")

        mock_client.get_org_tree.assert_called_once(), "Expected stale cache to trigger fresh get_org_tree call"

        # Cache should be overwritten with fresh timestamp
        new_data = json.loads(cache_file.read_text(encoding="utf-8"))
        new_ts = datetime.fromisoformat(new_data["timestamp"])
        assert (datetime.now() - new_ts).total_seconds() < 60, "Cache should have fresh timestamp"

    @patch("sfi_reporter.services.get_cache_dir")
    @patch("sfi_reporter.data.get_client")
    def test_tc04_corrupt_cache_falls_back_to_api(self, mock_get_client, mock_cache_dir, tmp_path):
        """TC-4: Corrupt/empty cache file → fallback to API."""
        from sfi_reporter.services import get_org_mapping

        mock_cache_dir.return_value = tmp_path
        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _simple_tree()
        mock_get_client.return_value = mock_client

        # Write corrupt cache
        cache_file = tmp_path / "rootalias_org_tree.json"
        cache_file.write_text("not valid json {{{", encoding="utf-8")

        result = get_org_mapping(["IC One"], "RootAlias")

        mock_client.get_org_tree.assert_called_once(), "Expected corrupt cache to trigger fallback to get_org_tree"

    @patch("sfi_reporter.services.get_cache_dir")
    @patch("sfi_reporter.data.get_client")
    def test_tc04b_empty_cache_falls_back_to_api(self, mock_get_client, mock_cache_dir, tmp_path):
        """TC-4b: Empty cache file → fallback to API."""
        from sfi_reporter.services import get_org_mapping

        mock_cache_dir.return_value = tmp_path
        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _simple_tree()
        mock_get_client.return_value = mock_client

        cache_file = tmp_path / "rootalias_org_tree.json"
        cache_file.write_text("", encoding="utf-8")

        result = get_org_mapping(["IC One"], "RootAlias")

        mock_client.get_org_tree.assert_called_once()

    @patch("sfi_reporter.services.get_cache_dir")
    @patch("sfi_reporter.data.get_client")
    def test_tc05_api_failure_no_cache_written(self, mock_get_client, mock_cache_dir, tmp_path):
        """TC-5: API exception → no cache written, all Unknown Owner."""
        from sfi_reporter.services import get_org_mapping
        from sfi_reporter.models import OrgAncestry

        mock_cache_dir.return_value = tmp_path
        mock_client = MagicMock()
        mock_client.get_org_tree.side_effect = Exception("Graph API down")
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Alice", "Bob"], "RootAlias")

        # All owners should be Unknown
        for name in ["Alice", "Bob"]:
            assert result[name] == OrgAncestry(path=("Unknown Owner",))

        # No cache file should exist
        cache_file = tmp_path / "rootalias_org_tree.json"
        assert not cache_file.exists(), "Expected API failure to skip cache write"

    @patch("sfi_reporter.services.get_cache_dir")
    @patch("sfi_reporter.data.get_client")
    def test_tc07_cache_key_lowercased(self, mock_get_client, mock_cache_dir, tmp_path):
        """TC-7: Cache key is lowercased regardless of input case."""
        from sfi_reporter.services import get_org_mapping

        mock_cache_dir.return_value = tmp_path
        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _simple_tree()
        mock_get_client.return_value = mock_client

        get_org_mapping(["IC One"], "BrentJ")

        # get_org_tree should be called with lowercased alias
        mock_client.get_org_tree.assert_called_once_with("brentj")

        # The cache file written should have the lowercase key in its name
        files_on_disk = [f.name for f in tmp_path.iterdir() if f.suffix == ".json"]
        assert "brentj_org_tree.json" in files_on_disk, "Expected cache key to be lowercased"

    @patch("sfi_reporter.services.get_cache_dir")
    @patch("sfi_reporter.data.get_client")
    def test_mapping_result_same_with_cache(self, mock_get_client, mock_cache_dir, tmp_path):
        """Mapping result is identical whether from cache or from API."""
        from sfi_reporter.services import get_org_mapping, _serialize_org_tree

        mock_cache_dir.return_value = tmp_path
        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _simple_tree()
        mock_get_client.return_value = mock_client

        # First call — cache miss
        result_miss = get_org_mapping(["IC One", "Manager One"], "RootAlias")

        # Second call — cache hit
        mock_client.get_org_tree.reset_mock()
        result_hit = get_org_mapping(["IC One", "Manager One"], "RootAlias")

        mock_client.get_org_tree.assert_not_called()
        assert result_miss == result_hit, "Cached result should produce identical mapping"
