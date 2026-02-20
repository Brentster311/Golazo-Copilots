"""Tests for SFI-026: Multi-Level Owner Grouping in Services Table.

Tests cover:
- OrgAncestry NamedTuple (path-based)
- aggregate_by_owner() with OrgAncestry tuples
- collect_services_for_owner() path-prefix drill-down
- Backward compatibility with legacy string mappings
- Cache serialization round-trip
"""
import json


# ---------------------------------------------------------------------------
# 1. OrgAncestry NamedTuple
# ---------------------------------------------------------------------------

class TestOrgAncestry:
    """Verify the OrgAncestry type exists and behaves correctly."""

    def test_creation_with_two_levels(self):
        from sfi_reporter.models import OrgAncestry
        a = OrgAncestry(path=("L1", "L2"))
        assert a.path == ("L1", "L2")

    def test_creation_single_element(self):
        from sfi_reporter.models import OrgAncestry
        a = OrgAncestry(path=("Muralic Name",))
        assert a.path == ("Muralic Name",)

    def test_path_access(self):
        from sfi_reporter.models import OrgAncestry
        a = OrgAncestry(path=("L1", "L2"))
        assert a.path[0] == "L1"
        assert a.path[1] == "L2"

    def test_unknown_owner(self):
        from sfi_reporter.models import OrgAncestry
        a = OrgAncestry(path=("Unknown Owner",))
        assert a.path == ("Unknown Owner",)


# ---------------------------------------------------------------------------
# 2. aggregate_by_owner() — With OrgAncestry
# ---------------------------------------------------------------------------

class TestAggregateByOwnerWithOrgAncestry:
    """Tests for aggregate_by_owner consuming OrgAncestry tuples."""

    def test_tc_2_1_level1_stats_are_sum_of_children(self):
        """TC-2.1: Level-1 stats equal sum of all children."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import aggregate_by_owner

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
            "Owner1": OrgAncestry(path=("Root", "Direct A")),
            "Owner2": OrgAncestry(path=("Root", "Direct A")),
            "Owner3": OrgAncestry(path=("Root", "Direct B")),
        }

        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)

        # Level1 rollup: Direct A has 2 items, Direct B has 1
        assert "Direct A" in result
        assert result["Direct A"]["count"] == 2
        assert "Direct B" in result
        assert result["Direct B"]["count"] == 1

    def test_tc_2_2_sla_and_eta_rollup(self):
        """TC-2.2: SLA and invalid ETA roll up correctly."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import aggregate_by_owner

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "OutOfSla", "EtaDate": None},
            {"S360_ServiceTreeServiceName": "Svc B", "SlaType": "InSLA", "EtaDate": "2025-01-01"},
        ]
        service_owners = {
            "Svc A": ["Owner1"],
            "Svc B": ["Owner2"],
        }
        org_mapping = {
            "Owner1": OrgAncestry(path=("Root", "Direct A")),
            "Owner2": OrgAncestry(path=("Root", "Direct A")),
        }

        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)

        assert result["Direct A"]["sla"] == 1  # Only 1 OutOfSla
        assert result["Direct A"]["count"] == 2

    def test_tc_2_3_unknown_owner_bucket(self):
        """TC-2.3: Unmapped owners fall into Unknown Owner."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import aggregate_by_owner

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {
            "Svc A": ["Unmapped Person"],
        }
        org_mapping = {
            "Unmapped Person": OrgAncestry(path=("Unknown Owner",)),
        }

        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)

        assert "Unknown Owner" in result
        assert result["Unknown Owner"]["count"] == 1

    def test_tc_2_4_path_with_two_elements_uses_path1(self):
        """TC-2.4: When path has 2 elements, uses path[1] as group key."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import aggregate_by_owner

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
            {"S360_ServiceTreeServiceName": "Svc B", "SlaType": "OutOfSla", "EtaDate": "2030-01-01"},
        ]
        service_owners = {
            "Svc A": ["Owner1"],
            "Svc B": ["Owner2"],
        }
        org_mapping = {
            "Owner1": OrgAncestry(path=("Root", "Direct A")),
            "Owner2": OrgAncestry(path=("Root", "Direct B")),
        }

        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)

        assert "Direct A" in result
        assert result["Direct A"]["count"] == 1
        assert "Direct B" in result
        assert result["Direct B"]["count"] == 1

    def test_existing_string_org_mapping_still_works(self):
        """Regression: Old-style string org_mapping must still work."""
        from sfi_reporter.services import aggregate_by_owner

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {"Svc A": ["Owner1"]}
        org_mapping = {"Owner1": "Direct A"}  # Old string format

        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)

        assert "Direct A" in result
        assert result["Direct A"]["count"] == 1


# ---------------------------------------------------------------------------
# 3. Drill-Down Logic — Collect Services by Org Subtree
# ---------------------------------------------------------------------------

class TestDrillDownSubtree:
    """Tests for collecting services by org subtree for drill-down."""

    def test_level1_drilldown_collects_entire_subtree(self):
        """TC-4.1: Level-1 drill-down includes ALL items in subtree."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import collect_services_for_owner

        org_mapping = {
            "Owner1": OrgAncestry(path=("Root", "Direct A", "Sub1")),
            "Owner2": OrgAncestry(path=("Root", "Direct A", "Sub2")),
            "Owner3": OrgAncestry(path=("Root", "Direct B", "Sub3")),
        }
        service_owners = {
            "Svc A": ["Owner1"],
            "Svc B": ["Owner2"],
            "Svc C": ["Owner3"],
        }

        # Drill down on "Direct A" via path prefix
        services = collect_services_for_owner(("Root", "Direct A"), service_owners, org_mapping)

        assert "Svc A" in services
        assert "Svc B" in services
        assert "Svc C" not in services  # Under Direct B

    def test_deeper_prefix_drilldown_collects_sub_report_only(self):
        """TC-4.2: Deeper prefix drill-down includes only that sub-report's items."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import collect_services_for_owner

        org_mapping = {
            "Owner1": OrgAncestry(path=("Root", "Direct A", "Sub1")),
            "Owner2": OrgAncestry(path=("Root", "Direct A", "Sub2")),
        }
        service_owners = {
            "Svc A": ["Owner1"],
            "Svc B": ["Owner2"],
        }

        # Drill down on "Sub1" via path prefix
        services = collect_services_for_owner(("Root", "Direct A", "Sub1"), service_owners, org_mapping)

        assert "Svc A" in services
        assert "Svc B" not in services

    def test_level1_direct_owns_services_directly(self):
        """Level-1 owner who directly owns services includes them."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import collect_services_for_owner

        org_mapping = {
            "DirectOwner": OrgAncestry(path=("Root", "DirectOwner")),
            "SubPerson": OrgAncestry(path=("Root", "DirectOwner", "SubPerson")),
        }
        service_owners = {
            "Svc Direct": ["DirectOwner"],
            "Svc Sub": ["SubPerson"],
        }

        services = collect_services_for_owner(("Root", "DirectOwner"), service_owners, org_mapping)

        assert "Svc Direct" in services
        assert "Svc Sub" in services


# ---------------------------------------------------------------------------
# 4. Backward Compatibility Regression
# ---------------------------------------------------------------------------

class TestBackwardCompatibility:
    """Ensure 1-level managers and ICs are not affected."""

    def test_aggregate_with_old_string_mapping(self):
        """Old-style string org_mapping must produce same results."""
        from sfi_reporter.services import aggregate_by_owner

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
        from sfi_reporter.services import aggregate_by_owner

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {"Svc A": ["Owner A", "Owner B"]}

        result = aggregate_by_owner(items, service_owners)

        assert "Owner A" in result
        assert "Owner B" in result

    def test_aggregate_allowed_owners_legacy(self):
        """Legacy allowed_owners mode still works."""
        from sfi_reporter.services import aggregate_by_owner

        items = [
            {"S360_ServiceTreeServiceName": "Svc A", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {"Svc A": ["Direct", "Skip"]}

        result = aggregate_by_owner(items, service_owners, allowed_owners={"Direct"})

        assert "Direct" in result
        assert "Skip" not in result


# ---------------------------------------------------------------------------
# 5. Cache Serialization Round-Trip
# ---------------------------------------------------------------------------

class TestCacheSerializationRoundTrip:
    """Verify OrgAncestry survives JSON cache round-trip."""

    def test_org_mapping_round_trip(self):
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import _serialize_org_data_for_cache, _deserialize_org_data_from_cache
        data = {
            'org_mapping': {
                'brentj': OrgAncestry(path=('Muralic Name', 'Brent Jensen')),
                'kehsieh': OrgAncestry(path=('Muralic Name',)),
            },
        }
        serialized = _serialize_org_data_for_cache(data)
        # Must be JSON-serializable
        json_str = json.dumps(serialized)
        deserialized = json.loads(json_str)
        _deserialize_org_data_from_cache(deserialized)
        assert isinstance(deserialized['org_mapping']['brentj'], OrgAncestry)
        assert deserialized['org_mapping']['brentj'].path == ('Muralic Name', 'Brent Jensen')
        assert deserialized['org_mapping']['kehsieh'].path == ('Muralic Name',)

    def test_empty_data_round_trip(self):
        from sfi_reporter.services import _serialize_org_data_for_cache, _deserialize_org_data_from_cache
        data = {'org_mapping': {}}
        serialized = _serialize_org_data_for_cache(data)
        json_str = json.dumps(serialized)
        deserialized = json.loads(json_str)
        _deserialize_org_data_from_cache(deserialized)
        assert deserialized['org_mapping'] == {}

    def test_legacy_string_org_mapping_preserved(self):
        """Legacy string org_mapping (from older caches) is not corrupted."""
        from sfi_reporter.services import _deserialize_org_data_from_cache
        data = {
            'org_mapping': {'brentj': 'Muralic Name'},
        }
        _deserialize_org_data_from_cache(data)
        assert data['org_mapping']['brentj'] == 'Muralic Name'
