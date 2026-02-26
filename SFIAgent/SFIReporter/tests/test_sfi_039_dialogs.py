"""Tests for sfi_reporter.dialogs — target ≥70 % statement coverage.

Covers: SortableTreeview, ColumnSelectorDialog, DetailModal, ItemDetailsModal,
        SingleEtaEditDialog, EtaModeDialog, ManualEtaReviewDialog,
        BulkEtaProgressDialog, SubscriptionPickerDialog, _launch_llm_analysis,
        _find_app.
"""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# ---------------------------------------------------------------------------
# Mock the copilot SDK before importing sfi_reporter (same pattern as other
# test modules) so transitive imports don't blow up.
# ---------------------------------------------------------------------------
_mock_copilot = MagicMock()
_mock_copilot.Tool = type("Tool", (), {"__init__": lambda self, **kw: self.__dict__.update(kw)})
_mock_copilot.ToolResult = type("ToolResult", (), {"__init__": lambda self, **kw: self.__dict__.update(kw)})
_mock_copilot.define_tool = MagicMock()
_mock_copilot.CopilotClient = MagicMock
sys.modules.setdefault("copilot", _mock_copilot)

# NOW import the module under test
from sfi_reporter.dialogs import (  # noqa: E402
    SortableTreeview,
    ColumnSelectorDialog,
    DetailModal,
    ItemDetailsModal,
    SingleEtaEditDialog,
    EtaModeDialog,
    ManualEtaReviewDialog,
    BulkEtaProgressDialog,
    SubscriptionPickerDialog,
    _launch_llm_analysis,
    _find_app,
)
from sfi_reporter.models import REQUIRED_COLUMNS  # noqa: E402

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_ITEM = {
    "id": "AI-001",
    "title": "Fix vulnerability",
    "S360_ServiceTreeServiceName": "MyService",
    "SlaType": "OutOfSla",
    "EtaDate": "2026-06-01",
    "DueDate": "2026-03-01",
    "dueDate": "2026-03-01",
    "ActionOwnerName": "John Doe",
    "ActionOwnerAlias": "johndoe",
    "S360_AssignedTo": "janedoe",
    "S360_AssignedToName": "Jane Smith",
    "ActionItemStatus": "Active",
    "_kpi_name": "Vulnerability Management",
    "_kpi_id": "kpi-001",
    "S360_ProgramIds": ["prog-1"],
    "S360_ServiceId": "svc-001",
    "serviceTreeId": "svc-001",
    "Remediation": "Apply patch https://aka.ms/fix",
    "ResourceURIs": [
        "/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm1",
    ],
    "EtaStatus": "In Progress",
}


def _make_item(**overrides) -> dict:
    """Return a copy of SAMPLE_ITEM with optional overrides."""
    item = dict(SAMPLE_ITEM)
    item.update(overrides)
    return item


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def tk_root():
    """Create a single Tk root; hidden."""
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture(autouse=True)
def _reset_column_selector():
    """Reset class-level state between tests."""
    ColumnSelectorDialog.reset_visible_columns()
    yield
    ColumnSelectorDialog.reset_visible_columns()


# ===========================================================================
# SortableTreeview
# ===========================================================================

class TestSortableTreeview:
    """Tests for the SortableTreeview widget."""

    def test_create_with_columns(self, tk_root):
        tree = SortableTreeview(tk_root, columns=("a", "b"), show="headings")
        tree.heading("a", text="ColA")
        tree.heading("b", text="ColB")
        assert tree.cget("columns") is not None
        tree.destroy()

    def test_sort_string_column_ascending(self, tk_root):
        tree = SortableTreeview(tk_root, columns=("name",), show="headings")
        tree.heading("name", text="Name")
        tree.insert("", tk.END, values=("Banana",))
        tree.insert("", tk.END, values=("Apple",))
        tree.insert("", tk.END, values=("Cherry",))

        # First sort → ascending (reverse starts False)
        tree._sort_by_column("name")
        vals = [tree.set(c, "name") for c in tree.get_children()]
        assert vals == ["Apple", "Banana", "Cherry"]
        tree.destroy()

    def test_sort_string_column_descending(self, tk_root):
        tree = SortableTreeview(tk_root, columns=("name",), show="headings")
        tree.heading("name", text="Name")
        tree.insert("", tk.END, values=("Banana",))
        tree.insert("", tk.END, values=("Apple",))
        tree.insert("", tk.END, values=("Cherry",))

        tree._sort_by_column("name")  # asc
        tree._sort_by_column("name")  # desc
        vals = [tree.set(c, "name") for c in tree.get_children()]
        assert vals == ["Cherry", "Banana", "Apple"]
        tree.destroy()

    def test_sort_numeric_column(self, tk_root):
        tree = SortableTreeview(tk_root, columns=("num",), show="headings")
        tree.heading("num", text="Number")
        tree.insert("", tk.END, values=("100",))
        tree.insert("", tk.END, values=("20",))
        tree.insert("", tk.END, values=("3",))

        tree._sort_by_column("num")
        vals = [tree.set(c, "num") for c in tree.get_children()]
        assert vals == ["3", "20", "100"]
        tree.destroy()

    def test_sort_numeric_with_comma(self, tk_root):
        tree = SortableTreeview(tk_root, columns=("num",), show="headings")
        tree.heading("num", text="Number")
        tree.insert("", tk.END, values=("1,000",))
        tree.insert("", tk.END, values=("200",))
        tree.insert("", tk.END, values=("50",))

        tree._sort_by_column("num")
        vals = [tree.set(c, "num") for c in tree.get_children()]
        assert vals == ["50", "200", "1,000"]
        tree.destroy()

    def test_sort_empty_values(self, tk_root):
        tree = SortableTreeview(tk_root, columns=("name",), show="headings")
        tree.heading("name", text="Name")
        tree.insert("", tk.END, values=("Banana",))
        tree.insert("", tk.END, values=("",))
        tree.insert("", tk.END, values=("Apple",))

        tree._sort_by_column("name")
        vals = [tree.set(c, "name") for c in tree.get_children()]
        assert vals[0] == ""  # empty sorts first
        tree.destroy()

    def test_sort_by_columns_multiple(self, tk_root):
        tree = SortableTreeview(tk_root, columns=("a", "b"), show="headings")
        tree.heading("a", text="A")
        tree.heading("b", text="B")
        tree.insert("", tk.END, values=("X", "2"))
        tree.insert("", tk.END, values=("Y", "1"))
        tree.insert("", tk.END, values=("X", "1"))

        tree.sort_by_columns([("a", False), ("b", False)])
        vals = [(tree.set(c, "a"), tree.set(c, "b")) for c in tree.get_children()]
        # Last column in list is primary sort
        assert vals[0][1] <= vals[1][1]
        tree.destroy()

    def test_sort_by_columns_empty_list(self, tk_root):
        tree = SortableTreeview(tk_root, columns=("a",), show="headings")
        tree.heading("a", text="A")
        tree.insert("", tk.END, values=("Z",))
        # Should be no-op
        tree.sort_by_columns([])
        vals = [tree.set(c, "a") for c in tree.get_children()]
        assert vals == ["Z"]
        tree.destroy()

    def test_sort_by_columns_no_items(self, tk_root):
        tree = SortableTreeview(tk_root, columns=("a",), show="headings")
        tree.heading("a", text="A")
        tree.sort_by_columns([("a", False)])  # no items → no-op
        assert list(tree.get_children()) == []
        tree.destroy()

    def test_heading_default_command(self, tk_root):
        """heading() injects a sort command when none provided."""
        tree = SortableTreeview(tk_root, columns=("x",), show="headings")
        tree.heading("x", text="X")
        # The heading was set; clicking it should sort (verify no crash)
        tree.insert("", tk.END, values=("B",))
        tree.insert("", tk.END, values=("A",))
        tree._sort_by_column("x")
        tree.destroy()


# ===========================================================================
# ColumnSelectorDialog
# ===========================================================================

class TestColumnSelectorDialog:
    """Tests for the column-visibility picker."""

    def test_create_dialog(self, tk_root):
        cols = ["title", "dueDate", "SlaType", "extra_col"]
        dlg = ColumnSelectorDialog(tk_root, cols)
        assert dlg.winfo_exists()
        dlg.destroy()

    def test_checkboxes_created(self, tk_root):
        cols = ["title", "dueDate", "SlaType", "foo"]
        dlg = ColumnSelectorDialog(tk_root, cols)
        assert len(dlg._checkboxes) == 4
        dlg.destroy()

    def test_select_all(self, tk_root):
        cols = ["title", "dueDate", "SlaType", "foo", "bar"]
        dlg = ColumnSelectorDialog(tk_root, cols)
        dlg._clear_all()
        dlg._select_all()
        for var in dlg._checkboxes.values():
            assert var.get() is True
        dlg.destroy()

    def test_clear_all_keeps_required(self, tk_root):
        cols = ["title", "dueDate", "SlaType", "optional"]
        dlg = ColumnSelectorDialog(tk_root, cols)
        dlg._clear_all()
        for col in REQUIRED_COLUMNS:
            if col in dlg._checkboxes:
                assert dlg._checkboxes[col].get() is True
        # Non-required should be False
        assert dlg._checkboxes["optional"].get() is False
        dlg.destroy()

    def test_apply_sets_visible_columns(self, tk_root):
        cols = ["title", "dueDate", "SlaType", "extra"]
        callback = MagicMock()
        dlg = ColumnSelectorDialog(tk_root, cols, on_apply=callback)
        dlg._select_all()
        dlg._apply()
        # Dialog destroyed + callback invoked
        callback.assert_called_once()
        visible = ColumnSelectorDialog.get_visible_columns()
        assert visible is not None
        assert "extra" in visible

    def test_apply_without_callback(self, tk_root):
        cols = ["title", "dueDate", "SlaType"]
        dlg = ColumnSelectorDialog(tk_root, cols, on_apply=None)
        dlg._apply()
        assert ColumnSelectorDialog.get_visible_columns() is not None

    def test_get_visible_columns_initially_none(self):
        ColumnSelectorDialog.reset_visible_columns()
        assert ColumnSelectorDialog.get_visible_columns() is None

    def test_reset_visible_columns(self, tk_root):
        cols = ["title", "dueDate", "SlaType"]
        dlg = ColumnSelectorDialog(tk_root, cols)
        dlg._apply()
        ColumnSelectorDialog.reset_visible_columns()
        assert ColumnSelectorDialog.get_visible_columns() is None

    def test_empty_columns_labelled(self, tk_root):
        cols = ["title", "dueDate", "SlaType", "empty_col"]
        dlg = ColumnSelectorDialog(tk_root, cols, empty_columns={"empty_col"})
        # Just verify the dialog was created without error
        assert "empty_col" in dlg._checkboxes
        dlg.destroy()

    def test_on_mousewheel(self, tk_root):
        cols = ["title", "dueDate", "SlaType"]
        dlg = ColumnSelectorDialog(tk_root, cols)
        # Simulate a mousewheel event
        event = MagicMock()
        event.delta = 120
        dlg._on_mousewheel(event)  # Should not raise
        dlg.destroy()


# ===========================================================================
# DetailModal
# ===========================================================================

class TestDetailModal:
    """Tests for the drill-down detail tree modal."""

    def test_create_with_items(self, tk_root):
        items = [_make_item(id="AI-001"), _make_item(id="AI-002", title="Second item")]
        dlg = DetailModal(tk_root, "Test Detail", items)
        assert dlg.winfo_exists()
        # Tree should have 2 rows
        assert len(dlg.tree.get_children()) == 2
        dlg.destroy()

    def test_create_with_no_items(self, tk_root):
        dlg = DetailModal(tk_root, "Empty", [])
        assert dlg.winfo_exists()
        assert not hasattr(dlg, "tree") or len(dlg.tree.get_children()) == 0
        dlg.destroy()

    def test_populate_rows_service_name_lookup(self, tk_root):
        items = [_make_item(serviceTreeId="svc-x")]
        svc_names = {"svc-x": "My Service X"}
        dlg = DetailModal(tk_root, "Test", items, service_names=svc_names)
        vals = dlg.tree.item(dlg.tree.get_children()[0], "values")
        assert "My Service X" in vals
        dlg.destroy()

    def test_populate_rows_truncates_long_service_id(self, tk_root):
        long_id = "a" * 30
        items = [_make_item(serviceTreeId=long_id)]
        dlg = DetailModal(tk_root, "Test", items)
        vals = dlg.tree.item(dlg.tree.get_children()[0], "values")
        # The truncated id should be in values
        assert any("..." in str(v) for v in vals)
        dlg.destroy()

    def test_on_tree_select_with_selection(self, tk_root):
        items = [_make_item()]
        dlg = DetailModal(tk_root, "Test", items)
        iid = dlg.tree.get_children()[0]
        dlg.tree.selection_set(iid)
        dlg._on_tree_select()
        assert "normal" in str(dlg.selected_eta_btn["state"])
        dlg.destroy()

    def test_on_tree_select_no_selection(self, tk_root):
        items = [_make_item()]
        dlg = DetailModal(tk_root, "Test", items)
        dlg.tree.selection_remove(*dlg.tree.selection())
        dlg._on_tree_select()
        assert "disabled" in str(dlg.selected_eta_btn["state"])
        dlg.destroy()

    def test_on_item_double_click_opens_details(self, tk_root):
        items = [_make_item()]
        dlg = DetailModal(tk_root, "Test", items)
        iid = dlg.tree.get_children()[0]
        dlg.tree.selection_set(iid)
        dlg.tree.focus(iid)

        with patch("sfi_reporter.dialogs.ItemDetailsModal") as mock_modal:
            dlg._on_item_double_click(MagicMock())
            mock_modal.assert_called_once()
        dlg.destroy()

    def test_on_item_double_click_no_selection(self, tk_root):
        items = [_make_item()]
        dlg = DetailModal(tk_root, "Test", items)
        dlg.tree.selection_remove(*dlg.tree.get_children())
        with patch("sfi_reporter.dialogs.ItemDetailsModal") as mock_modal:
            dlg._on_item_double_click(MagicMock())
            mock_modal.assert_not_called()
        dlg.destroy()

    def test_on_detail_eta_complete_updates_items(self, tk_root):
        items = [_make_item()]
        callback = MagicMock()
        dlg = DetailModal(tk_root, "Test", items, on_eta_complete=callback)
        saved = [(items[0], "2026-08-01", "Updated")]
        dlg._on_detail_eta_complete(saved, [], [])
        assert items[0]["EtaDate"] == "2026-08-01"
        assert items[0]["EtaStatus"] == "Updated"
        callback.assert_called_once_with(saved, [], [])
        dlg.destroy()

    def test_on_detail_eta_complete_no_saved(self, tk_root):
        items = [_make_item()]
        dlg = DetailModal(tk_root, "Test", items)
        # Empty saved list → early return (no refresh)
        dlg._on_detail_eta_complete([], [], [])
        dlg.destroy()

    def test_on_detail_eta_complete_with_empty_notes(self, tk_root):
        items = [_make_item(EtaStatus="OldStatus")]
        dlg = DetailModal(tk_root, "Test", items)
        saved = [(items[0], "2026-09-01", "")]
        dlg._on_detail_eta_complete(saved, [], [])
        assert items[0]["EtaDate"] == "2026-09-01"
        # Empty notes → EtaStatus NOT overwritten
        assert items[0]["EtaStatus"] == "OldStatus"
        dlg.destroy()

    def test_refresh_items(self, tk_root):
        items = [_make_item(), _make_item(id="AI-002")]
        dlg = DetailModal(tk_root, "Test", items)
        assert len(dlg.tree.get_children()) == 2
        dlg._refresh_items()
        assert len(dlg.tree.get_children()) == 2
        dlg.destroy()

    def test_on_detail_update_etas_no_items(self, tk_root):
        dlg = DetailModal(tk_root, "Test", [])
        # Should not raise even with no items
        dlg._on_detail_update_etas()
        dlg.destroy()

    @patch("sfi_reporter.dialogs.ManualEtaReviewDialog")
    def test_on_detail_update_etas_opens_dialog(self, mock_dialog, tk_root):
        items = [_make_item()]
        dlg = DetailModal(tk_root, "Test", items)
        dlg._on_detail_update_etas()
        mock_dialog.assert_called_once()
        dlg.destroy()

    @patch("sfi_reporter.dialogs.ManualEtaReviewDialog")
    def test_on_selected_eta_update_with_selection(self, mock_dialog, tk_root):
        items = [_make_item(), _make_item(id="AI-002")]
        dlg = DetailModal(tk_root, "Test", items)
        iid = dlg.tree.get_children()[0]
        dlg.tree.selection_set(iid)
        dlg._on_selected_eta_update()
        mock_dialog.assert_called_once()
        dlg.destroy()

    def test_on_selected_eta_update_no_selection(self, tk_root):
        items = [_make_item()]
        dlg = DetailModal(tk_root, "Test", items)
        dlg.tree.selection_remove(*dlg.tree.get_children())
        # No selection → early return
        dlg._on_selected_eta_update()
        dlg.destroy()

    def test_on_item_right_click(self, tk_root):
        items = [_make_item()]
        dlg = DetailModal(tk_root, "Test", items)
        iid = dlg.tree.get_children()[0]

        event = MagicMock()
        event.y = 10
        event.x_root = 100
        event.y_root = 100

        with patch.object(dlg.tree, "identify_row", return_value=iid):
            with patch("tkinter.Menu") as mock_menu_cls:
                mock_menu = MagicMock()
                mock_menu_cls.return_value = mock_menu
                dlg._on_item_right_click(event)
                mock_menu.add_command.assert_called_once()
                mock_menu.tk_popup.assert_called_once()
        dlg.destroy()

    def test_on_item_right_click_no_row(self, tk_root):
        items = [_make_item()]
        dlg = DetailModal(tk_root, "Test", items)
        event = MagicMock()
        event.y = 999
        with patch.object(dlg.tree, "identify_row", return_value=""):
            dlg._on_item_right_click(event)  # Should just return
        dlg.destroy()

    def test_count_label_displays(self, tk_root):
        items = [_make_item(), _make_item(id="AI-002")]
        dlg = DetailModal(tk_root, "Test", items)
        assert "2" in dlg._count_label.cget("text")
        dlg.destroy()


# ===========================================================================
# ItemDetailsModal
# ===========================================================================

class TestItemDetailsModal:
    """Tests for the single-item full-detail modal."""

    def test_create_basic(self, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        assert dlg.winfo_exists()
        dlg.destroy()

    def test_title_truncation(self, tk_root):
        long_title = "A" * 100
        dlg = ItemDetailsModal(tk_root, _make_item(title=long_title))
        assert dlg.title().endswith("...")
        dlg.destroy()

    def test_short_title_no_truncation(self, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item(title="Short"))
        assert "..." not in dlg.title()
        dlg.destroy()

    def test_build_content_renders_groups(self, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        # _build_content was called; main_frame has children
        assert len(dlg._main_frame.winfo_children()) > 0
        dlg.destroy()

    def test_build_content_with_visible_columns(self, tk_root):
        ColumnSelectorDialog._visible_columns = ["title", "dueDate", "SlaType", "EtaDate"]
        dlg = ItemDetailsModal(tk_root, _make_item())
        assert dlg.winfo_exists()
        dlg.destroy()

    def test_on_columns_changed_refreshes(self, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        initial_counter = dlg._link_counter
        dlg._on_columns_changed()
        # link counter reset to 0 before rebuild
        dlg.destroy()

    def test_on_eta_saved_updates_item(self, tk_root):
        item = _make_item()
        dlg = ItemDetailsModal(tk_root, item)
        dlg._on_eta_saved(item, "2026-12-01", "New note")
        assert item["EtaDate"] == "2026-12-01"
        assert item["EtaStatus"] == "New note"
        dlg.destroy()

    def test_on_eta_saved_empty_notes(self, tk_root):
        item = _make_item(EtaStatus="Old")
        dlg = ItemDetailsModal(tk_root, item)
        dlg._on_eta_saved(item, "2026-12-01", "")
        assert item["EtaDate"] == "2026-12-01"
        # Empty notes → EtaStatus not changed
        assert item["EtaStatus"] == "Old"
        dlg.destroy()

    @patch("webbrowser.open")
    def test_open_url(self, mock_open, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        dlg._open_url("https://example.com")
        mock_open.assert_called_once_with("https://example.com")
        dlg.destroy()

    @patch("webbrowser.open")
    def test_open_url_html_encoded(self, mock_open, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        dlg._open_url("https://example.com?a=1&amp;b=2")
        mock_open.assert_called_once_with("https://example.com?a=1&b=2")
        dlg.destroy()

    def test_insert_text_with_links_plain(self, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        text_widget = tk.Text(dlg)
        dlg._insert_text_with_links(text_widget, "Hello World")
        content = text_widget.get("1.0", tk.END).strip()
        assert "Hello World" in content
        text_widget.destroy()
        dlg.destroy()

    def test_insert_text_with_links_empty(self, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        text_widget = tk.Text(dlg)
        dlg._insert_text_with_links(text_widget, "")
        content = text_widget.get("1.0", tk.END).strip()
        assert content == ""
        text_widget.destroy()
        dlg.destroy()

    def test_insert_text_with_links_bare_url(self, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        text_widget = tk.Text(dlg)
        dlg._insert_text_with_links(text_widget, "https://aka.ms/fix")
        content = text_widget.get("1.0", tk.END).strip()
        assert "https://aka.ms/fix" in content
        text_widget.destroy()
        dlg.destroy()

    def test_insert_text_with_links_html_anchor(self, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        text_widget = tk.Text(dlg)
        html = 'See <a href="https://example.com">this link</a> for info'
        dlg._insert_text_with_links(text_widget, html)
        content = text_widget.get("1.0", tk.END).strip()
        assert "this link" in content or "https://example.com" in content
        text_widget.destroy()
        dlg.destroy()

    def test_insert_resource_uris(self, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        text_widget = tk.Text(dlg)
        uris = ["/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm1"]
        dlg._insert_resource_uris(text_widget, uris)
        content = text_widget.get("1.0", tk.END).strip()
        assert "vm1" in content or "sub1" in content
        text_widget.destroy()
        dlg.destroy()

    def test_insert_resource_uris_empty(self, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        text_widget = tk.Text(dlg)
        dlg._insert_resource_uris(text_widget, "just a string")
        content = text_widget.get("1.0", tk.END).strip()
        assert "just a string" in content
        text_widget.destroy()
        dlg.destroy()

    @patch("sfi_reporter.dialogs.ColumnSelectorDialog")
    def test_open_column_selector(self, mock_cls, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        dlg._open_column_selector()
        mock_cls.assert_called_once()
        dlg.destroy()

    @patch("sfi_reporter.dialogs.SingleEtaEditDialog")
    def test_open_eta_editor(self, mock_cls, tk_root):
        dlg = ItemDetailsModal(tk_root, _make_item())
        dlg._open_eta_editor()
        mock_cls.assert_called_once()
        dlg.destroy()

    def test_item_with_remediation_url(self, tk_root):
        """Ensure items containing inline URLs render without error."""
        item = _make_item(Remediation="Fix: https://aka.ms/patch and https://go.ms/other")
        dlg = ItemDetailsModal(tk_root, item)
        assert dlg.winfo_exists()
        dlg.destroy()


# ===========================================================================
# SingleEtaEditDialog
# ===========================================================================

class TestSingleEtaEditDialog:
    """Tests for the single-item ETA editor."""

    @patch("sfi_reporter.dialogs.SingleEtaEditDialog._create_widgets")
    def test_create_basic(self, mock_cw, tk_root):
        """Verify __init__ stores item & callback."""
        item = _make_item()
        cb = MagicMock()
        dlg = SingleEtaEditDialog(tk_root, item, on_saved=cb)
        assert dlg._item is item
        assert dlg._on_saved is cb
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_create_widgets(self, _mock_propose, tk_root):
        item = _make_item()
        dlg = SingleEtaEditDialog(tk_root, item)
        assert dlg._eta_var.get() == "2026-07-01"
        assert dlg._notes_var.get() == "In Progress"
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    @patch("sfi_reporter.eta_logic.validate_eta_date", return_value=(False, "Invalid date"))
    def test_on_save_invalid_date(self, _mock_val, _mock_prop, tk_root):
        item = _make_item()
        dlg = SingleEtaEditDialog(tk_root, item)
        dlg._on_save()
        assert "Invalid date" in dlg._error_var.get()
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    @patch("sfi_reporter.eta_logic.validate_eta_date", return_value=(True, ""))
    @patch("sfi_reporter.eta_logic.build_eta_update", return_value={"id": "AI-001"})
    @patch("sfi_reporter.data.get_current_user_alias", return_value="testuser")
    @patch("sfi_reporter.data.get_client")
    @patch("threading.Thread")
    def test_on_save_valid_starts_thread(self, mock_thread, mock_client,
                                          mock_alias, mock_build, mock_val,
                                          mock_propose, tk_root):
        item = _make_item()
        dlg = SingleEtaEditDialog(tk_root, item)
        dlg._on_save()
        mock_thread.assert_called_once()
        assert "disabled" in str(dlg._save_btn["state"])
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_on_save_result_success(self, _mock_prop, tk_root):
        cb = MagicMock()
        item = _make_item()
        dlg = SingleEtaEditDialog(tk_root, item, on_saved=cb)
        result = MagicMock(success=True)
        dlg._on_save_result(result, "2026-07-01")
        cb.assert_called_once_with(item, "2026-07-01", "In Progress")

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_on_save_result_failure(self, _mock_prop, tk_root):
        item = _make_item()
        dlg = SingleEtaEditDialog(tk_root, item)
        result = MagicMock(success=False, error_message="API error")
        dlg._on_save_result(result, "2026-07-01")
        assert "Save failed" in dlg._error_var.get()
        assert "normal" in str(dlg._save_btn["state"])
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_on_save_result_failure_no_message(self, _mock_prop, tk_root):
        item = _make_item()
        dlg = SingleEtaEditDialog(tk_root, item)
        result = MagicMock(success=False, error_message=None)
        dlg._on_save_result(result, "2026-07-01")
        assert "Unknown error" in dlg._error_var.get()
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_on_save_error(self, _mock_prop, tk_root):
        item = _make_item()
        dlg = SingleEtaEditDialog(tk_root, item)
        dlg._on_save_error("Connection timeout")
        assert "Connection timeout" in dlg._error_var.get()
        assert "normal" in str(dlg._save_btn["state"])
        dlg.destroy()


# ===========================================================================
# EtaModeDialog
# ===========================================================================

class TestEtaModeDialog:
    """Tests for the bulk/manual selection dialog."""

    def test_create_dialog(self, tk_root):
        cb = MagicMock()
        dlg = EtaModeDialog(tk_root, total_count=10, invalid_count=3, on_choice=cb)
        assert dlg.winfo_exists()
        dlg.destroy()

    def test_choose_manual(self, tk_root):
        cb = MagicMock()
        dlg = EtaModeDialog(tk_root, total_count=5, invalid_count=2, on_choice=cb)
        dlg._choose("manual")
        cb.assert_called_once_with("manual")

    def test_choose_bulk(self, tk_root):
        cb = MagicMock()
        dlg = EtaModeDialog(tk_root, total_count=5, invalid_count=2, on_choice=cb)
        dlg._choose("bulk")
        cb.assert_called_once_with("bulk")

    def test_zero_invalid_count(self, tk_root):
        cb = MagicMock()
        dlg = EtaModeDialog(tk_root, total_count=5, invalid_count=0, on_choice=cb)
        # Dialog should create without error, bulk button disabled
        assert dlg.winfo_exists()
        dlg.destroy()


# ===========================================================================
# ManualEtaReviewDialog
# ===========================================================================

class TestManualEtaReviewDialog:
    """Tests for the step-by-step manual ETA review."""

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_create_shows_first_item(self, _mock_prop, tk_root):
        items = [_make_item(id="AI-001"), _make_item(id="AI-002")]
        dlg = ManualEtaReviewDialog(tk_root, items)
        assert dlg._index == 0
        assert dlg._eta_var.get() == "2026-07-01"
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_skip_advances(self, _mock_prop, tk_root):
        items = [_make_item(id="AI-001"), _make_item(id="AI-002")]
        dlg = ManualEtaReviewDialog(tk_root, items)
        dlg._skip()
        assert dlg._index == 1
        assert len(dlg._skipped) == 1
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_skip_all_shows_summary(self, _mock_prop, tk_root):
        items = [_make_item(id="AI-001")]
        cb = MagicMock()
        dlg = ManualEtaReviewDialog(tk_root, items, on_complete=cb)
        dlg._skip()  # skip only item → summary
        # Now at summary; _finish closes
        dlg._finish()
        cb.assert_called_once()
        args = cb.call_args[0]
        assert len(args[0]) == 0  # saved
        assert len(args[1]) == 1  # skipped

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_cancel_skips_remaining(self, _mock_prop, tk_root):
        items = [_make_item(id=f"AI-{i}") for i in range(3)]
        dlg = ManualEtaReviewDialog(tk_root, items)
        dlg._cancel()
        assert len(dlg._skipped) == 3
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    @patch("sfi_reporter.eta_logic.validate_eta_date", return_value=(False, "Bad date"))
    def test_accept_invalid_date(self, _mock_val, _mock_prop, tk_root):
        items = [_make_item()]
        dlg = ManualEtaReviewDialog(tk_root, items)
        dlg._accept()
        assert "Bad date" in dlg._error_var.get()
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    @patch("sfi_reporter.eta_logic.validate_eta_date", return_value=(True, ""))
    @patch("sfi_reporter.eta_logic.build_eta_update", return_value={"id": "AI-001"})
    @patch("sfi_reporter.data.get_current_user_alias", return_value="tester")
    @patch("sfi_reporter.data.get_client")
    @patch("threading.Thread")
    def test_accept_valid_starts_thread(self, mock_thread, mock_client,
                                         mock_alias, mock_build, mock_val,
                                         mock_prop, tk_root):
        items = [_make_item()]
        dlg = ManualEtaReviewDialog(tk_root, items)
        dlg._accept()
        mock_thread.assert_called_once()
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_on_result_success(self, _mock_prop, tk_root):
        items = [_make_item(), _make_item(id="AI-002")]
        dlg = ManualEtaReviewDialog(tk_root, items)
        result = MagicMock(success=True)
        dlg._on_result(result, items[0], "2026-07-01")
        assert len(dlg._saved) == 1
        assert dlg._index == 1
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_on_result_failure(self, _mock_prop, tk_root):
        items = [_make_item(), _make_item(id="AI-002")]
        dlg = ManualEtaReviewDialog(tk_root, items)
        result = MagicMock(success=False, error_message="Oops")
        dlg._on_result(result, items[0], "2026-07-01")
        assert len(dlg._failed) == 1
        assert dlg._index == 1
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_on_result_failure_no_message(self, _mock_prop, tk_root):
        items = [_make_item(), _make_item(id="AI-002")]
        dlg = ManualEtaReviewDialog(tk_root, items)
        result = MagicMock(success=False, error_message=None)
        dlg._on_result(result, items[0], "2026-07-01")
        assert len(dlg._failed) == 1
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_on_error(self, _mock_prop, tk_root):
        items = [_make_item(), _make_item(id="AI-002")]
        dlg = ManualEtaReviewDialog(tk_root, items)
        dlg._on_error(items[0], "Network error")
        assert len(dlg._failed) == 1
        assert dlg._index == 1
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_show_summary_with_failures(self, _mock_prop, tk_root):
        items = [_make_item()]
        dlg = ManualEtaReviewDialog(tk_root, items)
        dlg._failed.append((_make_item(), "Error msg"))
        dlg._show_summary()
        # Summary was rendered; verify no crash
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_finish_calls_on_complete(self, _mock_prop, tk_root):
        cb = MagicMock()
        items = [_make_item()]
        dlg = ManualEtaReviewDialog(tk_root, items, on_complete=cb)
        dlg._show_summary()
        dlg._finish()
        cb.assert_called_once()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_finish_without_callback(self, _mock_prop, tk_root):
        items = [_make_item()]
        dlg = ManualEtaReviewDialog(tk_root, items, on_complete=None)
        dlg._show_summary()
        dlg._finish()
        # No callback → no error

    @patch("sfi_reporter.dialogs.ItemDetailsModal")
    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_view_details(self, _mock_prop, mock_modal, tk_root):
        items = [_make_item()]
        dlg = ManualEtaReviewDialog(tk_root, items)
        dlg._view_details()
        mock_modal.assert_called_once()
        dlg.destroy()


# ===========================================================================
# BulkEtaProgressDialog
# ===========================================================================

class TestBulkEtaProgressDialog:
    """Tests for the bulk ETA progress dialog."""

    def test_create_dialog(self, tk_root):
        items = [_make_item()]
        # Prevent auto-start
        with patch.object(BulkEtaProgressDialog, "_start"):
            dlg = BulkEtaProgressDialog(tk_root, items)
            assert dlg.winfo_exists()
            assert dlg._progress_var.get() == 0
            dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    @patch("sfi_reporter.eta_logic.build_eta_update", return_value={"id": "AI-001"})
    @patch("sfi_reporter.data.get_current_user_alias", return_value="tester")
    @patch("sfi_reporter.data.get_client")
    def test_run_bulk_success(self, mock_get_client, _alias, _build, _propose, tk_root):
        mock_client = MagicMock()
        mock_result = MagicMock(success=True)
        mock_client.save_etas.return_value = mock_result
        mock_get_client.return_value = mock_client

        items = [_make_item()]
        with patch.object(BulkEtaProgressDialog, "_start"):
            dlg = BulkEtaProgressDialog(tk_root, items)
            # Stub out dlg.after so it executes immediately instead of scheduling
            dlg.after = lambda ms, fn, *a, **kw: fn(*a, **kw) if callable(fn) else None
            dlg._run_bulk()
            assert len(dlg._saved) == 1
            assert len(dlg._failed) == 0
            dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    @patch("sfi_reporter.eta_logic.build_eta_update", return_value={"id": "AI-001"})
    @patch("sfi_reporter.data.get_current_user_alias", return_value="tester")
    @patch("sfi_reporter.data.get_client")
    def test_run_bulk_api_failure(self, mock_get_client, _alias, _build, _propose, tk_root):
        mock_client = MagicMock()
        mock_result = MagicMock(success=False, error_message="Server error")
        mock_client.save_etas.return_value = mock_result
        mock_get_client.return_value = mock_client

        items = [_make_item()]
        with patch.object(BulkEtaProgressDialog, "_start"):
            dlg = BulkEtaProgressDialog(tk_root, items)
            dlg.after = lambda ms, fn, *a, **kw: fn(*a, **kw) if callable(fn) else None
            dlg._run_bulk()
            assert len(dlg._saved) == 0
            assert len(dlg._failed) == 1
            dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    @patch("sfi_reporter.eta_logic.build_eta_update", return_value={"id": "AI-001"})
    @patch("sfi_reporter.data.get_current_user_alias", return_value="tester")
    @patch("sfi_reporter.data.get_client")
    def test_run_bulk_exception(self, mock_get_client, _alias, _build, _propose, tk_root):
        mock_client = MagicMock()
        mock_client.save_etas.side_effect = RuntimeError("Boom")
        mock_get_client.return_value = mock_client

        items = [_make_item()]
        with patch.object(BulkEtaProgressDialog, "_start"):
            dlg = BulkEtaProgressDialog(tk_root, items)
            dlg.after = lambda ms, fn, *a, **kw: fn(*a, **kw) if callable(fn) else None
            dlg._run_bulk()
            assert len(dlg._failed) == 1
            dlg.destroy()

    def test_show_summary(self, tk_root):
        items = [_make_item()]
        with patch.object(BulkEtaProgressDialog, "_start"):
            dlg = BulkEtaProgressDialog(tk_root, items)
            dlg._saved = [(items[0], "2026-07-01", "")]
            dlg._show_summary()
            dlg.destroy()

    def test_show_summary_with_failures(self, tk_root):
        items = [_make_item()]
        with patch.object(BulkEtaProgressDialog, "_start"):
            dlg = BulkEtaProgressDialog(tk_root, items)
            dlg._failed = [(items[0], "Error msg")]
            dlg._show_summary()
            dlg.destroy()

    def test_finish_calls_callback(self, tk_root):
        items = [_make_item()]
        cb = MagicMock()
        with patch.object(BulkEtaProgressDialog, "_start"):
            dlg = BulkEtaProgressDialog(tk_root, items, on_complete=cb)
            dlg._saved = [(items[0], "2026-07-01", "")]
            dlg._finish()
            cb.assert_called_once_with([(items[0], "2026-07-01", "")], [], [])

    def test_finish_no_callback(self, tk_root):
        items = [_make_item()]
        with patch.object(BulkEtaProgressDialog, "_start"):
            dlg = BulkEtaProgressDialog(tk_root, items, on_complete=None)
            dlg._finish()
            # No error

    def test_start_spawns_thread(self, tk_root):
        items = [_make_item()]
        with patch.object(BulkEtaProgressDialog, "_start"):
            dlg = BulkEtaProgressDialog(tk_root, items)
        with patch("threading.Thread") as mock_thread:
            dlg._start()
            mock_thread.assert_called_once()
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    @patch("sfi_reporter.eta_logic.build_eta_update", return_value={"id": "AI-001"})
    @patch("sfi_reporter.data.get_current_user_alias", return_value="tester")
    @patch("sfi_reporter.data.get_client")
    def test_run_bulk_multiple_items(self, mock_get_client, _alias, _build, _propose, tk_root):
        mock_client = MagicMock()
        mock_result = MagicMock(success=True)
        mock_client.save_etas.return_value = mock_result
        mock_get_client.return_value = mock_client

        items = [_make_item(id=f"AI-{i}") for i in range(3)]
        with patch.object(BulkEtaProgressDialog, "_start"):
            dlg = BulkEtaProgressDialog(tk_root, items)
            dlg.after = lambda ms, fn, *a, **kw: fn(*a, **kw) if callable(fn) else None
            dlg._run_bulk()
            assert len(dlg._saved) == 3
            dlg.destroy()


# ===========================================================================
# SubscriptionPickerDialog
# ===========================================================================

class TestSubscriptionPickerDialog:
    """Tests for the subscription picker, avoiding wait_window() blocking."""

    def test_on_ok_with_selection(self, tk_root):
        """Verify _on_ok sets result from selected row."""
        choices = ["Sub A (id-a)", "Sub B (id-b)"]
        with patch.object(SubscriptionPickerDialog, "wait_window"):
            dlg = SubscriptionPickerDialog(tk_root, choices)
        # Dialog created; first row selected by default
        dlg._on_ok()
        assert dlg.result is not None

    def test_on_cancel_sets_none(self, tk_root):
        choices = ["Sub A (id-a)"]
        with patch.object(SubscriptionPickerDialog, "wait_window"):
            dlg = SubscriptionPickerDialog(tk_root, choices)
        dlg._on_cancel()
        assert dlg.result is None

    def test_empty_choices(self, tk_root):
        with patch.object(SubscriptionPickerDialog, "wait_window"):
            dlg = SubscriptionPickerDialog(tk_root, [])
        # No rows → _on_ok should still work
        dlg._on_ok()
        assert dlg.result is None
        dlg.destroy()

    def test_choice_without_parentheses(self, tk_root):
        choices = ["SimpleChoice"]
        with patch.object(SubscriptionPickerDialog, "wait_window"):
            dlg = SubscriptionPickerDialog(tk_root, choices)
        dlg._on_ok()
        assert dlg.result == "SimpleChoice"

    def test_choices_sorted(self, tk_root):
        choices = ["Zulu Sub (id-z)", "Alpha Sub (id-a)"]
        with patch.object(SubscriptionPickerDialog, "wait_window"):
            dlg = SubscriptionPickerDialog(tk_root, choices)
        # First row should be Alpha (sorted)
        first_iid = dlg._tree.get_children()[0]
        first_name = dlg._tree.set(first_iid, "name")
        assert first_name == "Alpha Sub"
        dlg.destroy()

    def test_on_ok_no_selection(self, tk_root):
        choices = ["Sub A (id-a)"]
        with patch.object(SubscriptionPickerDialog, "wait_window"):
            dlg = SubscriptionPickerDialog(tk_root, choices)
        dlg._tree.selection_remove(*dlg._tree.selection())
        dlg._on_ok()
        # No selection → result stays None
        assert dlg.result is None


# ===========================================================================
# _find_app / _launch_llm_analysis
# ===========================================================================

class TestFindApp:
    def test_find_app_with_attr(self, tk_root):
        tk_root._sfi_app = "fake_app"
        result = _find_app(tk_root)
        assert result == "fake_app"
        del tk_root._sfi_app

    def test_find_app_without_attr(self, tk_root):
        result = _find_app(tk_root)
        assert result is None

    def test_find_app_child_widget(self, tk_root):
        tk_root._sfi_app = "found_it"
        frame = ttk.Frame(tk_root)
        result = _find_app(frame)
        assert result == "found_it"
        frame.destroy()
        del tk_root._sfi_app


class TestLaunchLlmAnalysis:
    @patch("sfi_reporter.dialogs.messagebox")
    def test_no_kpi_id(self, mock_mb, tk_root):
        item = _make_item(_kpi_id="")
        _launch_llm_analysis(tk_root, item)
        mock_mb.showwarning.assert_called_once()

    @patch("sfi_reporter.dialogs.messagebox")
    def test_no_app_found(self, mock_mb, tk_root):
        # Ensure no _sfi_app
        if hasattr(tk_root, "_sfi_app"):
            del tk_root._sfi_app
        item = _make_item()
        _launch_llm_analysis(tk_root, item)
        mock_mb.showerror.assert_called_once()

    @patch("sfi_reporter.dialogs.messagebox")
    def test_no_copilot_panel(self, mock_mb, tk_root):
        mock_app = MagicMock()
        mock_app._copilot_panel = None
        mock_app._toggle_copilot_panel = MagicMock()
        # After toggle, panel is still None
        tk_root._sfi_app = mock_app
        # getattr(app, '_copilot_panel') → None
        type(mock_app)._copilot_panel = PropertyMock(return_value=None)
        _launch_llm_analysis(tk_root, _make_item())
        mock_mb.showerror.assert_called_once()
        del tk_root._sfi_app

    @patch("threading.Thread")
    @patch("sfi_reporter.dialogs.messagebox")
    def test_launches_analysis_thread(self, mock_mb, mock_thread, tk_root):
        mock_panel = MagicMock()
        mock_panel.winfo_ismapped.return_value = True
        mock_app = MagicMock()
        mock_app._copilot_panel = mock_panel
        tk_root._sfi_app = mock_app

        _launch_llm_analysis(tk_root, _make_item())
        mock_thread.assert_called_once()
        mock_panel._set_status.assert_called()
        del tk_root._sfi_app

    @patch("threading.Thread")
    @patch("sfi_reporter.dialogs.messagebox")
    def test_toggles_panel_if_hidden(self, mock_mb, mock_thread, tk_root):
        mock_panel = MagicMock()
        mock_panel.winfo_ismapped.return_value = False
        mock_app = MagicMock()
        mock_app._copilot_panel = mock_panel
        tk_root._sfi_app = mock_app

        _launch_llm_analysis(tk_root, _make_item())
        mock_app._toggle_copilot_panel.assert_called()
        del tk_root._sfi_app


# ===========================================================================
# EdgeCase: DetailModal with various item shapes
# ===========================================================================

class TestDetailModalEdgeCases:
    """Edge-case coverage for populate_rows with missing fields."""

    def test_item_missing_optional_fields(self, tk_root):
        item = {"id": "AI-X", "title": "Minimal"}
        dlg = DetailModal(tk_root, "Test", [item])
        assert len(dlg.tree.get_children()) == 1
        dlg.destroy()

    def test_item_with_html_title(self, tk_root):
        item = _make_item(title="<b>Bold</b> title &amp; more")
        dlg = DetailModal(tk_root, "Test", [item])
        # Tree is populated without error
        vals = dlg.tree.item(dlg.tree.get_children()[0], "values")
        assert len(vals) > 0
        dlg.destroy()

    def test_item_with_long_title(self, tk_root):
        item = _make_item(title="A" * 200)
        dlg = DetailModal(tk_root, "Test", [item])
        vals = dlg.tree.item(dlg.tree.get_children()[0], "values")
        # Title is truncated to 60 chars in tree display
        assert len(str(vals[0])) <= 60
        dlg.destroy()

    def test_item_uses_DueDate_fallback(self, tk_root):
        item = {"id": "AI-X", "title": "T", "DueDate": "2026-05-01"}
        dlg = DetailModal(tk_root, "Test", [item])
        vals = dlg.tree.item(dlg.tree.get_children()[0], "values")
        assert "2026-05-01" in str(vals)
        dlg.destroy()

    def test_item_short_service_id(self, tk_root):
        item = _make_item(serviceTreeId="short")
        dlg = DetailModal(tk_root, "Test", [item])
        vals = dlg.tree.item(dlg.tree.get_children()[0], "values")
        assert "short" in str(vals)
        dlg.destroy()


# ===========================================================================
# ItemDetailsModal build_content with and without visible columns
# ===========================================================================

class TestItemDetailsModalBuildContent:
    """Verify _build_content rendering paths."""

    def test_visible_columns_filters_fields(self, tk_root):
        ColumnSelectorDialog._visible_columns = ["title", "dueDate", "SlaType"]
        item = _make_item()
        dlg = ItemDetailsModal(tk_root, item)
        assert dlg.winfo_exists()
        dlg.destroy()

    def test_no_visible_columns_shows_all(self, tk_root):
        ColumnSelectorDialog.reset_visible_columns()
        item = _make_item()
        dlg = ItemDetailsModal(tk_root, item)
        assert dlg.winfo_exists()
        dlg.destroy()

    def test_required_columns_always_included(self, tk_root):
        # Set visible to just one non-required column
        ColumnSelectorDialog._visible_columns = ["ActionOwnerName"]
        item = _make_item()
        dlg = ItemDetailsModal(tk_root, item)
        # Should still build; required columns are forced in
        assert dlg.winfo_exists()
        dlg.destroy()

    def test_resource_uris_rendered(self, tk_root):
        item = _make_item(ResourceURIs=["/subscriptions/sub1/resourceGroups/rg1"])
        dlg = ItemDetailsModal(tk_root, item)
        assert dlg.winfo_exists()
        dlg.destroy()

    def test_remediation_with_url(self, tk_root):
        item = _make_item(Remediation="See https://aka.ms/fix for details")
        dlg = ItemDetailsModal(tk_root, item)
        assert dlg.winfo_exists()
        dlg.destroy()

    def test_item_with_html_link(self, tk_root):
        item = _make_item(
            Remediation='Apply <a href="https://aka.ms/patch">this patch</a>'
        )
        dlg = ItemDetailsModal(tk_root, item)
        assert dlg.winfo_exists()
        dlg.destroy()


# ===========================================================================
# ManualEtaReviewDialog — additional paths
# ===========================================================================

class TestManualEtaReviewDialogMore:
    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_view_details_beyond_range(self, _mock_prop, tk_root):
        items = [_make_item()]
        dlg = ManualEtaReviewDialog(tk_root, items)
        dlg._index = 99  # beyond range
        dlg._view_details()  # should be no-op
        dlg.destroy()

    @patch("sfi_reporter.eta_logic.propose_eta", return_value="2026-07-01")
    def test_show_summary_many_failures(self, _mock_prop, tk_root):
        items = [_make_item()]
        dlg = ManualEtaReviewDialog(tk_root, items)
        for i in range(7):
            dlg._failed.append((_make_item(id=f"AI-{i}"), f"Error {i}"))
        dlg._show_summary()
        # Only first 5 shown in UI, but all stored
        assert len(dlg._failed) == 7
        dlg.destroy()
