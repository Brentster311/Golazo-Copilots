"""Tests for EtaUpdate payload format and save_etas flow.

TC-06 through TC-08 from SFI-019 Test Cases.
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch


class TestEtaUpdatePayload:
    """Tests for EtaUpdate.to_api_payload() — Sauron format (BD-1)."""

    def test_tc06_payload_matches_sauron_format(self):
        """TC-06: Payload must have top-level ETADate, UserStatus, KpiId + ActionItems array."""
        from accia_s360.models import EtaUpdate

        update = EtaUpdate(
            kpi_id="04988624-19fe-4a58-974a-aa47f6f6c1a4",
            service_id="47d282c5-0dc6-4580-9030-bbcbd6ac9078",
            action_item_id="item-001",
            new_eta=datetime(2026, 2, 28),
            notes="Working on remediation",
            assigned_to="brentj",
            sla_type="InSla",
        )

        payload = update.to_api_payload()

        # Top-level fields
        assert payload["ETADate"] == "2026-02-28"
        assert payload["UserStatus"] == "Working on remediation"
        assert payload["KpiId"] == "04988624-19fe-4a58-974a-aa47f6f6c1a4"

        # ActionItems array
        assert "ActionItems" in payload
        assert len(payload["ActionItems"]) == 1
        ai = payload["ActionItems"][0]
        assert ai["ServiceId"] == "47d282c5-0dc6-4580-9030-bbcbd6ac9078"
        assert ai["ActionItemId"] == "item-001"
        assert ai["AssignedTo"] == "brentj"
        assert ai["SLAType"] == "InSla"

        # Old format fields must NOT be present at top level
        assert "Eta" not in payload
        assert "items" not in payload


class TestSaveEtas:
    """Tests for save_etas() API call flow."""

    def test_tc07_successful_save(self):
        """TC-07: 200 response → SaveResult(success=True)."""
        from accia_s360.endpoints.action_items import ActionItemsEndpoint
        from accia_s360.models import EtaUpdate, SaveResult

        endpoint = ActionItemsEndpoint.__new__(ActionItemsEndpoint)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = None

        update = EtaUpdate(
            kpi_id="kpi-1",
            service_id="svc-1",
            action_item_id="item-1",
            new_eta=datetime(2026, 3, 31),
            notes="Fixed",
            assigned_to="brentj",
        )

        with patch.object(endpoint, "_make_request", return_value=mock_response):
            result = endpoint.save_etas([update])

        assert result.success is True

    def test_tc08_api_error(self):
        """TC-08: 400 response → SaveResult(success=False) with error detail."""
        from accia_s360.endpoints.action_items import ActionItemsEndpoint
        from accia_s360.models import EtaUpdate

        endpoint = ActionItemsEndpoint.__new__(ActionItemsEndpoint)

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid KPI ID"}
        mock_response.text = "Invalid KPI ID"

        update = EtaUpdate(
            kpi_id="bad-kpi",
            service_id="svc-1",
            action_item_id="item-1",
            new_eta=datetime(2026, 3, 31),
            notes="",
            assigned_to="brentj",
        )

        with patch.object(endpoint, "_make_request", return_value=mock_response):
            result = endpoint.save_etas([update])

        assert result.success is False
        assert "400" in result.error_message
