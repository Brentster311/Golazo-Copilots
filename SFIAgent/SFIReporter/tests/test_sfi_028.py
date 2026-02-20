"""Tests for SFI-028: get_service_owners return-type validation.

NOTE: Most original SFI-028 tests (get_org_mapping via get_manager_chain, duplicate
display-name disambiguation, S360 alias resolution) are superseded by SFI-029 which
tests the new get_org_tree-based implementation.  Only the get_service_owners
return-type test remains here.
"""
from unittest.mock import MagicMock, patch


class TestGetServiceOwnersSimplified:
    """Test that get_service_owners returns a plain dict of service → owners."""

    @patch("sfi_reporter.data.get_client")
    def test_returns_dict(self, mock_get_client):
        """get_service_owners returns a dict (no longer a tuple)."""
        from sfi_reporter.services import get_service_owners

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

        assert isinstance(result, dict), "get_service_owners must return a dict"
        assert "My Service" in result
        assert result["My Service"] == ["Brent Jensen"]
