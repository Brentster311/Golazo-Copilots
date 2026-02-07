"""
SFI-015: Detail Modal Color Indicators — Automated Tests

Verifies that section headers in the ItemDetailsModal use the correct
colored circle emoji indicators:
  - Status: 🔴 (red circle)
  - Dates: 🔵 (blue circle)
  - Ownership: 🟣 (purple circle)
  - Service & Program: ⚫ (black circle)

Tests verify actual production code via source inspection and
the group_item_fields() pure function.
"""

import inspect

from sfi_reporter.tk_app import group_item_fields, FIELD_GROUPS


# ── TC-001 through TC-004: Section header emoji verification ────────

class TestSectionHeaderEmojis:
    """Verify the production code group_titles dict contains correct emojis.

    Since group_titles is a local variable inside _build_content(), we inspect
    the source code to verify the emoji strings without instantiating tkinter.
    """

    @staticmethod
    def _get_build_content_source() -> str:
        """Get the source code of ItemDetailsModal._build_content."""
        # Import inside to avoid tkinter initialization at module level
        from sfi_reporter.tk_app import ItemDetailsModal
        return inspect.getsource(ItemDetailsModal._build_content)

    def test_status_header_has_red_circle(self):
        """TC-001: Status section header uses 🔴 red circle."""
        source = self._get_build_content_source()
        assert "'status': '🔴 Status'" in source

    def test_dates_header_has_blue_circle(self):
        """TC-002: Dates section header uses 🔵 blue circle."""
        source = self._get_build_content_source()
        assert "'dates': '🔵 Dates'" in source

    def test_ownership_header_has_purple_circle(self):
        """TC-003: Ownership section header uses 🟣 purple circle."""
        source = self._get_build_content_source()
        assert "'ownership': '🟣 Ownership'" in source

    def test_service_program_header_has_black_circle(self):
        """TC-004: Service & Program section header uses ⚫ black circle."""
        source = self._get_build_content_source()
        assert "'service_program': '⚫ Service & Program'" in source

    def test_no_old_calendar_emoji_for_dates(self):
        """Regression: Dates should not use the old 📅 calendar emoji."""
        source = self._get_build_content_source()
        assert "'dates': '📅" not in source

    def test_no_old_person_emoji_for_ownership(self):
        """Regression: Ownership should not use the old 👤 person emoji."""
        source = self._get_build_content_source()
        assert "'ownership': '👤" not in source

    def test_no_old_wrench_emoji_for_service(self):
        """Regression: Service & Program should not use the old 🔧 wrench emoji."""
        source = self._get_build_content_source()
        assert "'service_program': '🔧" not in source

    def test_unchanged_sections_preserved(self):
        """Non-circle sections retain their original emojis."""
        source = self._get_build_content_source()
        assert "'identity': '📋 Identity'" in source
        assert "'resources': '🔗 Resources & Details'" in source
        assert "'other': '📎 Other'" in source

    def test_all_eight_groups_present_in_group_titles(self):
        """Verify group_titles has entries for all 8 section groups."""
        source = self._get_build_content_source()
        for group in ['identity', 'status', 'dates', 'ownership',
                      'service_program', 'subscription', 'resources', 'other']:
            assert f"'{group}':" in source, f"Missing group_titles entry for '{group}'"

    def test_group_order_in_build_content(self):
        """Verify groups are rendered in the correct order."""
        source = self._get_build_content_source()
        expected_order = [
            'identity', 'status', 'dates', 'ownership',
            'service_program', 'subscription', 'resources', 'other'
        ]
        # The group_order list should appear in source
        assert "group_order = ['identity', 'status', 'dates', 'ownership', 'service_program'" in source


# ── TC-005: group_item_fields pure function ─────────────────────────

class TestGroupItemFields:
    """Verify the grouping function correctly categorizes item fields."""

    def test_status_fields_grouped(self):
        """Status-related fields are placed in the 'status' group."""
        item = {'SlaType': 0, 'classificationType': 'SFI'}
        groups = group_item_fields(item)
        field_names = [name for name, _ in groups['status']]
        assert 'SlaType' in field_names
        assert 'classificationType' in field_names

    def test_date_fields_grouped(self):
        """Date-related fields are placed in the 'dates' group."""
        item = {'dueDate': '2026-01-15', 'EtaDate': '2026-02-01'}
        groups = group_item_fields(item)
        field_names = [name for name, _ in groups['dates']]
        assert 'dueDate' in field_names
        assert 'EtaDate' in field_names

    def test_ownership_fields_grouped(self):
        """Ownership-related fields are placed in the 'ownership' group."""
        item = {'assignedTo': 'user@ms.com', 'ActionOwnerAlias': 'testuser'}
        groups = group_item_fields(item)
        field_names = [name for name, _ in groups['ownership']]
        assert 'assignedTo' in field_names
        assert 'ActionOwnerAlias' in field_names

    def test_service_program_fields_grouped(self):
        """Service/program fields are placed in the 'service_program' group."""
        item = {'serviceTreeId': 'abc-123', 'S360_ProgramIds': ['p1']}
        groups = group_item_fields(item)
        field_names = [name for name, _ in groups['service_program']]
        assert 'serviceTreeId' in field_names
        assert 'S360_ProgramIds' in field_names

    def test_unknown_fields_go_to_other(self):
        """Fields not in FIELD_GROUPS are placed in 'other'."""
        item = {'customField': 'some value'}
        groups = group_item_fields(item)
        field_names = [name for name, _ in groups['other']]
        assert 'customField' in field_names

    def test_empty_values_excluded(self):
        """Fields with empty/None values are excluded from groups."""
        item = {'SlaType': '', 'dueDate': None, 'title': 'Test'}
        groups = group_item_fields(item)
        # SlaType with empty string should be excluded
        status_fields = [name for name, _ in groups['status']]
        assert 'SlaType' not in status_fields

    def test_all_field_groups_have_keys(self):
        """FIELD_GROUPS constant covers the expected section keys."""
        expected = {'identity', 'status', 'dates', 'ownership',
                    'service_program', 'subscription', 'resources'}
        assert set(FIELD_GROUPS.keys()) == expected


# ── TC-006: Header font tag ─────────────────────────────────────────

class TestHeaderStyling:
    """Verify the text widget header tag is configured for readability."""

    def test_header_tag_uses_segoe_ui_bold(self):
        """Header tag should use Segoe UI bold for emoji readability."""
        from sfi_reporter.tk_app import ItemDetailsModal
        source = inspect.getsource(ItemDetailsModal._build_content)
        assert "tag_configure('header', font=(\"Segoe UI\"" in source
        assert '"bold"' in source
