"""SFI-041 tests for Action Owner save flow (red/green TDD)."""

from __future__ import annotations

import sys
import tkinter as tk
from unittest.mock import MagicMock

import pytest

_mock_copilot = MagicMock()
_mock_copilot.Tool = type("Tool", (), {"__init__": lambda self, **kw: self.__dict__.update(kw)})
_mock_copilot.ToolResult = type("ToolResult", (), {"__init__": lambda self, **kw: self.__dict__.update(kw)})
_mock_copilot.define_tool = MagicMock()
_mock_copilot.CopilotClient = MagicMock
sys.modules.setdefault("copilot", _mock_copilot)

from sfi_reporter.data import (  # noqa: E402
    build_action_owner_save_request,
    get_action_owner_save_success_count,
    reset_action_owner_save_success_count,
    save_action_owner,
)
from sfi_reporter.dialogs import ItemDetailsModal  # noqa: E402


@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture(autouse=True)
def _reset_owner_counter():
    reset_action_owner_save_success_count()
    yield
    reset_action_owner_save_success_count()


def _item(**overrides) -> dict:
    base = {
        "id": "AI-001",
        "_kpi_id": "kpi-001",
        "S360_ServiceId": "svc-001",
        "S360_ActionItemId": "ai-001",
        "SlaType": "OutOfSla",
        "ActionOwnerAlias": "oldowner",
        "ActionOwnerName": "Old Owner",
        "title": "Sample Action Item",
    }
    base.update(overrides)
    return base


def test_build_action_owner_save_request_validation_failure_for_missing_owner():
    ok, message, request = build_action_owner_save_request(_item(), "", "")
    assert ok is False
    assert request is None
    assert "Action Owner" in message


def test_build_action_owner_save_request_builds_required_contract_fields():
    ok, _message, request = build_action_owner_save_request(_item(), " NewAlias ", "New Owner")
    assert ok is True
    assert request is not None
    assert request["kpi_id"] == "kpi-001"
    assert request["action_owner_alias"] == "newalias"
    assert request["action_owner_name"] == "New Owner"
    assert request["action_items"] == [
        {
            "ServiceId": "svc-001",
            "ActionItemId": "ai-001",
            "SLAType": "OutOfSla",
        }
    ]


def test_save_action_owner_calls_s360_client_with_expected_payload(mocker):
    mock_client = mocker.Mock()
    mock_client.save_action_owners.return_value = True
    mocker.patch("sfi_reporter.data.get_client", return_value=mock_client)

    ok, _msg, category = save_action_owner(_item(), "newalias", "New Owner")
    assert ok is True
    assert category == "success"
    mock_client.save_action_owners.assert_called_once_with(
        "kpi-001",
        "newalias",
        "New Owner",
        [{"ServiceId": "svc-001", "ActionItemId": "ai-001", "SLAType": "OutOfSla"}],
    )


def test_save_action_owner_does_not_call_api_when_validation_fails(mocker):
    mock_get_client = mocker.patch("sfi_reporter.data.get_client")
    ok, _msg, category = save_action_owner(_item(), " ", "")
    assert ok is False
    assert category == "validation_failure"
    mock_get_client.assert_not_called()


def test_save_action_owner_maps_auth_failure_to_user_friendly_message(mocker):
    mock_client = mocker.Mock()
    mock_client.save_action_owners.side_effect = Exception("AUTH token expired")
    mocker.patch("sfi_reporter.data.get_client", return_value=mock_client)

    ok, msg, category = save_action_owner(_item(), "newalias", "New Owner")
    assert ok is False
    assert category == "auth_failure"
    assert "session" in msg.lower() or "sign in" in msg.lower()


def test_save_action_owner_increments_session_success_counter(mocker):
    mock_client = mocker.Mock()
    mock_client.save_action_owners.return_value = True
    mocker.patch("sfi_reporter.data.get_client", return_value=mock_client)

    assert get_action_owner_save_success_count() == 0
    save_action_owner(_item(), "newalias", "New Owner")
    save_action_owner(_item(id="AI-002", S360_ActionItemId="ai-002"), "newalias", "New Owner")
    assert get_action_owner_save_success_count() == 2


def test_item_details_modal_exposes_action_owner_button(tk_root):
    dlg = ItemDetailsModal(tk_root, _item())
    buttons = []
    for frame_child in dlg._main_frame.winfo_children():
        for widget in getattr(frame_child, "winfo_children", lambda: [])():
            if widget.winfo_class() == "TButton":
                buttons.append(widget.cget("text"))
    assert any("Action Owner" in text for text in buttons)
    dlg.destroy()


def test_item_details_modal_owner_saved_updates_item_and_callback(tk_root):
    callback = MagicMock()
    item = _item()
    dlg = ItemDetailsModal(tk_root, item, on_owner_saved=callback)
    dlg._on_action_owner_saved(item, "newalias", "New Owner")
    assert item["ActionOwnerAlias"] == "newalias"
    assert item["ActionOwnerName"] == "New Owner"
    callback.assert_called_once_with(item, "newalias", "New Owner")
    dlg.destroy()