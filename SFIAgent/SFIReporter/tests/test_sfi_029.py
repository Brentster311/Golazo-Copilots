"""Tests for SFI-029: Top-down org tree grouping with N-level manager hierarchy.

TDD red phase — tests written before production changes.
Tests verify:
- get_org_mapping uses get_org_tree() instead of get_manager_chain()
- OrgAncestry.path supports N-level nesting
- get_service_owners returns simple dict (no tuple)
- ICs never appear as group headers
- Owner disambiguation via tree
- Expand/collapse defaults
"""
import pytest
from unittest.mock import MagicMock, patch
from accia_s360.models import OrgPerson, OrgTree


def _person(alias: str, display_name: str, **kw) -> OrgPerson:
    """Build an OrgPerson with minimal fields."""
    return OrgPerson(alias=alias, display_name=display_name, **kw)


def _tree(alias: str, display_name: str, children: list | None = None) -> OrgTree:
    """Build an OrgTree node with optional children."""
    return OrgTree(
        person=_person(alias, display_name),
        direct_reports=children or [],
    )


# ---------------------------------------------------------------------------
# Fixture: realistic 3-level org tree for muralic
# muralic -> karanpar (mgr) -> bhgopal (IC), jepeach (IC)
# muralic -> brentj (mgr) -> weizou (IC), trtran (IC)
# muralic -> ropandey (mgr) -> chavigupta (IC)
# muralic -> armukher (IC — no reports, manager only by chain depth)
# ---------------------------------------------------------------------------
def _muralic_tree() -> OrgTree:
    return _tree("muralic", "Murali Chintalapati", [
        _tree("karanpar", "Karan Parkash", [
            _tree("bhgopal", "Bhavya Gopal"),
            _tree("jepeach", "Jeremy Peach"),
        ]),
        _tree("brentj", "Brent Jensen", [
            _tree("weizou", "Wei Zou"),
            _tree("trtran", "Tri Tran"),
        ]),
        _tree("ropandey", "Rohit Pandey", [
            _tree("chavigupta", "Chavi Gupta"),
        ]),
        _tree("armukher", "Arjun Mukherjee"),  # IC direct report, no sub-reports
    ])


class TestGetOrgMappingOrgTree:
    """Tests for get_org_mapping using get_org_tree()."""

    @patch("sfi_reporter.data.get_client")
    def test_tc01_calls_get_org_tree_once(self, mock_get_client):
        """TC-01: get_org_mapping calls get_org_tree once, not get_manager_chain."""
        from sfi_reporter.services import get_org_mapping

        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _muralic_tree()
        mock_get_client.return_value = mock_client

        get_org_mapping(["Brent Jensen"], "muralic")

        mock_client.get_org_tree.assert_called_once_with("muralic")
        mock_client.get_manager_chain.assert_not_called()
        mock_client.search.assert_not_called()

    @patch("sfi_reporter.data.get_client")
    def test_tc04_ics_never_in_path(self, mock_get_client):
        """TC-04: ICs (no direct reports) never appear in ancestry path.
        
        Bhavya Gopal is an IC under Karan Parkash (manager under muralic).
        Path should be ("Murali Chintalapati", "Karan Parkash") — root + nearest manager.
        Bhavya's name never appears in the path.
        """
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import get_org_mapping

        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _muralic_tree()
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Bhavya Gopal"], "muralic")
        ancestry = result["Bhavya Gopal"]

        assert isinstance(ancestry, OrgAncestry)
        assert ancestry.path == ("Murali Chintalapati", "Karan Parkash")
        assert "Bhavya Gopal" not in ancestry.path

    @patch("sfi_reporter.data.get_client")
    def test_tc05_n_level_nesting(self, mock_get_client):
        """TC-05: Ancestry path follows manager chain, not capped at 2.
        
        4-level tree: alex(root) -> muralic(mgr) -> brentj(mgr) -> Wei Zou(IC)
        Root IS a group (path[0]). Managers in chain = alex, muralic, brentj.
        Wei Zou's name never appears. Path = ("Alex Howells", "Murali Chintalapati", "Brent Jensen").
        """
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import get_org_mapping

        deep_tree = _tree("alexhowells", "Alex Howells", [
            _tree("muralic", "Murali Chintalapati", [
                _tree("brentj", "Brent Jensen", [
                    _tree("weizou", "Wei Zou"),
                ]),
            ]),
        ])

        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = deep_tree
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Wei Zou"], "alexhowells")
        ancestry = result["Wei Zou"]

        # 3 managers in chain: alex (root), muralic, brentj
        assert isinstance(ancestry, OrgAncestry)
        assert ancestry.path == ("Alex Howells", "Murali Chintalapati", "Brent Jensen")
        assert "Wei Zou" not in ancestry.path

    @patch("sfi_reporter.data.get_client")
    def test_tc07_name_disambiguation(self, mock_get_client):
        """TC-07: Only the person in the tree matches, not external duplicates."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import get_org_mapping

        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _muralic_tree()
        mock_get_client.return_value = mock_client

        # "Rohit Pandey" exists in muralic's tree under ropandey
        result = get_org_mapping(["Rohit Pandey"], "muralic")
        ancestry = result["Rohit Pandey"]

        # Rohit Pandey IS a manager under muralic → path includes root + Rohit
        assert isinstance(ancestry, OrgAncestry)
        assert ancestry.path == ("Murali Chintalapati", "Rohit Pandey")

    @patch("sfi_reporter.data.get_client")
    def test_tc08_owner_is_manager(self, mock_get_client):
        """TC-08: When owner IS the root manager, path = (root_name,)."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import get_org_mapping

        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _muralic_tree()
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Murali Chintalapati"], "muralic")
        ancestry = result["Murali Chintalapati"]

        # Owner IS the root manager → path = (root_name,)
        assert isinstance(ancestry, OrgAncestry)
        assert ancestry.path == ("Murali Chintalapati",)

    @patch("sfi_reporter.data.get_client")
    def test_tc09_owner_not_found(self, mock_get_client):
        """TC-09: Owner not in tree maps to Unknown Owner."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import get_org_mapping

        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _muralic_tree()
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Nonexistent Person"], "muralic")
        ancestry = result["Nonexistent Person"]

        assert isinstance(ancestry, OrgAncestry)
        assert ancestry.path == ("Unknown Owner",)

    @patch("sfi_reporter.data.get_client")
    def test_tc11_empty_tree(self, mock_get_client):
        """TC-11: Manager with no reports → all owners unknown."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import get_org_mapping

        empty_tree = _tree("solo", "Solo Manager")
        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = empty_tree
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Some Owner"], "solo")
        assert result["Some Owner"].path == ("Unknown Owner",)

    @patch("sfi_reporter.data.get_client")
    def test_tc08b_direct_report_ic_under_root(self, mock_get_client):
        """TC-08b: Arjun Mukherjee is a direct IC (no sub-reports).
        
        He has no direct_reports → not a manager → no group header.
        Path = ("Murali Chintalapati",) — service under root's group.
        """
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import get_org_mapping

        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _muralic_tree()
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Arjun Mukherjee"], "muralic")
        ancestry = result["Arjun Mukherjee"]

        # Arjun is IC direct of root — path = (root,)
        assert isinstance(ancestry, OrgAncestry)
        assert ancestry.path == ("Murali Chintalapati",)

    @patch("sfi_reporter.data.get_client")
    def test_case_insensitive_name_match(self, mock_get_client):
        """Owner name matching is case-insensitive."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import get_org_mapping

        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _muralic_tree()
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["brent jensen"], "muralic")
        ancestry = result["brent jensen"]

        assert isinstance(ancestry, OrgAncestry)
        assert ancestry.path == ("Murali Chintalapati", "Brent Jensen")

    @patch("sfi_reporter.data.get_client")
    def test_no_owner_aliases_param(self, mock_get_client):
        """TC-03: get_org_mapping no longer accepts owner_aliases parameter."""
        from sfi_reporter.services import get_org_mapping
        import inspect

        sig = inspect.signature(get_org_mapping)
        assert "owner_aliases" not in sig.parameters


class TestGetServiceOwnersSimplified:
    """TC-02: get_service_owners returns simple dict, not tuple."""

    @patch("sfi_reporter.data.get_client")
    def test_returns_dict_not_tuple(self, mock_get_client):
        """get_service_owners returns dict[str, list[str]], not tuple."""
        from sfi_reporter.services import get_service_owners

        mock_client = MagicMock()
        mock_client.search.return_value = [{
            'Group': 'Service',
            'Name': 'TestService',
            'Owners': '["Owner A"]',
        }]
        mock_get_client.return_value = mock_client

        result = get_service_owners(["TestService"])
        assert isinstance(result, dict)
        assert not isinstance(result, tuple)
        assert "TestService" in result

    @patch("sfi_reporter.data.get_client")
    def test_no_resolve_alias_calls(self, mock_get_client):
        """No S360 search calls for alias resolution (only for service lookup)."""
        from sfi_reporter.services import get_service_owners

        mock_client = MagicMock()
        mock_client.search.return_value = [{
            'Group': 'Service',
            'Name': 'TestService',
            'Owners': '["Owner A"]',
        }]
        mock_get_client.return_value = mock_client

        get_service_owners(["TestService"])
        # search should only be called once (for service), not again for alias resolution
        assert mock_client.search.call_count == 1


class TestAggregationNLevel:
    """Tests for N-level aggregation functions."""

    def test_aggregate_by_owner_uses_path(self):
        """aggregate_by_owner rolls up to path[0] (top-level manager)."""
        from sfi_reporter.models import OrgAncestry
        from sfi_reporter.services import aggregate_by_owner

        items = [
            {'S360_ServiceTreeServiceName': 'Svc1', 'SlaType': 'InSla', 'EtaDate': '2026-06-01'},
            {'S360_ServiceTreeServiceName': 'Svc2', 'SlaType': 'OutOfSla', 'EtaDate': '2026-06-01'},
        ]
        service_owners = {
            'Svc1': ['Wei Zou'],
            'Svc2': ['Chavi Gupta'],
        }
        org_mapping = {
            'Wei Zou': OrgAncestry(path=('Murali Chintalapati', 'Brent Jensen')),
            'Chavi Gupta': OrgAncestry(path=('Murali Chintalapati', 'Rohit Pandey')),
        }

        stats = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)
        # Aggregation at direct-report level (path[1])
        assert 'Brent Jensen' in stats
        assert 'Rohit Pandey' in stats
        assert stats['Brent Jensen']['count'] == 1
        assert stats['Rohit Pandey']['count'] == 1
