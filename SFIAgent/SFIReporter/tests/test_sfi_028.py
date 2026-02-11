"""Tests for SFI-028: Replace S360 chain-walking with MS Graph in get_org_mapping.

TDD red phase — tests written before implementation.
Tests verify that get_org_mapping now uses client.get_manager_chain() instead of
client.search() for hierarchy resolution.
"""
import pytest
from unittest.mock import MagicMock, patch
from accia_s360.models import OrgPerson


def _make_person(alias: str, display_name: str) -> OrgPerson:
    """Build an OrgPerson with minimal fields."""
    return OrgPerson(alias=alias, display_name=display_name)


def _build_chain_side_effect(chain_registry: dict[str, list[OrgPerson]]) -> callable:
    """Build a side_effect for client.get_manager_chain().

    chain_registry: {alias_lower: [OrgPerson, ...]} — immediate_mgr first, CEO last.
    Missing aliases raise S360ApiError.
    """
    from accia_s360.exceptions import S360ApiError

    def get_manager_chain(alias: str):
        key = alias.lower()
        if key in chain_registry:
            return chain_registry[key]
        raise S360ApiError(f"User '{alias}' not found", endpoint="graph", status_code=404)

    return get_manager_chain


class TestGetOrgMappingGraphAPI:
    """Tests for get_org_mapping using Graph-based get_manager_chain."""

    def _chain_registry(self):
        """Build a test org: alexhowells → muralic → brentj → deepPerson.

        get_manager_chain returns [immediate_mgr, ..., CEO], so:
        - alexhowells chain: [vp, ceo]
        - muralic chain: [alexhowells, vp, ceo]
        - brentj chain: [muralic, alexhowells, vp, ceo]
        - deepperson chain: [brentj, muralic, alexhowells, vp, ceo]
        - external chain: [otherdir, othervp, ceo] — not under alexhowells
        """
        return {
            "alexhowells": [
                _make_person("vp", "VP Person"),
                _make_person("ceo", "CEO Person"),
            ],
            "muralic": [
                _make_person("alexhowells", "Alex Howells"),
                _make_person("vp", "VP Person"),
                _make_person("ceo", "CEO Person"),
            ],
            "brentj": [
                _make_person("muralic", "Muralic Name"),
                _make_person("alexhowells", "Alex Howells"),
                _make_person("vp", "VP Person"),
                _make_person("ceo", "CEO Person"),
            ],
            "deepperson": [
                _make_person("brentj", "Brent Jensen"),
                _make_person("muralic", "Muralic Name"),
                _make_person("alexhowells", "Alex Howells"),
                _make_person("vp", "VP Person"),
                _make_person("ceo", "CEO Person"),
            ],
            "external": [
                _make_person("otherdir", "Other Director"),
                _make_person("othervp", "Other VP"),
                _make_person("ceo", "CEO Person"),
            ],
        }

    def _owner_aliases(self):
        """Map display_name → alias for get_org_mapping."""
        return {
            "Alex Howells": "alexhowells",
            "Muralic Name": "muralic",
            "Brent Jensen": "brentj",
            "Deep Person": "deepperson",
            "External Person": "external",
        }

    @patch("sfi_reporter.data.get_client")
    def test_t1_calls_get_manager_chain_not_search(self, mock_get_client):
        """T1: get_org_mapping calls get_manager_chain, not search for hierarchy."""
        from sfi_reporter.tk_app import get_org_mapping

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(self._chain_registry())
        mock_get_client.return_value = mock_client

        get_org_mapping(
            ["Brent Jensen"], "alexhowells",
            owner_aliases=self._owner_aliases(),
        )

        mock_client.get_manager_chain.assert_called()
        # search should NOT be called for hierarchy resolution
        mock_client.search.assert_not_called()

    @patch("sfi_reporter.data.get_client")
    def test_t2_direct_report(self, mock_get_client):
        """T2: Owner whose chain contains manager_alias at position 0 → direct report."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(self._chain_registry())
        mock_get_client.return_value = mock_client

        result = get_org_mapping(
            ["Muralic Name"], "alexhowells",
            owner_aliases=self._owner_aliases(),
        )

        ancestry = result["Muralic Name"]
        assert ancestry == OrgAncestry(level1="Muralic Name", level2=None)

    @patch("sfi_reporter.data.get_client")
    def test_t3_two_hops_deep(self, mock_get_client):
        """T3: Owner 2 hops deep → level1=direct, level2=owner."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(self._chain_registry())
        mock_get_client.return_value = mock_client

        result = get_org_mapping(
            ["Brent Jensen"], "alexhowells",
            owner_aliases=self._owner_aliases(),
        )

        ancestry = result["Brent Jensen"]
        # brentj chain = [muralic, alexhowells, vp, ceo]
        # alexhowells at index 1 → hops=1
        # level1 = chain[0].display_name = "Muralic Name" (immediate mgr = viewer's direct)
        # level2 = None (hops==1 → IC, not a sub-manager)
        assert ancestry == OrgAncestry(level1="Muralic Name", level2=None)

    @patch("sfi_reporter.data.get_client")
    def test_t4_three_plus_hops_capped(self, mock_get_client):
        """T4: Owner 3+ hops → capped at 2 levels."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(self._chain_registry())
        mock_get_client.return_value = mock_client

        result = get_org_mapping(
            ["Deep Person"], "alexhowells",
            owner_aliases=self._owner_aliases(),
        )

        ancestry = result["Deep Person"]
        # deepperson chain = [brentj, muralic, alexhowells, vp, ceo]
        # alexhowells at index 2 → hops=2
        # level1 = chain[2-1].display_name = chain[1] = "Muralic Name" (viewer's direct)
        # level2 = chain[2-2].display_name = chain[0] = "Brent Jensen" (one below direct)
        assert ancestry == OrgAncestry(level1="Muralic Name", level2="Brent Jensen")

    @patch("sfi_reporter.data.get_client")
    def test_t5_not_in_managers_org(self, mock_get_client):
        """T5: Owner not in manager's org → Unknown Owner."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(self._chain_registry())
        mock_get_client.return_value = mock_client

        result = get_org_mapping(
            ["External Person"], "alexhowells",
            owner_aliases=self._owner_aliases(),
        )

        ancestry = result["External Person"]
        assert ancestry == OrgAncestry(level1="Unknown Owner", level2=None)

    @patch("sfi_reporter.data.get_client")
    def test_t6_graph_api_error_graceful_fallback(self, mock_get_client):
        """T6: Graph API error for one owner → graceful fallback, others unaffected."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        registry = self._chain_registry()
        # Remove brentj so it will raise S360ApiError
        del registry["brentj"]

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(registry)
        mock_get_client.return_value = mock_client

        result = get_org_mapping(
            ["Muralic Name", "Brent Jensen"], "alexhowells",
            owner_aliases=self._owner_aliases(),
        )

        # brentj fails → Unknown Owner
        assert result["Brent Jensen"] == OrgAncestry(level1="Unknown Owner", level2=None)
        # muralic still works
        assert result["Muralic Name"] == OrgAncestry(level1="Muralic Name", level2=None)

    @patch("sfi_reporter.data.get_client")
    def test_t7_owner_is_manager_self_mapping(self, mock_get_client):
        """T7: Owner IS the manager → self-mapping."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(self._chain_registry())
        mock_get_client.return_value = mock_client

        result = get_org_mapping(
            ["Alex Howells"], "alexhowells",
            owner_aliases=self._owner_aliases(),
        )

        ancestry = result["Alex Howells"]
        assert ancestry == OrgAncestry(level1="Alex Howells", level2=None)

    @patch("sfi_reporter.data.get_client")
    def test_missing_alias_falls_back_gracefully(self, mock_get_client):
        """Owner with no alias in owner_aliases → Unknown Owner."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(self._chain_registry())
        mock_get_client.return_value = mock_client

        # "Mystery Person" is not in owner_aliases
        result = get_org_mapping(
            ["Mystery Person"], "alexhowells",
            owner_aliases={"Alex Howells": "alexhowells"},
        )

        assert result["Mystery Person"] == OrgAncestry(level1="Unknown Owner", level2=None)

    @patch("sfi_reporter.data.get_client")
    def test_backward_compat_no_owner_aliases(self, mock_get_client):
        """When owner_aliases is not provided, falls back gracefully."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(self._chain_registry())
        mock_get_client.return_value = mock_client

        # No owner_aliases → all owners map to Unknown Owner (can't resolve alias)
        result = get_org_mapping(["Muralic Name"], "alexhowells")

        assert result["Muralic Name"] == OrgAncestry(level1="Unknown Owner", level2=None)

    @patch("sfi_reporter.data.get_client")
    def test_parallel_multiple_owners(self, mock_get_client):
        """Multiple owners processed in parallel without errors."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(self._chain_registry())
        mock_get_client.return_value = mock_client

        owners = ["Muralic Name", "Brent Jensen", "Deep Person", "External Person", "Alex Howells"]
        result = get_org_mapping(owners, "alexhowells", owner_aliases=self._owner_aliases())

        assert len(result) == 5
        for name in owners:
            assert name in result
            assert isinstance(result[name], OrgAncestry)


class TestGetServiceOwnersWithAliases:
    """Test that get_service_owners returns alias mapping alongside owner names."""

    @patch("sfi_reporter.data.get_client")
    def test_returns_aliases_in_second_dict(self, mock_get_client):
        """get_service_owners returns (owners_dict, alias_dict) tuple."""
        from sfi_reporter.tk_app import get_service_owners

        mock_client = MagicMock()
        mock_client.search.return_value = [
            {
                "Group": "Service",
                "Name": "My Service",
                "Owners": '["Brent Jensen"]',
            }
        ]
        mock_get_client.return_value = mock_client

        result = get_service_owners(["My Service"])

        # Result should now be a tuple of (service_owners, owner_aliases)
        assert isinstance(result, tuple), "get_service_owners must return a tuple"
        service_owners, owner_aliases = result
        assert "My Service" in service_owners
        assert service_owners["My Service"] == ["Brent Jensen"]

    @patch("sfi_reporter.data.get_client")
    def test_alias_from_org_search_result(self, mock_get_client):
        """Owner aliases are resolved from Org search results (Id field)."""
        from sfi_reporter.tk_app import get_service_owners

        def search_side_effect(query):
            if query == "My Service":
                return [
                    {
                        "Group": "Service",
                        "Name": "My Service",
                        "Owners": '["Brent Jensen"]',
                    }
                ]
            if query == "Brent Jensen":
                return [
                    {
                        "Group": "Org",
                        "Id": "brentj",
                        "Owners": "Brent Jensen",
                        "Name": "Brent Jensen",
                    }
                ]
            return []

        mock_client = MagicMock()
        mock_client.search.side_effect = search_side_effect
        mock_get_client.return_value = mock_client

        service_owners, owner_aliases = get_service_owners(["My Service"])

        assert owner_aliases.get("Brent Jensen") == "brentj"


class TestDuplicateDisplayNames:
    """Tests for handling multiple people with the same display name."""

    def _chain_registry(self):
        """Org where two "Rohit Pandey" exist — one in org, one not.

        rohitpandey1 reports to muralic → in org.
        rohitpandey2 reports to otherdir → NOT in org.
        """
        return {
            "muralic": [
                _make_person("alexhowells", "Alex Howells"),
                _make_person("vp", "VP Person"),
            ],
            "rohitpandey1": [
                _make_person("muralic", "Murali Chintalapati"),
                _make_person("alexhowells", "Alex Howells"),
                _make_person("vp", "VP Person"),
            ],
            "rohitpandey2": [
                _make_person("otherdir", "Other Director"),
                _make_person("othervp", "Other VP"),
                _make_person("ceo", "CEO Person"),
            ],
        }

    @patch("sfi_reporter.data.get_client")
    def test_ambiguous_name_picks_correct_alias(self, mock_get_client):
        """When two people share a name, get_org_mapping picks the one in the org."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(
            self._chain_registry()
        )
        mock_get_client.return_value = mock_client

        # owner_aliases has a LIST of candidates for "Rohit Pandey"
        result = get_org_mapping(
            ["Rohit Pandey"], "alexhowells",
            owner_aliases={"Rohit Pandey": ["rohitpandey2", "rohitpandey1"]},
        )

        ancestry = result["Rohit Pandey"]
        # rohitpandey2 is NOT in alexhowells' org, so it should be skipped.
        # rohitpandey1 IS in alexhowells' org (chain: muralic → alexhowells).
        assert ancestry.level1 == "Murali Chintalapati"
        assert ancestry.level2 is None

    @patch("sfi_reporter.data.get_client")
    def test_ambiguous_name_correct_alias_first(self, mock_get_client):
        """When the correct alias is first in the list, it's used directly."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(
            self._chain_registry()
        )
        mock_get_client.return_value = mock_client

        result = get_org_mapping(
            ["Rohit Pandey"], "alexhowells",
            owner_aliases={"Rohit Pandey": ["rohitpandey1", "rohitpandey2"]},
        )

        ancestry = result["Rohit Pandey"]
        assert ancestry.level1 == "Murali Chintalapati"

    @patch("sfi_reporter.data.get_client")
    def test_ambiguous_name_neither_in_org(self, mock_get_client):
        """When no candidate is in the org, maps to Unknown Owner."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(
            self._chain_registry()
        )
        mock_get_client.return_value = mock_client

        # Both aliases are NOT under "someotheralias"
        result = get_org_mapping(
            ["Rohit Pandey"], "someotheralias",
            owner_aliases={"Rohit Pandey": ["rohitpandey1", "rohitpandey2"]},
        )

        ancestry = result["Rohit Pandey"]
        assert ancestry == OrgAncestry(level1="Unknown Owner", level2=None)

    @patch("sfi_reporter.data.get_client")
    def test_single_alias_str_still_works(self, mock_get_client):
        """Single alias stored as str (not list) still works fine."""
        from sfi_reporter.tk_app import get_org_mapping, OrgAncestry

        mock_client = MagicMock()
        mock_client.get_manager_chain.side_effect = _build_chain_side_effect(
            self._chain_registry()
        )
        mock_get_client.return_value = mock_client

        result = get_org_mapping(
            ["Rohit Pandey"], "alexhowells",
            owner_aliases={"Rohit Pandey": "rohitpandey1"},
        )

        ancestry = result["Rohit Pandey"]
        assert ancestry.level1 == "Murali Chintalapati"


class TestGetServiceOwnersAmbiguousAliases:
    """Test that get_service_owners handles duplicate display names."""

    @patch("sfi_reporter.data.get_client")
    def test_multiple_org_matches_returns_list(self, mock_get_client):
        """When S360 returns two Org matches for the same name, owner_aliases stores a list."""
        from sfi_reporter.tk_app import get_service_owners

        def search_side_effect(query):
            if query == "My Service":
                return [
                    {
                        "Group": "Service",
                        "Name": "My Service",
                        "Owners": '["Rohit Pandey"]',
                    }
                ]
            if query == "Rohit Pandey":
                return [
                    {
                        "Group": "Org",
                        "Id": "rohitpandey1",
                        "Owners": "Rohit Pandey",
                        "Name": "Rohit Pandey",
                    },
                    {
                        "Group": "Org",
                        "Id": "rohitpandey2",
                        "Owners": "Rohit Pandey",
                        "Name": "Rohit Pandey",
                    },
                ]
            return []

        mock_client = MagicMock()
        mock_client.search.side_effect = search_side_effect
        mock_get_client.return_value = mock_client

        service_owners, owner_aliases = get_service_owners(["My Service"])

        # Should store as list since there are multiple candidates
        aliases = owner_aliases.get("Rohit Pandey")
        assert isinstance(aliases, list), f"Expected list, got {type(aliases)}"
        assert "rohitpandey1" in aliases
        assert "rohitpandey2" in aliases

    @patch("sfi_reporter.data.get_client")
    def test_single_org_match_returns_string(self, mock_get_client):
        """When S360 returns exactly one match, owner_aliases stores a string."""
        from sfi_reporter.tk_app import get_service_owners

        def search_side_effect(query):
            if query == "My Service":
                return [
                    {
                        "Group": "Service",
                        "Name": "My Service",
                        "Owners": '["Brent Jensen"]',
                    }
                ]
            if query == "Brent Jensen":
                return [
                    {
                        "Group": "Org",
                        "Id": "brentj",
                        "Owners": "Brent Jensen",
                        "Name": "Brent Jensen",
                    },
                ]
            return []

        mock_client = MagicMock()
        mock_client.search.side_effect = search_side_effect
        mock_get_client.return_value = mock_client

        service_owners, owner_aliases = get_service_owners(["My Service"])

        # Single match → string, not list
        assert owner_aliases.get("Brent Jensen") == "brentj"
