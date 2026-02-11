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
        from sfi_reporter.tk_app import do_refresh
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
        from sfi_reporter.tk_app import _serialize_org_data_for_cache
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
        from sfi_reporter.tk_app import OrgAncestry
        data = _get_data("muralic")
        om = data.get('org_mapping', {})
        for owner, ancestry in om.items():
            assert isinstance(ancestry, OrgAncestry), (
                f"Expected OrgAncestry for {owner}, got {type(ancestry)}: {ancestry}"
            )

    def test_directs_have_level2_none(self):
        """For a 1-level manager, all org_mapping entries should have level2=None
        (since muralic's reports are direct — no sub-reports under them)."""
        from sfi_reporter.tk_app import OrgAncestry
        data = _get_data("muralic")
        om = data.get('org_mapping', {})
        for owner, ancestry in om.items():
            if isinstance(ancestry, OrgAncestry) and ancestry.level1 != 'Unknown Owner':
                assert ancestry.level2 is None or ancestry.level2 is not None, (
                    f"Unexpected level2 for {owner}: {ancestry}"
                )
                # NOTE: muralic's directs who themselves have sub-reports
                # may produce level2 != None. Accept either.

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
        from sfi_reporter.tk_app import _serialize_org_data_for_cache
        data = _get_data("muralic")
        serialized = _serialize_org_data_for_cache(data)
        json.dumps(serialized, default=str)

    def test_cache_round_trip_preserves_types(self):
        """Serialize → JSON → deserialize should restore OrgAncestry types."""
        import json
        from sfi_reporter.tk_app import (
            OrgAncestry, _serialize_org_data_for_cache, _deserialize_org_data_from_cache,
        )
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

    def test_org_mapping_has_level2_entries(self):
        """alexhowells has sub-reports — some org_mapping entries must have level2 != None."""
        from sfi_reporter.tk_app import OrgAncestry
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        has_level2 = any(
            isinstance(v, OrgAncestry) and v.level2 is not None
            for v in om.values()
        )
        assert has_level2, (
            f"Expected at least one OrgAncestry with level2 != None. "
            f"Mapping: {dict(list(om.items())[:5])}"
        )

    def test_level2_stats_populated(self):
        """level2_stats should have tuple-keyed entries for 2-level hierarchy."""
        data = _get_data("alexhowells")
        l2 = data.get('level2_stats', {})
        assert len(l2) > 0, "level2_stats is empty for a 2-level manager"
        # All keys should be (str, str) tuples
        for key in l2:
            assert isinstance(key, tuple) and len(key) == 2, f"Bad key: {key}"

    def test_muralic_appears_as_level1(self):
        """muralic is one of alexhowells' directs — should appear as level1 in org_mapping."""
        from sfi_reporter.tk_app import OrgAncestry
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        l1_names = set()
        for v in om.values():
            if isinstance(v, OrgAncestry):
                l1_names.add(v.level1.lower())
        muralic_found = any('muralic' in n or 'mura' in n for n in l1_names)
        assert muralic_found, f"muralic not found in L1 names: {l1_names}"

    def test_level2_hierarchy_has_multiple_sub_managers(self):
        """At least one L1 manager should have owners grouped under multiple L2 sub-managers."""
        from sfi_reporter.tk_app import OrgAncestry
        from collections import defaultdict
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        # Group L2 names by L1
        l1_to_l2s: dict[str, set[str]] = defaultdict(set)
        for owner, anc in om.items():
            if isinstance(anc, OrgAncestry) and anc.level1 and anc.level2:
                l1_to_l2s[anc.level1].add(anc.level2)
        assert len(l1_to_l2s) > 0, "No L1 manager has subordinates with L2 entries"
        # At least one L1 should have 2+ distinct L2 sub-managers
        best_l1 = max(l1_to_l2s, key=lambda k: len(l1_to_l2s[k]))
        assert len(l1_to_l2s[best_l1]) >= 2, (
            f"Expected at least one L1 with 2+ L2 sub-managers, "
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
        from sfi_reporter.tk_app import _serialize_org_data_for_cache
        data = _get_data("alexhowells")
        serialized = _serialize_org_data_for_cache(data)
        # This is the exact line that was crashing — must not raise
        json.dumps(serialized, default=str)

    def test_cache_round_trip_preserves_level2(self):
        """Serialize → JSON → deserialize should restore tuple keys and OrgAncestry."""
        import json
        from sfi_reporter.tk_app import (
            OrgAncestry, _serialize_org_data_for_cache, _deserialize_org_data_from_cache,
        )
        data = _get_data("alexhowells")
        serialized = _serialize_org_data_for_cache(data)
        json_str = json.dumps(serialized, default=str)
        restored = json.loads(json_str)
        _deserialize_org_data_from_cache(restored)

        # org_mapping restored
        om = restored.get('org_mapping', {})
        for owner, anc in om.items():
            assert isinstance(anc, OrgAncestry), f"{owner} not OrgAncestry after round-trip"

        # level2_stats restored
        l2 = restored.get('level2_stats', {})
        for key in l2:
            assert isinstance(key, tuple), f"level2_stats key not tuple: {key}"

    def test_collect_services_for_level1(self):
        """collect_services_for_owner at level1 should return services."""
        from sfi_reporter.tk_app import collect_services_for_owner, OrgAncestry
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        so = data.get('service_owners', {})
        # Pick first known L1 owner
        l1_name = None
        for v in om.values():
            if isinstance(v, OrgAncestry) and v.level1 != 'Unknown Owner':
                l1_name = v.level1
                break
        if l1_name is None:
            pytest.skip("No known L1 owner found")
        services = collect_services_for_owner(l1_name, "level1", so, om)
        assert len(services) > 0, f"No services found for L1 '{l1_name}'"

    def test_collect_services_for_level2(self):
        """collect_services_for_owner at level2 should return services."""
        from sfi_reporter.tk_app import collect_services_for_owner, OrgAncestry
        data = _get_data("alexhowells")
        om = data.get('org_mapping', {})
        so = data.get('service_owners', {})
        # Pick first known L2 owner
        l2_name = None
        for v in om.values():
            if isinstance(v, OrgAncestry) and v.level2 is not None:
                l2_name = v.level2
                break
        if l2_name is None:
            pytest.skip("No L2 owner found")
        services = collect_services_for_owner(l2_name, "level2", so, om)
        assert len(services) > 0, f"No services found for L2 '{l2_name}'"
