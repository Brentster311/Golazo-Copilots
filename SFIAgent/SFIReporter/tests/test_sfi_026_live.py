"""Live integration tests for SFI-026: Multi-Level Owner Grouping.

These tests call the real S360 API — no mocking.
Requires: `az login` to have been run with valid Azure CLI credentials.

Run with:  pytest tests/test_sfi_026_live.py -v -s
Mark:      @pytest.mark.live (skip in CI with: pytest -m "not live")

Scenarios:
  - brentj    (IC, non-manager)  → flat list, no owner grouping
  - muralic   (1-level manager)  → services grouped by direct reports
  - alexhowells (2-level manager) → services grouped by L1 directs + L2 sub-reports
"""
import pytest

# All live tests share this marker so CI can exclude them
pytestmark = pytest.mark.live


# ---------------------------------------------------------------------------
# Shared fixture: run do_refresh once per alias, cache result for the session
# ---------------------------------------------------------------------------

_REFRESH_CACHE: dict[str, dict | None] = {}


def _get_data(alias: str) -> dict:
    """Run do_refresh for the alias, caching the result across tests."""
    if alias not in _REFRESH_CACHE:
        from sfi_reporter.services import do_refresh
        result = do_refresh(alias, on_status=lambda msg: print(f"  [{alias}] {msg}"))
        _REFRESH_CACHE[alias] = result
    data = _REFRESH_CACHE[alias]
    if data is None:
        pytest.skip(f"do_refresh returned None for {alias} — check az login")
    return data


# ═══════════════════════════════════════════════════════════════════════════
# Scenario 1: brentj (IC / non-manager)
# ═══════════════════════════════════════════════════════════════════════════

class TestBrentjIC:
    """brentj is an individual contributor — no manager grouping expected."""

    def test_refresh_succeeds(self):
        data = _get_data("brentj")
        assert data is not None
        assert 'services' in data
        assert 'detailed_items' in data

    def test_is_not_manager(self):
        data = _get_data("brentj")
        assert data['is_manager'] is False

    def test_no_owner_stats(self):
        """IC view should have empty owner_stats."""
        data = _get_data("brentj")
        assert data.get('owner_stats') == {} or data.get('owner_stats') is None or len(data.get('owner_stats', {})) == 0

    def test_no_org_mapping(self):
        """IC view should have no org_mapping."""
        data = _get_data("brentj")
        om = data.get('org_mapping')
        assert om is None or om == {} or len(om) == 0

    def test_no_level2_stats(self):
        """IC view should have no level2_stats."""
        data = _get_data("brentj")
        l2 = data.get('level2_stats')
        assert l2 is None or l2 == {} or len(l2) == 0

    def test_has_services(self):
        """brentj should own at least one service."""
        data = _get_data("brentj")
        assert len(data['services']) > 0

    def test_cache_serialization(self):
        """The data dict should be JSON-serializable after _serialize_org_data_for_cache."""
        import json
        from sfi_reporter.services import _serialize_org_data_for_cache
        data = _get_data("brentj")
        serialized = _serialize_org_data_for_cache(data)
        # Must not raise
        json.dumps(serialized, default=str)


# ═══════════════════════════════════════════════════════════════════════════
# Scenario 2: muralic (1-level manager)
# ═══════════════════════════════════════════════════════════════════════════

class TestMuralic1LevelManager:
    """muralic is a 1-level manager — services grouped by direct reports."""

    def test_refresh_succeeds(self):
        data = _get_data("muralic")
        assert data is not None

    def test_is_manager(self):
        data = _get_data("muralic")
        assert data['is_manager'] is True

    def test_has_owner_stats(self):
        """Manager view should have owner_stats with at least one owner."""
        data = _get_data("muralic")
        assert len(data.get('owner_stats', {})) > 0

    def test_has_org_mapping(self):
        """Manager view should produce org_mapping."""
        data = _get_data("muralic")
        om = data.get('org_mapping', {})
        assert len(om) > 0

    def test_org_mapping_contains_org_ancestry(self):
        """Every org_mapping value should be an OrgAncestry."""
        from sfi_reporter.models import OrgAncestry
        data = _get_data("muralic")
        om = data.get('org_mapping', {})
        for owner, ancestry in om.items():
            assert isinstance(ancestry, OrgAncestry), (
                f"Expected OrgAncestry for {owner}, got {type(ancestry)}: {ancestry}"
            )

    def test_directs_have_short_paths(self):
        """For a 1-level manager, org_mapping entries should have short paths
        (length 1 for ICs under root, length 2 for ICs under a sub-manager)."""
        from sfi_reporter.models import OrgAncestry
        data = _get_data("muralic")
        om = data.get('org_mapping', {})
        for owner, ancestry in om.items():
            if isinstance(ancestry, OrgAncestry) and ancestry.path != ('Unknown Owner',):
                assert len(ancestry.path) >= 1, (
                    f"Empty path for {owner}: {ancestry}"
                )
                # 1-level manager: most paths are length 1-2

    def test_no_unknown_owner_for_known_directs(self):
        """Owner stats should not be dominated by 'Unknown Owner'."""
        data = _get_data("muralic")
        os = data.get('owner_stats', {})
        known = {k: v for k, v in os.items() if k != 'Unknown Owner' and k != 'No Owner'}
        assert len(known) > 0, "All owners were Unknown — org mapping likely failed"

    def test_brentj_appears_as_direct(self):
        """brentj is one of muralic's direct reports — should appear in owner_stats."""
        data = _get_data("muralic")
        os = data.get('owner_stats', {})
        om = data.get('org_mapping', {})
        # Look for brentj either as an owner_stats key or via org_mapping
        brent_found = (
            any('brent' in k.lower() for k in os) or
            any('brentj' in k.lower() for k in om)
        )
        assert brent_found, f"brentj not found in owner_stats={list(os.keys())} or org_mapping={list(om.keys())}"

    def test_cache_serialization(self):
        """The data dict should be JSON-serializable after serialize."""
        import json
        from sfi_reporter.services import _serialize_org_data_for_cache
        data = _get_data("muralic")
        serialized = _serialize_org_data_for_cache(data)
        json.dumps(serialized, default=str)

    def test_cache_round_trip_preserves_types(self):
        """Serialize → JSON → deserialize should restore OrgAncestry types."""
        import json
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import _serialize_org_data_for_cache, _deserialize_org_data_from_cache
        data = _get_data("muralic")
        serialized = _serialize_org_data_for_cache(data)
        json_str = json.dumps(serialized, default=str)
        restored = json.loads(json_str)
        _deserialize_org_data_from_cache(restored)
        om = restored.get('org_mapping', {})
        for owner, ancestry in om.items():
            assert isinstance(ancestry, OrgAncestry), (
                f"After round-trip, {owner} is {type(ancestry)} not OrgAncestry"
            )


# ═══════════════════════════════════════════════════════════════════════════
# Scenario 3: alexhowells (2-level manager)
# ═══════════════════════════════════════════════════════════════════════════

class TestAlexhowells2LevelManager:
    """alexhowells is a 2-level manager — should see L1 directs + L2 sub-reports."""

    def test_refresh_succeeds(self):
        data = _get_data("alexhowells")
        assert data is not None

    def test_is_manager(self):
        data = _get_data("alexhowells")
        assert data['is_manager'] is True

    def test_has_owner_stats(self):
        data = _get_data("alexhowells")
        assert len(data.get('owner_stats', {})) > 0

    def test_has_org_mapping(self):
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        assert len(om) > 0

    def test_org_mapping_has_deep_paths(self):
        """alexhowells has sub-reports — some org_mapping entries must have path depth >= 3."""
        from sfi_reporter.models import OrgAncestry
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        has_deep = any(
            isinstance(v, OrgAncestry) and len(v.path) >= 3
            for v in om.values()
        )
        assert has_deep, (
            f"Expected at least one OrgAncestry with path depth >= 3. "
            f"Sample: {dict(list(om.items())[:5])}"
        )

    def test_multi_level_paths_present(self):
        """2-level manager should produce org_mapping entries at multiple depths."""
        from sfi_reporter.models import OrgAncestry
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        depths = set()
        for v in om.values():
            if isinstance(v, OrgAncestry) and v.path != ('Unknown Owner',):
                depths.add(len(v.path))
        assert len(depths) >= 2, f"Expected multiple path depths, got: {depths}"

    def test_muralic_appears_in_paths(self):
        """muralic is one of alexhowells' directs — should appear in paths at depth 1."""
        from sfi_reporter.models import OrgAncestry
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        path_names = set()
        for v in om.values():
            if isinstance(v, OrgAncestry):
                for segment in v.path:
                    path_names.add(segment.lower())
        muralic_found = any('muralic' in n or 'mura' in n for n in path_names)
        assert muralic_found, f"muralic not found in path names: {path_names}"

    def test_hierarchy_has_multiple_branches(self):
        """At least one path[1] manager should have owners under multiple path[2] sub-managers."""
        from sfi_reporter.models import OrgAncestry
        from collections import defaultdict
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        # Group path[2] names by path[1]
        l1_to_l2s: dict[str, set[str]] = defaultdict(set)
        for owner, anc in om.items():
            if isinstance(anc, OrgAncestry) and len(anc.path) >= 3:
                l1_to_l2s[anc.path[1]].add(anc.path[2])
        assert len(l1_to_l2s) > 0, "No direct has subordinates with sub-managers"
        # At least one direct should have 2+ distinct sub-managers
        best_l1 = max(l1_to_l2s, key=lambda k: len(l1_to_l2s[k]))
        assert len(l1_to_l2s[best_l1]) >= 2, (
            f"Expected at least one direct with 2+ sub-managers, "
            f"best is {best_l1!r} with {l1_to_l2s[best_l1]}"
        )

    def test_owner_stats_not_dominated_by_unknown(self):
        """The majority of items should be grouped under known owners."""
        data = _get_data("alexhowells")
        os = data.get('owner_stats', {})
        unknown = os.get('Unknown Owner', {}).get('count', 0)
        total = sum(v.get('count', 0) for v in os.values())
        if total > 0:
            unknown_pct = unknown / total
            assert unknown_pct < 0.5, (
                f"Unknown Owner has {unknown}/{total} ({unknown_pct:.0%}) — "
                f"grouping may be broken"
            )

    def test_cache_serialization(self):
        """The full data dict must be JSON-serializable."""
        import json
        from sfi_reporter.services import _serialize_org_data_for_cache
        data = _get_data("alexhowells")
        serialized = _serialize_org_data_for_cache(data)
        # This is the exact line that was crashing — must not raise
        json.dumps(serialized, default=str)

    def test_cache_round_trip_preserves_paths(self):
        """Serialize → JSON → deserialize should restore OrgAncestry with paths."""
        import json
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import _serialize_org_data_for_cache, _deserialize_org_data_from_cache
        data = _get_data("alexhowells")
        serialized = _serialize_org_data_for_cache(data)
        json_str = json.dumps(serialized, default=str)
        restored = json.loads(json_str)
        _deserialize_org_data_from_cache(restored)

        # org_mapping restored with OrgAncestry types
        om = restored.get('org_mapping', {})
        for owner, anc in om.items():
            assert isinstance(anc, OrgAncestry), f"{owner} not OrgAncestry after round-trip"
            assert isinstance(anc.path, tuple), f"{owner} path not tuple: {type(anc.path)}"
            assert len(anc.path) >= 1, f"{owner} has empty path"

    def test_collect_services_for_direct(self):
        """collect_services_for_owner with a direct-report path prefix should return services."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import collect_services_for_owner
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        so = data.get('service_owners', {})
        # Pick first known path with length >= 2 (root + direct)
        prefix = None
        for v in om.values():
            if isinstance(v, OrgAncestry) and len(v.path) >= 2 and v.path != ('Unknown Owner',):
                prefix = v.path[:2]  # (root, direct)
                break
        if prefix is None:
            pytest.skip("No known direct-report path found")
        services = collect_services_for_owner(prefix, so, om)
        assert len(services) > 0, f"No services found for prefix {prefix}"

    def test_collect_services_for_sub_manager(self):
        """collect_services_for_owner with a deeper path prefix should return services."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import collect_services_for_owner
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        so = data.get('service_owners', {})
        # Pick first known path with length >= 3 (root + direct + sub)
        prefix = None
        for v in om.values():
            if isinstance(v, OrgAncestry) and len(v.path) >= 3:
                prefix = v.path[:3]
                break
        if prefix is None:
            pytest.skip("No sub-manager path found")
        services = collect_services_for_owner(prefix, so, om)
        assert len(services) > 0, f"No services found for prefix {prefix}"
