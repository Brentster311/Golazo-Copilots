"""Tests for SFI-031/032: get_org_mapping behaviour.

After SFI-032 the org-tree caching was moved into accia-s360 SDK
(GraphEndpoint._build_subtree). These tests cover the remaining
responsibilities of get_org_mapping:
- Lowercase alias normalisation
- API failure → all Unknown Owner
- Correct mapping result from tree
"""
import pytest
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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetOrgMapping:
    """Tests for get_org_mapping after cache was moved to SDK."""

    @patch("s360_reporter.data.get_client")
    def test_api_failure_returns_unknown(self, mock_get_client):
        """API exception → all owners mapped to Unknown Owner."""
        from s360_reporter.services import get_org_mapping
        from s360_reporter.models import OrgAncestry

        mock_client = MagicMock()
        mock_client.get_org_tree.side_effect = Exception("Graph API down")
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["Alice", "Bob"], "RootAlias")

        for name in ["Alice", "Bob"]:
            assert result[name] == OrgAncestry(path=("Unknown Owner",))

    @patch("s360_reporter.data.get_client")
    def test_alias_lowercased(self, mock_get_client):
        """Cache key (alias) is lowercased regardless of input case."""
        from s360_reporter.services import get_org_mapping

        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _simple_tree()
        mock_get_client.return_value = mock_client

        get_org_mapping(["IC One"], "BrentJ")

        mock_client.get_org_tree.assert_called_once_with("brentj")

    @patch("s360_reporter.data.get_client")
    def test_empty_owners_returns_empty(self, mock_get_client):
        """No owner names → empty dict, no API call."""
        from s360_reporter.services import get_org_mapping

        result = get_org_mapping([], "RootAlias")
        assert result == {}
        mock_get_client.assert_not_called()

    @patch("s360_reporter.data.get_client")
    def test_mapping_result_correct(self, mock_get_client):
        """Owners found in tree get correct ancestry path."""
        from s360_reporter.services import get_org_mapping
        from s360_reporter.models import OrgAncestry

        mock_client = MagicMock()
        mock_client.get_org_tree.return_value = _simple_tree()
        mock_get_client.return_value = mock_client

        result = get_org_mapping(["IC One", "Manager One", "Missing Person"], "root")

        # IC One is under Manager One who is under Root Manager
        assert result["IC One"].path[-1] == "Manager One"
        assert result["IC One"].path[0] == "Root Manager"
        # Missing Person → Unknown Owner
        assert result["Missing Person"] == OrgAncestry(path=("Unknown Owner",))
