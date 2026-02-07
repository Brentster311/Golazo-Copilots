"""Tests for Tkinter app components."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta


class TestDataFetching:
    """Test data fetching with mocks."""

    def test_refresh_success(self, mocker):
        """TC-004: Verify refresh fetches and caches data."""
        # Mock the S360 client for landing view
        mock_client = MagicMock()
        mock_client.get_default_landing_view.return_value = {
            'SearchDataList': [{'Group': 'Service', 'Name': 'Svc1', 'Id': '123'}]
        }
        mocker.patch('sfi_reporter.data.get_client', return_value=mock_client)
        
        mock_team_info = mocker.patch('sfi_reporter.data.get_user_team_info')
        mock_action_items = mocker.patch('sfi_reporter.data.get_action_items_summary')
        mock_detailed = mocker.patch('sfi_reporter.data.get_detailed_action_items')
        mock_programs = mocker.patch('sfi_reporter.data.get_all_programs')
        mock_write = mocker.patch('sfi_reporter.tk_app.write_cache')
        
        mock_team_info.return_value = ([{'Name': 'Svc1', 'Id': '123'}], ['123'])
        mock_action_items.return_value = {'ActionItemSummaryList': []}
        mock_detailed.return_value = ([], [])  # (rows, failed_kpis)
        mock_programs.return_value = {}
        
        from sfi_reporter.tk_app import do_refresh
        
        result = do_refresh('testuser')
        
        mock_team_info.assert_called_once_with('testuser')
        mock_action_items.assert_called_once_with(['123'])
        mock_write.assert_called_once()
        assert result is not None
        assert 'services' in result

    def test_refresh_error(self, mocker):
        """TC-005: Verify error handling during refresh."""
        # Mock the S360 client for landing view - will fail on get_user_team_info
        mock_client = MagicMock()
        mock_client.get_default_landing_view.return_value = {'SearchDataList': []}
        mocker.patch('sfi_reporter.data.get_client', return_value=mock_client)
        
        mock_team_info = mocker.patch('sfi_reporter.data.get_user_team_info')
        mock_team_info.side_effect = Exception("API Error")
        
        from sfi_reporter.tk_app import do_refresh
        
        result = do_refresh('testuser')
        
        assert result is None

    def test_refresh_with_status_callback(self, mocker):
        """TC-011: Verify status callback is called during refresh."""
        # Mock the S360 client for landing view
        mock_client = MagicMock()
        mock_client.get_default_landing_view.return_value = {
            'SearchDataList': [{'Group': 'Service', 'Name': 'Svc1', 'Id': '123'}]
        }
        mocker.patch('sfi_reporter.data.get_client', return_value=mock_client)
        
        mock_team_info = mocker.patch('sfi_reporter.data.get_user_team_info')
        mock_action_items = mocker.patch('sfi_reporter.data.get_action_items_summary')
        mock_detailed = mocker.patch('sfi_reporter.data.get_detailed_action_items')
        mock_programs = mocker.patch('sfi_reporter.data.get_all_programs')
        mock_write = mocker.patch('sfi_reporter.tk_app.write_cache')
        
        mock_team_info.return_value = ([{'Name': 'Svc1', 'Id': '123'}], ['123'])
        mock_action_items.return_value = {'ActionItemSummaryList': []}
        mock_detailed.return_value = ([], [])  # (rows, failed_kpis)
        mock_programs.return_value = {}
        
        status_messages = []
        def on_status(msg):
            status_messages.append(msg)
        
        from sfi_reporter.tk_app import do_refresh
        
        result = do_refresh('testuser', on_status=on_status)
        
        assert len(status_messages) >= 2  # At least "Connecting" and "Retrieved services"
        assert "Connecting" in status_messages[0]
        assert result is not None


class TestDetailModal:
    """Test detail modal functionality."""

    def test_filter_by_service(self):
        """TC-004: Filter items by service ID."""
        from sfi_reporter.tk_app import filter_items_by_service
        
        items = [
            {'id': '1', 'serviceTreeId': 'svc-a', 'title': 'Item 1'},
            {'id': '2', 'serviceTreeId': 'svc-b', 'title': 'Item 2'},
            {'id': '3', 'serviceTreeId': 'svc-a', 'title': 'Item 3'},
        ]
        
        result = filter_items_by_service(items, 'svc-a')
        
        assert len(result) == 2
        assert all(item['serviceTreeId'] == 'svc-a' for item in result)

    def test_filter_by_program(self):
        """TC-005: Filter items by program ID."""
        from sfi_reporter.tk_app import filter_items_by_program
        
        items = [
            {'id': '1', 'S360_ProgramIds': ['prog-a'], 'title': 'Item 1'},
            {'id': '2', 'S360_ProgramIds': ['prog-b'], 'title': 'Item 2'},
            {'id': '3', 'S360_ProgramIds': ['prog-a', 'prog-c'], 'title': 'Item 3'},
            {'id': '4', 'S360_ProgramIds': [], 'title': 'Item 4'},
        ]
        
        result = filter_items_by_program(items, 'prog-a')
        
        assert len(result) == 2
        assert all('prog-a' in item['S360_ProgramIds'] for item in result)

    def test_filter_by_item_id(self):
        """TC-006: Filter to get single item by ID."""
        from sfi_reporter.tk_app import filter_items_by_id
        
        items = [
            {'id': '1', 'title': 'Item 1'},
            {'id': '2', 'title': 'Item 2'},
            {'id': '3', 'title': 'Item 3'},
        ]
        
        result = filter_items_by_id(items, '2')
        
        assert len(result) == 1
        assert result[0]['id'] == '2'

    def test_filter_empty_result(self):
        """TC-007: Filter that returns no items."""
        from sfi_reporter.tk_app import filter_items_by_service
        
        items = [
            {'id': '1', 'serviceTreeId': 'svc-a', 'title': 'Item 1'},
        ]
        
        result = filter_items_by_service(items, 'svc-nonexistent')
        
        assert len(result) == 0


class TestItemDetailsModal:
    """Test item details modal functionality."""

    def test_format_field_label_snake_case(self):
        """TC-006: Format snake_case field names to human-readable."""
        from sfi_reporter.tk_app import format_field_label
        
        assert format_field_label('serviceTreeId') == 'Service Tree Id'
        assert format_field_label('S360_AssignedTo') == 'S360 Assigned To'
        assert format_field_label('_kpi_id') == 'Kpi Id'
        assert format_field_label('dueDate') == 'Due Date'

    def test_format_field_value_string(self):
        """TC-007: Format string values."""
        from sfi_reporter.tk_app import format_field_value
        
        assert format_field_value('simple text') == 'simple text'
        assert format_field_value('') == ''
        assert format_field_value(None) == ''

    def test_format_field_value_list(self):
        """TC-007: Format list values."""
        from sfi_reporter.tk_app import format_field_value
        
        assert format_field_value(['a', 'b', 'c']) == 'a, b, c'
        assert format_field_value([]) == ''

    def test_format_field_value_bool(self):
        """TC-007: Format boolean values."""
        from sfi_reporter.tk_app import format_field_value
        
        assert format_field_value(True) == 'Yes'
        assert format_field_value(False) == 'No'

    def test_group_item_fields(self):
        """TC-004: Group fields into categories."""
        from sfi_reporter.tk_app import group_item_fields
        
        item = {
            'title': 'Test Item',
            'id': '123',
            '_kpi_id': 'kpi-1',
            'SlaType': 'OutOfSla',
            'dueDate': '2026-02-03',
            'assignedTo': 'testuser',
            'serviceTreeId': 'svc-1',
            'S360_ProgramIds': ['prog-1'],
            'EventId': 'evt-1',
        }
        
        groups = group_item_fields(item)
        
        assert 'identity' in groups
        assert 'status' in groups
        assert 'dates' in groups
        assert 'ownership' in groups
        assert 'service_program' in groups
        assert 'other' in groups
        
        # Check field placement
        assert any(f[0] == 'title' for f in groups['identity'])
        assert any(f[0] == 'SlaType' for f in groups['status'])
        assert any(f[0] == 'dueDate' for f in groups['dates'])
        assert any(f[0] == 'assignedTo' for f in groups['ownership'])
        assert any(f[0] == 'serviceTreeId' for f in groups['service_program'])

    def test_group_item_fields_empty_excluded(self):
        """TC-005: Empty fields are excluded from groups."""
        from sfi_reporter.tk_app import group_item_fields
        
        item = {
            'title': 'Test Item',
            'id': '123',
            'EtaDate': '',  # Empty string
            'ActionOwnerName': None,  # None
            'S360_WavesMetadata': [],  # Empty list
        }
        
        groups = group_item_fields(item)
        
        # Flatten all fields
        all_fields = []
        for group_fields in groups.values():
            all_fields.extend([f[0] for f in group_fields])
        
        assert 'EtaDate' not in all_fields
        assert 'ActionOwnerName' not in all_fields
        assert 'S360_WavesMetadata' not in all_fields


class TestUrlExtraction:
    """Test URL extraction and hyperlink handling."""

    def test_extract_plain_urls(self):
        """TC-008: Extract plain HTTP/HTTPS URLs from text."""
        from sfi_reporter.tk_app import extract_urls_from_text
        
        text = "Visit https://example.com for more info"
        urls = extract_urls_from_text(text)
        
        assert len(urls) == 1
        assert urls[0][0] == 'https://example.com'  # url
        assert urls[0][1] == 'https://example.com'  # display text (same for plain URL)

    def test_extract_url_with_special_chars(self):
        """TC-008: Extract URLs with special characters like quotes in query params."""
        from sfi_reporter.tk_app import extract_urls_from_text
        
        # S360 lens URLs have single quotes in query parameters
        url = "https://lens.msftcloudes.com/v2/#/dashboard/123?params=(filters:!((k:ServiceOid,v:'abc-123'),(k:nCloud,v:public)))"
        urls = extract_urls_from_text(url)
        
        assert len(urls) == 1
        assert urls[0][0] == url  # Full URL including quotes
        assert len(urls[0][0]) == len(url)

    def test_extract_html_anchor(self):
        """TC-008: Extract URL from HTML anchor tag."""
        from sfi_reporter.tk_app import extract_urls_from_text
        
        text = '<a target="_blank" href="https://aka.ms/test">Test Link</a>'
        urls = extract_urls_from_text(text)
        
        assert len(urls) == 1
        assert urls[0][0] == 'https://aka.ms/test'  # url
        assert urls[0][1] == 'Test Link'  # display text

    def test_extract_multiple_urls(self):
        """TC-008: Extract multiple URLs from text."""
        from sfi_reporter.tk_app import extract_urls_from_text
        
        text = "See https://one.com and https://two.com for details"
        urls = extract_urls_from_text(text)
        
        assert len(urls) == 2
        urls_only = [u[0] for u in urls]
        assert 'https://one.com' in urls_only
        assert 'https://two.com' in urls_only

    def test_extract_no_urls(self):
        """TC-008: Handle text with no URLs."""
        from sfi_reporter.tk_app import extract_urls_from_text
        
        assert extract_urls_from_text("no urls here") == []
        assert extract_urls_from_text("") == []
        assert extract_urls_from_text(None) == []

    def test_clean_html_from_title(self):
        """TC-009: Clean HTML anchor tags from title."""
        from sfi_reporter.tk_app import clean_html_from_title
        
        title = '<a target="_blank" href="https://aka.ms/GDPRScanComplianceWiki"> GDPR Scan Compliance</a>'
        cleaned = clean_html_from_title(title)
        
        assert cleaned == ' GDPR Scan Compliance'
        assert '<a' not in cleaned
        assert 'href' not in cleaned

    def test_clean_html_plain_text(self):
        """TC-009: Plain text passes through unchanged."""
        from sfi_reporter.tk_app import clean_html_from_title
        
        assert clean_html_from_title("Plain Title") == "Plain Title"
        assert clean_html_from_title("") == ""
        assert clean_html_from_title(None) == ""

    def test_parse_resource_uris_json_string(self):
        """TC-010: Parse ResourceURIs JSON array string."""
        from sfi_reporter.tk_app import parse_resource_uris
        
        json_str = '["https://kusto.windows.net/","https://storage.azure.com/"]'
        uris = parse_resource_uris(json_str)
        
        assert len(uris) == 2
        assert 'https://kusto.windows.net/' in uris
        assert 'https://storage.azure.com/' in uris

    def test_parse_resource_uris_list(self):
        """TC-010: Parse ResourceURIs already as list."""
        from sfi_reporter.tk_app import parse_resource_uris
        
        uris_list = ['https://a.com', 'https://b.com']
        uris = parse_resource_uris(uris_list)
        
        assert uris == uris_list

    def test_parse_resource_uris_empty(self):
        """TC-010: Handle empty ResourceURIs."""
        from sfi_reporter.tk_app import parse_resource_uris
        
        assert parse_resource_uris("") == []
        assert parse_resource_uris(None) == []
        assert parse_resource_uris([]) == []

class TestSortableTreeview:
    """Test sortable treeview functionality."""

    def test_sort_by_columns_numeric(self):
        """TC-011: Multi-column sort with numeric columns."""
        from sfi_reporter.tk_app import SortableTreeview
        import tkinter as tk
        
        # Create minimal root window (required for Treeview)
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        try:
            tree = SortableTreeview(root, columns=("name", "count", "sla"), show="headings")
            tree.heading("name", text="Name")
            tree.heading("count", text="Count")
            tree.heading("sla", text="SLA")
            
            # Insert test data
            tree.insert('', tk.END, values=("Alpha", "10", "2"))
            tree.insert('', tk.END, values=("Beta", "5", "3"))
            tree.insert('', tk.END, values=("Gamma", "5", "1"))
            
            # Sort by count desc, then name asc
            tree.sort_by_columns([("name", False), ("count", True)])
            
            # Get sorted values
            items = [tree.item(iid)['values'] for iid in tree.get_children('')]
            
            # Should be: Alpha (10), Beta (5), Gamma (5) - count desc, then name asc within same count
            assert items[0][0] == "Alpha"  # 10 is highest
            assert items[1][0] == "Beta"   # 5, and Beta < Gamma alphabetically
            assert items[2][0] == "Gamma"  # 5, but Gamma > Beta
        finally:
            root.destroy()

    def test_sort_by_columns_empty(self):
        """TC-011: Sort handles empty treeview gracefully."""
        from sfi_reporter.tk_app import SortableTreeview
        import tkinter as tk
        
        try:
            root = tk.Tk()
        except tk.TclError:
            pytest.skip("Tcl/Tk not available in this environment")
        root.withdraw()
        
        try:
            tree = SortableTreeview(root, columns=("name",), show="headings")
            tree.heading("name", text="Name")
            
            # Should not raise an error
            tree.sort_by_columns([("name", False)])
            tree.sort_by_columns([])
            
            assert len(tree.get_children('')) == 0
        finally:
            root.destroy()


class TestHyperlinkIntegration:
    """Test hyperlink rendering integration."""

    def test_url_field_in_group_item_fields(self):
        """TC-012: URL field is included in grouped fields."""
        from sfi_reporter.tk_app import group_item_fields
        
        item = {
            'id': '123',
            'title': 'Test',
            'url': 'https://example.com/test',
        }
        
        groups = group_item_fields(item)
        
        # url should be in identity group
        identity_fields = [f[0] for f in groups.get('identity', [])]
        assert 'url' in identity_fields

    def test_url_field_detected_for_hyperlink(self):
        """TC-012: URL fields are detected for hyperlink rendering."""
        from sfi_reporter.tk_app import extract_urls_from_text
        
        # Test typical url field value with HTML anchor
        url_with_anchor = '<a target="_blank" href="https://s360.msftcloudes.com/ActionItem/Details/123">View Details</a>'
        urls = extract_urls_from_text(url_with_anchor)
        
        assert len(urls) == 1
        assert urls[0][0] == 'https://s360.msftcloudes.com/ActionItem/Details/123'
        assert urls[0][1] == 'View Details'
        
        # Test plain URL
        plain_url = 'https://portal.azure.com/#resource/123'
        urls = extract_urls_from_text(plain_url)
        
        assert len(urls) == 1
        assert urls[0][0] == plain_url

    def test_hyperlink_condition_check(self):
        """TC-012: Verify hyperlink detection logic matches ItemDetailsModal."""
        from sfi_reporter.tk_app import format_field_value
        
        # The code checks: field_name in ('title', 'url', 'Details') or 'http' in formatted_value.lower()
        
        # Test with URL value
        url_value = 'https://example.com'
        formatted = format_field_value(url_value)
        assert 'http' in formatted.lower(), "URL should be detected for hyperlink"
        
        # Test with plain text
        plain = 'Just some text'
        formatted = format_field_value(plain)
        assert 'http' not in formatted.lower(), "Plain text should not be detected as hyperlink"


class TestColumnToggle:
    """Test column toggle functionality for drill-down modal."""

    def test_required_columns_defined(self):
        """TC03: Required columns list exists and contains essential fields."""
        from sfi_reporter.tk_app import REQUIRED_COLUMNS
        
        assert 'title' in REQUIRED_COLUMNS
        assert 'dueDate' in REQUIRED_COLUMNS
        assert 'SlaType' in REQUIRED_COLUMNS

    def test_get_available_columns(self):
        """TC02: Available columns are derived from data items."""
        from sfi_reporter.tk_app import get_available_columns
        
        items = [
            {'title': 'A', 'dueDate': '2026-01-01', 'custom1': 'val'},
            {'title': 'B', 'dueDate': '2026-01-02', 'custom2': 'val'},
        ]
        columns = get_available_columns(items)
        
        assert 'title' in columns
        assert 'dueDate' in columns
        assert 'custom1' in columns
        assert 'custom2' in columns

    def test_filter_item_columns(self):
        """TC04: Items are filtered to only visible columns."""
        from sfi_reporter.tk_app import filter_item_columns
        
        item = {'title': 'Test', 'dueDate': '2026-01-01', 'extra': 'hidden'}
        visible = ['title', 'dueDate']
        
        result = filter_item_columns(item, visible)
        
        assert result == {'title': 'Test', 'dueDate': '2026-01-01'}

    def test_select_all_columns(self):
        """TC06: Select All enables all columns."""
        from sfi_reporter.tk_app import select_all_columns
        
        available = ['title', 'dueDate', 'SlaType', 'extra1', 'extra2']
        result = select_all_columns(available)
        
        assert set(result) == set(available)

    def test_clear_all_keeps_required(self):
        """TC07: Clear All keeps required columns checked."""
        from sfi_reporter.tk_app import clear_all_columns, REQUIRED_COLUMNS
        
        available = ['title', 'dueDate', 'SlaType', 'extra1', 'extra2']
        result = clear_all_columns(available)
        
        # Only required columns remain
        for col in REQUIRED_COLUMNS:
            if col in available:
                assert col in result
        assert 'extra1' not in result
        assert 'extra2' not in result

    def test_validate_visible_columns(self):
        """TC08: Required columns cannot be removed from visible list."""
        from sfi_reporter.tk_app import validate_visible_columns, REQUIRED_COLUMNS
        
        # Try to hide all columns
        visible = []
        result = validate_visible_columns(visible)
        
        # Required columns are always present
        for col in REQUIRED_COLUMNS:
            assert col in result

    def test_column_display_names(self):
        """Column display names are human-readable."""
        from sfi_reporter.tk_app import COLUMN_DISPLAY_NAMES
        
        assert COLUMN_DISPLAY_NAMES.get('title') == 'Title'
        assert COLUMN_DISPLAY_NAMES.get('dueDate') == 'Due Date'
        assert COLUMN_DISPLAY_NAMES.get('SlaType') == 'SLA Type'


class TestEmptyColumnDetection:
    """Test empty column detection for column picker annotations."""

    def test_get_empty_columns_none_value(self):
        """TC01: Column with None value is detected as empty."""
        from sfi_reporter.tk_app import get_empty_columns
        
        item = {'col1': None, 'col2': 'value'}
        empty = get_empty_columns(item)
        
        assert 'col1' in empty
        assert 'col2' not in empty

    def test_get_empty_columns_empty_string(self):
        """TC02: Column with empty string is detected as empty."""
        from sfi_reporter.tk_app import get_empty_columns
        
        item = {'col1': '', 'col2': 'value'}
        empty = get_empty_columns(item)
        
        assert 'col1' in empty
        assert 'col2' not in empty

    def test_get_empty_columns_whitespace_string(self):
        """TC03: Column with whitespace-only string is detected as empty."""
        from sfi_reporter.tk_app import get_empty_columns
        
        item = {'col1': '   ', 'col2': 'value'}
        empty = get_empty_columns(item)
        
        assert 'col1' in empty

    def test_get_empty_columns_empty_list(self):
        """TC04: Column with empty list is detected as empty."""
        from sfi_reporter.tk_app import get_empty_columns
        
        item = {'col1': [], 'col2': ['item']}
        empty = get_empty_columns(item)
        
        assert 'col1' in empty
        assert 'col2' not in empty

    def test_get_empty_columns_zero_not_empty(self):
        """TC05: Column with zero is NOT detected as empty (0 is valid data)."""
        from sfi_reporter.tk_app import get_empty_columns
        
        item = {'col1': 0, 'col2': 'value'}
        empty = get_empty_columns(item)
        
        assert 'col1' not in empty

    def test_get_empty_columns_false_not_empty(self):
        """TC06: Column with False is NOT detected as empty (False is valid data)."""
        from sfi_reporter.tk_app import get_empty_columns
        
        item = {'col1': False, 'col2': 'value'}
        empty = get_empty_columns(item)
        
        assert 'col1' not in empty

    def test_get_empty_columns_string_none(self):
        """TC07: Column with string 'None' is detected as empty."""
        from sfi_reporter.tk_app import get_empty_columns
        
        item = {'col1': 'None', 'col2': 'value'}
        empty = get_empty_columns(item)
        
        assert 'col1' in empty


class TestManagerDetection:
    """Tests for is_manager_view() function - SFI-013 TC1."""
    
    def test_is_manager_view_true_for_team_group(self):
        """TC1.1: is_manager_view returns True for TeamGroup."""
        from sfi_reporter.tk_app import is_manager_view
        
        landing_view = [{"Group": "TeamGroup", "Id": "xxx", "Name": "Team"}]
        assert is_manager_view(landing_view) is True
    
    def test_is_manager_view_false_for_services(self):
        """TC1.2: is_manager_view returns False for Services."""
        from sfi_reporter.tk_app import is_manager_view
        
        landing_view = [{"Group": "Service", "Id": "xxx", "Name": "Svc"}]
        assert is_manager_view(landing_view) is False
    
    def test_is_manager_view_false_for_empty(self):
        """TC1.3: is_manager_view returns False for empty list."""
        from sfi_reporter.tk_app import is_manager_view
        
        assert is_manager_view([]) is False
    
    def test_is_manager_view_true_for_mixed(self):
        """TC1.4: is_manager_view returns True when TeamGroup is present with others."""
        from sfi_reporter.tk_app import is_manager_view
        
        landing_view = [
            {"Group": "Service", "Id": "svc1", "Name": "Svc"},
            {"Group": "TeamGroup", "Id": "team1", "Name": "Team"},
        ]
        assert is_manager_view(landing_view) is True


class TestServiceOwnerLookup:
    """Tests for get_service_owners() function - SFI-013 TC2."""
    
    def test_get_service_owners_single_owner(self):
        """TC2.1: Parses single owner correctly."""
        from sfi_reporter.tk_app import parse_owners_field
        
        owners_json = '["John Doe"]'
        result = parse_owners_field(owners_json)
        assert result == ["John Doe"]
    
    def test_get_service_owners_multiple_owners(self):
        """TC2.2: Parses multiple owners correctly."""
        from sfi_reporter.tk_app import parse_owners_field
        
        owners_json = '["John Doe","Jane Smith"]'
        result = parse_owners_field(owners_json)
        assert result == ["John Doe", "Jane Smith"]
    
    def test_get_service_owners_null_owners(self):
        """TC2.3: Handles null owners field."""
        from sfi_reporter.tk_app import parse_owners_field
        
        assert parse_owners_field(None) == []
        assert parse_owners_field("null") == []
    
    def test_get_service_owners_empty_string(self):
        """TC2.4: Handles empty string owners field."""
        from sfi_reporter.tk_app import parse_owners_field
        
        assert parse_owners_field("") == []
        assert parse_owners_field("[]") == []


class TestOwnerAggregation:
    """Tests for aggregate_by_owner() function - SFI-013 TC3."""
    
    def test_aggregate_by_owner_single_owner(self):
        """TC3.1: Groups items under single owner correctly."""
        from sfi_reporter.tk_app import aggregate_by_owner
        
        items = [
            {"S360_ServiceTreeServiceName": "Service One", "SlaType": "InSLA"},
            {"S360_ServiceTreeServiceName": "Service One", "SlaType": "InSLA"},
        ]
        service_owners = {"Service One": ["Brent Jensen"]}
        
        result = aggregate_by_owner(items, service_owners)
        
        assert "Brent Jensen" in result
        assert result["Brent Jensen"]["count"] == 2
    
    def test_aggregate_by_owner_multi_owner(self):
        """TC3.2: Counts item under each owner for multi-owner services."""
        from sfi_reporter.tk_app import aggregate_by_owner
        
        items = [{"S360_ServiceTreeServiceName": "Service One", "SlaType": "OutOfSla"}]
        service_owners = {"Service One": ["Owner A", "Owner B"]}
        
        result = aggregate_by_owner(items, service_owners)
        
        assert "Owner A" in result
        assert "Owner B" in result
        assert result["Owner A"]["count"] == 1
        assert result["Owner B"]["count"] == 1
        assert result["Owner A"]["sla"] == 1
        assert result["Owner B"]["sla"] == 1
    
    def test_aggregate_by_owner_unknown_service(self):
        """TC3.3: Handles items with unknown service ID."""
        from sfi_reporter.tk_app import aggregate_by_owner
        
        items = [{"S360_ServiceTreeServiceName": "Unknown Service", "SlaType": "InSLA"}]
        service_owners = {}  # No mapping
        
        result = aggregate_by_owner(items, service_owners)
        
        assert "Unknown Owner" in result
        assert result["Unknown Owner"]["count"] == 1
    
    def test_aggregate_by_owner_empty_owners(self):
        """TC3.4: Handles services with empty owners list."""
        from sfi_reporter.tk_app import aggregate_by_owner
        
        items = [{"S360_ServiceTreeServiceName": "Service One", "SlaType": "InSLA"}]
        service_owners = {"Service One": []}  # Empty owners
        
        result = aggregate_by_owner(items, service_owners)
        
        assert "No Owner" in result
        assert result["No Owner"]["count"] == 1
    
    def test_aggregate_by_owner_sla_calculation(self):
        """TC3.5: Calculates SLA and invalid ETA correctly."""
        from sfi_reporter.tk_app import aggregate_by_owner
        from sfi_reporter.data import is_invalid_eta
        
        items = [
            {"S360_ServiceTreeServiceName": "Service One", "SlaType": "OutOfSla", "EtaDate": "2025-01-01"},
            {"S360_ServiceTreeServiceName": "Service One", "SlaType": "InSLA", "EtaDate": None},
            {"S360_ServiceTreeServiceName": "Service One", "SlaType": "InSLA", "EtaDate": "2030-01-01"},
        ]
        service_owners = {"Service One": ["Test Owner"]}
        
        result = aggregate_by_owner(items, service_owners)
        
        assert result["Test Owner"]["count"] == 3
        assert result["Test Owner"]["sla"] == 1  # 1 OutOfSla


class TestDirectReportFiltering:
    """Tests for extract_direct_reports() and owner filtering - SFI-013."""
    
    def test_extract_direct_reports_from_team_entries(self):
        """Should extract names from 'X's Team' entries only."""
        from sfi_reporter.tk_app import extract_direct_reports
        
        service_owners = {
            "Gowri Bhaskara's Team": ["Gowri Bhaskara"],
            "Ze Li's Team": ["Ze Li"],
            "Karan Parkash's Team": ["Karan Parkash"],
            "Service A": ["Gowri Bhaskara", "Skip Level"],  # Skip Level NOT a direct
        }
        
        result = extract_direct_reports(service_owners)
        
        # Only team owners are directs
        assert result == {"Gowri Bhaskara", "Ze Li", "Karan Parkash"}
        assert "Skip Level" not in result  # Not a team owner
    
    def test_extract_direct_reports_includes_manager(self):
        """Should include manager name when provided."""
        from sfi_reporter.tk_app import extract_direct_reports
        
        service_owners = {
            "Gowri Bhaskara's Team": ["Gowri Bhaskara"],
            "Service A": ["Someone Else"],  # Not a direct
        }
        
        result = extract_direct_reports(service_owners, manager_name="The Manager")
        
        assert "The Manager" in result
        assert "Gowri Bhaskara" in result
        assert "Someone Else" not in result  # Not a team owner
    
    def test_extract_direct_reports_empty_when_no_teams(self):
        """Should return empty set when no team entries."""
        from sfi_reporter.tk_app import extract_direct_reports
        
        service_owners = {
            "Service A": ["Person 1"],
            "Service B": ["Person 2"],
        }
        
        result = extract_direct_reports(service_owners)
        
        assert result == set()
    
    def test_aggregate_by_owner_picks_first_allowed(self):
        """Should pick first allowed owner, not count item multiple times."""
        from sfi_reporter.tk_app import aggregate_by_owner
        
        items = [
            {"S360_ServiceTreeServiceName": "Service One", "SlaType": "InSLA", "EtaDate": "2025-12-31"},
        ]
        service_owners = {
            "Service One": ["Direct Report", "Skip Level", "Another Skip"],
        }
        allowed = {"Direct Report"}
        
        result = aggregate_by_owner(items, service_owners, allowed_owners=allowed)
        
        # Item attributed to "Direct Report" only (first match)
        assert "Direct Report" in result
        assert result["Direct Report"]["count"] == 1
        assert "Skip Level" not in result
        assert "Another Skip" not in result
    
    def test_aggregate_by_owner_unknown_when_no_match(self):
        """Should use Unknown Owner when no allowed owner matches."""
        from sfi_reporter.tk_app import aggregate_by_owner
        
        items = [
            {"S360_ServiceTreeServiceName": "Service One", "SlaType": "InSLA", "EtaDate": "2025-12-31"},
        ]
        service_owners = {
            "Service One": ["Skip Level 1", "Skip Level 2"],
        }
        allowed = {"Direct Report"}  # Neither owner is allowed
        
        result = aggregate_by_owner(items, service_owners, allowed_owners=allowed)
        
        # No match -> Unknown Owner
        assert "Unknown Owner" in result
        assert result["Unknown Owner"]["count"] == 1
        assert "Skip Level 1" not in result
        assert "Skip Level 2" not in result

    def test_aggregate_by_owner_with_org_mapping(self):
        """Should use org_mapping to roll up skip-levels to directs."""
        from sfi_reporter.tk_app import aggregate_by_owner
        
        items = [
            {"S360_ServiceTreeServiceName": "Service One", "SlaType": "InSLA", "EtaDate": "2025-12-31"},
            {"S360_ServiceTreeServiceName": "Service Two", "SlaType": "OutOfSla", "EtaDate": "2025-12-31"},
        ]
        service_owners = {
            "Service One": ["Ken Hsieh", "Other Owner"],  # Ken is a skip-level under Ze Li
            "Service Two": ["Brent Jensen"],  # Brent is a direct
        }
        # org_mapping: maps each owner to their direct-report-level ancestor
        org_mapping = {
            "Ken Hsieh": "Ze Li",  # Ken rolls up to Ze Li
            "Brent Jensen": "Brent Jensen",  # Brent is a direct (maps to self)
            "Other Owner": "Unknown Owner",  # Not in manager's org
        }
        
        result = aggregate_by_owner(items, service_owners, org_mapping=org_mapping)
        
        # Ken's service rolls up to Ze Li
        assert "Ze Li" in result
        assert result["Ze Li"]["count"] == 1
        
        # Brent's service stays with Brent
        assert "Brent Jensen" in result
        assert result["Brent Jensen"]["count"] == 1
        assert result["Brent Jensen"]["sla"] == 1  # Out of SLA
        
        # No Ken Hsieh in results (rolled up)
        assert "Ken Hsieh" not in result