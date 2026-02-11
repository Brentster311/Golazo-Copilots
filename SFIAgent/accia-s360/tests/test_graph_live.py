"""
Live integration tests for GraphEndpoint — MS Graph people hierarchy.

Tests T35–T40 from SFI-027-Test-Cases.md.
Requires real Azure CLI credentials. Run with:
    pytest tests/test_graph_live.py -m live -v
"""

import pytest

from accia_s360 import S360Client
from accia_s360.exceptions import S360ApiError


pytestmark = pytest.mark.live


@pytest.fixture(scope="module")
def client():
    """Create a real S360Client for live tests."""
    return S360Client()


class TestLiveGraphEndpoint:
    """Live integration tests — require Azure CLI auth."""

    def test_get_manager_chain_muralic(self, client):
        """T35: muralic's manager chain contains alexhowells."""
        chain = client.get_manager_chain("muralic")
        aliases = [p.alias for p in chain]
        assert "alexhowells" in aliases, (
            f"Expected alexhowells in manager chain, got: {aliases}"
        )

    def test_get_direct_reports_muralic(self, client):
        """T36: muralic's direct reports include brentj."""
        reports = client.get_direct_reports("muralic")
        aliases = [p.alias for p in reports]
        assert "brentj" in aliases, (
            f"Expected brentj in direct reports, got: {aliases}"
        )

    def test_get_direct_reports_excludes_sc_alts(self, client):
        """T37: No SC ALT aliases in filtered results."""
        reports = client.get_direct_reports("muralic")
        for p in reports:
            assert not p.alias.lower().startswith("sc-"), (
                f"SC ALT not filtered: {p.alias}"
            )
            assert "NON EA SC ALT" not in (p.display_name or "").upper(), (
                f"SC ALT not filtered: {p.display_name}"
            )

    def test_get_org_tree_muralic(self, client):
        """T38: Org tree root is muralic with direct reports."""
        tree = client.get_org_tree("muralic", depth=1)
        assert tree.person.alias == "muralic"
        assert len(tree.direct_reports) > 0, "Expected at least one direct report"

    def test_manager_chain_reaches_ceo(self, client):
        """T39: Manager chain ends at satyan (CEO)."""
        chain = client.get_manager_chain("muralic")
        assert len(chain) > 0, "Expected non-empty chain"
        assert chain[-1].alias == "satyan", (
            f"Expected CEO satyan at end of chain, got: {chain[-1].alias}"
        )

    def test_unknown_alias_raises(self, client):
        """T40: Non-existent alias raises S360ApiError."""
        with pytest.raises(S360ApiError):
            client.get_manager_chain("nonexistent_alias_zzz_xyz_999")
