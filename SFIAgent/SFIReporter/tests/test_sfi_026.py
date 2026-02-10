"""Tests for SFI-026: Multi-Level Owner Grouping in Services Table.

TDD red phase — tests written before implementation.
Tests cover:
- OrgAncestry NamedTuple
- get_org_mapping() with multi-level chains
- aggregate_by_owner() with OrgAncestry tuples
- level2 aggregation
- Backward compatibility with 1-level managers
"""
import pytest
from unittest.mock import MagicMock, patch, call
import json


# ---------------------------------------------------------------------------
# 1. OrgAncestry NamedTuple
# ---------------------------------------------------------------------------

class TestOrgAncestry:
    """Verify the OrgAncestry type exists and behaves correctly."""

    def test_creation_with_level2(self):
        from sfi_reporter.tk_app import OrgAncestry
        a = OrgAncestry(level1="Muralic Name", level2="Brent Jensen")
        assert a.level1 == "Muralic Name"
        assert a.level2 == "Brent Jensen"

    def test_creation_level2_none(self):
        from sfi_reporter.tk_app import OrgAncestry
        a = OrgAncestry(level1="Muralic Name", level2=None)
        assert a.level1 == "Muralic Name"
        assert a.level2 is None

    def test_tuple_unpacking(self):
        from sfi_reporter.tk_app import OrgAncestry
        a = OrgAncestry(level1="L1", level2="L2")
        l1, l2 = a
        assert l1 == "L1"
        assert l2 == "L2"

    def test_unknown_owner(self):
        from sfi_reporter.tk_app import OrgAncestry
        a = OrgAncestry(level1="Unknown Owner", level2=None)
        assert a.level1 == "Unknown Owner"
        assert a.level2 is None


# ---------------------------------------------------------------------------
# Helpers for mocking S360 search results
# ---------------------------------------------------------------------------

def _make_org_result(alias: str, display_name: str, managers: list[str]) -> dict:
    """Build a mock S360 search result for an Org entry."""
    return {
        "Group": "Org",
        "Id": alias,
        "Owners": display_name,
        "Name": display_name,
        "Managers": json.dumps(managers),
    }


def _build_search_side_effect(people: dict[str, dict]) -> callable:
    """Build a side_effect for client.search() given a people registry.
    
    people: {display_name_lower: {alias, display_name, managers}}
    Also matches by alias (for name resolution lookups).
    """
    def search(query: str):
        q = query.lower()
        results = []
        for key, info in people.items():
            if q == key or q == info["alias"].lower():
                results.append(_make_org_result(
                    info["alias"], info["display_name"], info["managers"]
                ))
        return results
    return search


# ---------------------------------------------------------------------------
# 2. get_org_mapping() — Multi-Level Mapping
# ---------------------------------------------------------------------------

class TestGetOrgMappingMultiLevel:
    """Tests for get_org_mapping returning OrgAncestry tuples."""

    def _people_registry(self):
        """Build a test org: alexhowells → muralic → brentj → deepPerson."""
        return {
            "alex howells": {
                "alias": "alexhowells",
                "display_name": "Alex Howells",
                "managers": ["ceo", "vp"],  # alexhowells' managers
            },
            "muralic name": {
                "alias": "muralic",
                "display_name": "Muralic Name",
                "managers": ["ceo", "vp", "alexhowells"],
            },
            "brent jensen": {
                "alias": "brentj",
                "display_name": "Brent Jensen",
                "managers": ["ceo", "vp", "alexhowells", "muralic"],
            },
            "deep person": {
                "alias": "deepperson",
                "display_name": "Deep Person",
                "managers": ["ceo", "vp", "alexhowells", "muralic", "brentj"],
            },
            "external person": {
                "alias": "external",
                "display_name": "External Person",
                "managers": ["ceo", "othervp", "otherdir"],  # Not under alexhowells
            },
        }

    @patch("sfi_reporter.data.get_client")
    def test_tc_1_1_owner_two_levels_deep(self, mock_get_client):
        """TC-1.1: Owner 2 levels below manager → (direct, sub-report)."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.search.side_effect = _build_search_side_effect(self._people_registry())
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Brent Jensen"], "alexhowells")

        assert "Brent Jensen" in result
        ancestry = result["Brent Jensen"]
        assert isinstance(ancestry, OrgAncestry), "Return value must be OrgAncestry"
        assert ancestry.level1 == "Muralic Name"
        assert ancestry.level2 == "Brent Jensen"

    @patch("sfi_reporter.data.get_client")
    def test_tc_1_2_owner_is_direct_report(self, mock_get_client):
        """TC-1.2: Owner IS a direct report of viewer → (self, None)."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.search.side_effect = _build_search_side_effect(self._people_registry())
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Muralic Name"], "alexhowells")

        assert "Muralic Name" in result
        ancestry = result["Muralic Name"]
        assert ancestry.level1 == "Muralic Name"
        assert ancestry.level2 is None

    @patch("sfi_reporter.data.get_client")
    def test_tc_1_3_one_level_manager_backward_compat(self, mock_get_client):
        """TC-1.3: 1-level manager → all level2 should be None."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.search.side_effect = _build_search_side_effect(self._people_registry())
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Brent Jensen"], "muralic")

        assert "Brent Jensen" in result
        ancestry = result["Brent Jensen"]
        assert ancestry.level1 == "Brent Jensen"
        assert ancestry.level2 is None, "For 1-level manager, level2 must be None"

    @patch("sfi_reporter.data.get_client")
    def test_tc_1_4_owner_not_in_org(self, mock_get_client):
        """TC-1.4: Owner outside manager's org → ('Unknown Owner', None)."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.search.side_effect = _build_search_side_effect(self._people_registry())
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["External Person"], "alexhowells")

        assert "External Person" in result
        ancestry = result["External Person"]
        assert ancestry.level1 == "Unknown Owner"
        assert ancestry.level2 is None

    @patch("sfi_reporter.data.get_client")
    def test_tc_1_5_manager_own_services(self, mock_get_client):
        """TC-1.5: Manager owning services → (self, None), NOT Unknown Owner."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.search.side_effect = _build_search_side_effect(self._people_registry())
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Alex Howells"], "alexhowells")

        assert "Alex Howells" in result
        ancestry = result["Alex Howells"]
        assert ancestry.level1 == "Alex Howells"
        assert ancestry.level2 is None

    @patch("sfi_reporter.data.get_client")
    def test_tc_1_6_owner_three_levels_deep(self, mock_get_client):
        """TC-1.6: Owner 3+ levels deep → maps to first 2 ancestors only."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.search.side_effect = _build_search_side_effect(self._people_registry())
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Deep Person"], "alexhowells")

        assert "Deep Person" in result
        ancestry = result["Deep Person"]
        # Deep Person → brentj → muralic → alexhowells
        # level1 = muralic (alexhowells' direct), level2 = brentj (muralic's sub-report)
        assert ancestry.level1 == "Muralic Name"
        assert ancestry.level2 == "Brent Jensen"

    def test_tc_1_7_empty_owner_list(self):
        """TC-1.7: Empty owner list returns empty dict."""
        from sfi_reporter.tk_app import get_org_mapping

        result = get_org_mapping([], "alexhowells")
        assert result == {}

    @patch("sfi_reporter.data.get_client")
    def test_tc_1_8_parallel_multiple_owners(self, mock_get_client):
        """TC-1.8: Multiple owners processed in parallel without errors."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.search.side_effect = _build_search_side_effect(self._people_registry())
        mock_get_client.return_value = mock_client

        owners = ["Muralic Name", "Brent Jensen", "Deep Person", "External Person"]
        result = get_org_mapping(owners, "alexhowells")

        assert len(result) == 4
        for name in owners:
            assert name in result
            assert isinstance(result[name], OrgAncestry)


# ---------------------------------------------------------------------------
# 3. aggregate_by_owner() — With OrgAncestry
# ---------------------------------------------------------------------------

class TestAggregateByOwnerWithOrgAncestry:
    """Tests for aggregate_by_owner consuming OrgAncestry tuples."""

    def test_tc_2_1_level1_stats_are_sum_of_children(self):
        """TC-2.1: Level-1 stats equal sum of all Level-2 children."""
        from sfi_reporter.tk_app import aggregate_by_owner, OrgAncestry

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
            {"S360_ServiceTreeServiceName": "Svc B", "SlaType": "OutOfSla", "EtaDate": "2030-01-01"},
            {"S360_ServiceTreeServiceName": "Svc C", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {
            "Svc A": ["Owner1"],
            "Svc B": ["Owner2"],
            "Svc C": ["Owner3"],
        }
        org_mapping = {
            "Owner1": OrgAncestry(level1="Direct A", level2="Owner1"),
            "Owner2": OrgAncestry(level1="Direct A", level2="Owner2"),
            "Owner3": OrgAncestry(level1="Direct B", level2="Owner3"),
        }

        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)

        # Level1 rollup: Direct A has 2 items, Direct B has 1
        assert "Direct A" in result
        assert result["Direct A"]["count"] == 2
        assert "Direct B" in result
        assert result["Direct B"]["count"] == 1

    def test_tc_2_2_sla_and_eta_rollup(self):
        """TC-2.2: SLA and invalid ETA roll up correctly."""
        from sfi_reporter.tk_app import aggregate_by_owner, OrgAncestry

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "OutOfSla", "EtaDate": None},
            {"S360_ServiceTreeServiceName": "Svc B", "SlaType": "InSLA", "EtaDate": "2025-01-01"},
        ]
        service_owners = {
            "Svc A": ["Owner1"],
            "Svc B": ["Owner2"],
        }
        org_mapping = {
            "Owner1": OrgAncestry(level1="Direct A", level2="Owner1"),
            "Owner2": OrgAncestry(level1="Direct A", level2="Owner2"),
        }

        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)

        assert result["Direct A"]["sla"] == 1  # Only 1 OutOfSla
        assert result["Direct A"]["count"] == 2

    def test_tc_2_3_unknown_owner_bucket(self):
        """TC-2.3: Unmapped owners fall into Unknown Owner."""
        from sfi_reporter.tk_app import aggregate_by_owner, OrgAncestry

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {
            "Svc A": ["Unmapped Person"],
        }
        org_mapping = {
            "Unmapped Person": OrgAncestry(level1="Unknown Owner", level2=None),
        }

        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)

        assert "Unknown Owner" in result
        assert result["Unknown Owner"]["count"] == 1

    def test_tc_2_4_one_level_backward_compat(self):
        """TC-2.4: When all level2 are None, behaves like 1-level."""
        from sfi_reporter.tk_app import aggregate_by_owner, OrgAncestry

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
            {"S360_ServiceTreeServiceName": "Svc B", "SlaType": "OutOfSla", "EtaDate": "2030-01-01"},
        ]
        service_owners = {
            "Svc A": ["Owner1"],
            "Svc B": ["Owner2"],
        }
        org_mapping = {
            "Owner1": OrgAncestry(level1="Direct A", level2=None),
            "Owner2": OrgAncestry(level1="Direct B", level2=None),
        }

        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)

        assert "Direct A" in result
        assert result["Direct A"]["count"] == 1
        assert "Direct B" in result
        assert result["Direct B"]["count"] == 1

    def test_existing_string_org_mapping_still_works(self):
        """Regression: Old-style string org_mapping must still work."""
        from sfi_reporter.tk_app import aggregate_by_owner

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {"Svc A": ["Owner1"]}
        org_mapping = {"Owner1": "Direct A"}  # Old string format

        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)

        assert "Direct A" in result
        assert result["Direct A"]["count"] == 1


# ---------------------------------------------------------------------------
# 4. aggregate_by_level2() — Level-2 Stats
# ---------------------------------------------------------------------------

class TestAggregateByLevel2:
    """Tests for level2 aggregation."""

    def test_level2_stats_per_subreport(self):
        """Each level2 sub-report has correct stats."""
        from sfi_reporter.tk_app import aggregate_by_level2, OrgAncestry

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "OutOfSla", "EtaDate": "2030-01-01"},
            {"S360_ServiceTreeServiceName": "Svc B", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
            {"S360_ServiceTreeServiceName": "Svc C", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {
            "Svc A": ["Owner1"],
            "Svc B": ["Owner1"],
            "Svc C": ["Owner2"],
        }
        org_mapping = {
            "Owner1": OrgAncestry(level1="Direct A", level2="Sub1"),
            "Owner2": OrgAncestry(level1="Direct A", level2="Sub2"),
        }

        result = aggregate_by_level2(items, service_owners, org_mapping)

        # Sub1 has 2 items (Svc A + Svc B), Sub2 has 1 item (Svc C)
        assert ("Direct A", "Sub1") in result
        assert result[("Direct A", "Sub1")]["count"] == 2
        assert result[("Direct A", "Sub1")]["sla"] == 1

        assert ("Direct A", "Sub2") in result
        assert result[("Direct A", "Sub2")]["count"] == 1

    def test_level2_none_entries_excluded(self):
        """Entries with level2=None should not appear in level2 stats."""
        from sfi_reporter.tk_app import aggregate_by_level2, OrgAncestry

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {"Svc A": ["DirectOwner"]}
        org_mapping = {
            "DirectOwner": OrgAncestry(level1="DirectOwner", level2=None),
        }

        result = aggregate_by_level2(items, service_owners, org_mapping)

        # No level2 entries since level2 is None
        assert len(result) == 0

    def test_level2_unknown_owner_excluded(self):
        """Unknown Owner entries should not appear in level2 stats."""
        from sfi_reporter.tk_app import aggregate_by_level2, OrgAncestry

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {"Svc A": ["External"]}
        org_mapping = {
            "External": OrgAncestry(level1="Unknown Owner", level2=None),
        }

        result = aggregate_by_level2(items, service_owners, org_mapping)

        assert len(result) == 0


# ---------------------------------------------------------------------------
# 5. Drill-Down Logic — Collect Services by Org Subtree
# ---------------------------------------------------------------------------

class TestDrillDownSubtree:
    """Tests for collecting services by org subtree for drill-down."""

    def test_level1_drilldown_collects_entire_subtree(self):
        """TC-4.1: Level-1 drill-down includes ALL items in subtree."""
        from sfi_reporter.tk_app import collect_services_for_owner, OrgAncestry

        org_mapping = {
            "Owner1": OrgAncestry(level1="Direct A", level2="Sub1"),
            "Owner2": OrgAncestry(level1="Direct A", level2="Sub2"),
            "Owner3": OrgAncestry(level1="Direct B", level2="Sub3"),
        }
        service_owners = {
            "Svc A": ["Owner1"],
            "Svc B": ["Owner2"],
            "Svc C": ["Owner3"],
        }

        # Drill down on "Direct A" at level1
        services = collect_services_for_owner("Direct A", "level1", service_owners, org_mapping)

        assert "Svc A" in services
        assert "Svc B" in services
        assert "Svc C" not in services  # Under Direct B

    def test_level2_drilldown_collects_sub_report_only(self):
        """TC-4.2: Level-2 drill-down includes only that sub-report's items."""
        from sfi_reporter.tk_app import collect_services_for_owner, OrgAncestry

        org_mapping = {
            "Owner1": OrgAncestry(level1="Direct A", level2="Sub1"),
            "Owner2": OrgAncestry(level1="Direct A", level2="Sub2"),
        }
        service_owners = {
            "Svc A": ["Owner1"],
            "Svc B": ["Owner2"],
        }

        # Drill down on "Sub1" at level2
        services = collect_services_for_owner("Sub1", "level2", service_owners, org_mapping)

        assert "Svc A" in services
        assert "Svc B" not in services

    def test_level1_direct_owns_services_directly(self):
        """Level-1 owner who directly owns services includes them."""
        from sfi_reporter.tk_app import collect_services_for_owner, OrgAncestry

        org_mapping = {
            "DirectOwner": OrgAncestry(level1="DirectOwner", level2=None),
            "SubPerson": OrgAncestry(level1="DirectOwner", level2="SubPerson"),
        }
        service_owners = {
            "Svc Direct": ["DirectOwner"],
            "Svc Sub": ["SubPerson"],
        }

        services = collect_services_for_owner("DirectOwner", "level1", service_owners, org_mapping)

        assert "Svc Direct" in services
        assert "Svc Sub" in services


# ---------------------------------------------------------------------------
# 6. Backward Compatibility Regression
# ---------------------------------------------------------------------------

class TestBackwardCompatibility:
    """Ensure 1-level managers and ICs are not affected."""

    def test_aggregate_with_old_string_mapping(self):
        """Old-style string org_mapping must produce same results."""
        from sfi_reporter.tk_app import aggregate_by_owner

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "OutOfSla", "EtaDate": "2025-01-01"},
            {"S360_ServiceTreeServiceName": "Svc B", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {
            "Svc A": ["Ken Hsieh"],
            "Svc B": ["Brent Jensen"],
        }
        org_mapping = {
            "Ken Hsieh": "Ze Li",
            "Brent Jensen": "Brent Jensen",
        }

        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)

        # Ken rolls up to Ze Li
        assert "Ze Li" in result
        assert result["Ze Li"]["count"] == 1
        assert result["Ze Li"]["sla"] == 1

        # Brent stays with Brent
        assert "Brent Jensen" in result
        assert result["Brent Jensen"]["count"] == 1

    def test_aggregate_no_org_mapping(self):
        """Without org_mapping, behaves as direct owner attribution."""
        from sfi_reporter.tk_app import aggregate_by_owner

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {"Svc A": ["Owner A", "Owner B"]}

        result = aggregate_by_owner(items, service_owners)

        assert "Owner A" in result
        assert "Owner B" in result

    def test_aggregate_allowed_owners_legacy(self):
        """Legacy allowed_owners mode still works."""
        from sfi_reporter.tk_app import aggregate_by_owner

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {"Svc A": ["Direct", "Skip"]}

        result = aggregate_by_owner(items, service_owners, allowed_owners={"Direct"})

        assert "Direct" in result
        assert "Skip" not in result
