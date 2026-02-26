# SFI-039 — Test Cases

This document defines every test case the developer must implement. Each test maps to an acceptance criterion (AC) and specifies the function under test, setup, expected outcome, and mocking requirements.

**Convention**: Test IDs use the pattern `TC-<file-abbrev>-<seq>`. File abbreviations:
- **LC** = `logging_config.py`
- **KA** = `kpi_analyzer.py`
- **QB** = `query_builder.py`
- **CT** = `copilot_tools.py`
- **CP** = `copilot_panel.py`
- **DG** = `dialogs.py`
- **AP** = `app.py`

---

## Shared Fixtures (conftest additions)

The developer should add these to `SFIReporter/tests/conftest.py` or a local conftest:

```python
import sys
from unittest.mock import MagicMock

# Inject mock copilot module before any copilot_tools / copilot_panel import
_mock_copilot = MagicMock()
_mock_copilot.Tool = MagicMock
_mock_copilot.ToolResult = MagicMock
_mock_copilot.define_tool = MagicMock()
sys.modules.setdefault("copilot", _mock_copilot)

@pytest.fixture(scope="module")
def tk_root():
    """Shared Tk root for GUI tests — one per module, destroyed at end."""
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # headless
    yield root
    root.destroy()

@pytest.fixture
def mock_app(tk_root):
    """Minimal SFIReporterApp mock with required attributes."""
    app = MagicMock()
    app.root = tk_root
    app.current_data = {}
    app._unfiltered_data = {}
    return app
```

---

## Phase 1 — Quick Wins

### File: `test_logging_config.py` → AC: `logging_config.py ≥ 70%`

| ID | Test Name | Function Under Test | Setup / Mocks | Expected Outcome |
|----|-----------|---------------------|---------------|------------------|
| TC-LC-01 | `test_setup_logging_creates_handlers` | `setup_logging()` | Clear `sfi_reporter` logger handlers before test. Mock `LOG_DIR.mkdir`. | Logger has exactly 2 handlers (file + console). Root level is DEBUG. |
| TC-LC-02 | `test_setup_logging_idempotent` | `setup_logging()` | Call `setup_logging()` twice. | Still exactly 2 handlers after second call. |
| TC-LC-03 | `test_setup_logging_custom_level` | `setup_logging(level=logging.WARNING)` | Clear handlers first. | `root.level == logging.WARNING`. |
| TC-LC-04 | `test_get_log_path_returns_expected` | `get_log_path()` | None. | Returns `Path` ending in `sfireporter/sfi_reporter.log`. |
| TC-LC-05 | `test_patch_subprocess_windows_on_win32` | `patch_subprocess_windows()` | `mocker.patch("sfi_reporter.logging_config.sys.platform", "win32")`. Reset `_sfi_patched` flag first. | `subprocess.Popen.__init__` has `_sfi_patched == True`. |
| TC-LC-06 | `test_patch_subprocess_windows_noop_on_linux` | `patch_subprocess_windows()` | `mocker.patch("sfi_reporter.logging_config.sys.platform", "linux")`. | `subprocess.Popen.__init__` is unchanged. |
| TC-LC-07 | `test_patch_subprocess_windows_idempotent` | `patch_subprocess_windows()` | Call twice on win32. | `_sfi_patched` still True; only patched once. |
| TC-LC-08 | `test_patched_popen_adds_creation_flags` | `_patched_popen_init` (direct call) | `mocker.patch("sfi_reporter.logging_config.sys.platform", "win32")`. Create mock self, call `_patched_popen_init(self, "echo", "hi")`. | `kwargs["creationflags"]` includes `CREATE_NO_WINDOW`. |

---

### File: `test_kpi_analyzer_extended.py` → AC: `kpi_analyzer.py ≥ 70%`

| ID | Test Name | Function Under Test | Setup / Mocks | Expected Outcome |
|----|-----------|---------------------|---------------|------------------|
| TC-KA-01 | `test_is_js_shell_empty_string` | `_is_js_shell("")` | None. | Returns `False`. |
| TC-KA-02 | `test_is_js_shell_short_with_indicator` | `_is_js_shell("Loading...")` | None. | Returns `True`. |
| TC-KA-03 | `test_is_js_shell_short_few_words` | `_is_js_shell("hello world")` | None. | Returns `True` (< 50 words). |
| TC-KA-04 | `test_is_js_shell_long_text_false` | `_is_js_shell("x " * 300)` | None. | Returns `False` (≥ 400 chars). |
| TC-KA-05 | `test_is_login_page_empty` | `_is_login_page("")` | None. | Returns `False`. |
| TC-KA-06 | `test_is_login_page_sign_in_short` | `_is_login_page("Sign in to your account ...")` | Text with < 30 unique words, < 80 words total. | Returns `True`. |
| TC-KA-07 | `test_is_login_page_real_content` | `_is_login_page(long_unique_text)` | 200+ unique words, contains "sign in" once. | Returns `False` (enough unique words). |
| TC-KA-08 | `test_extract_text_strips_scripts` | `extract_text("<script>var x=1;</script><p>Hello</p>")` | None. | Returns `"Hello"`. |
| TC-KA-09 | `test_extract_text_strips_styles` | `extract_text("<style>.x{}</style><div>World</div>")` | None. | Returns `"World"`. |
| TC-KA-10 | `test_truncate_content_no_truncation` | `truncate_content("short", 100)` | None. | Returns `"short"` (unchanged). |
| TC-KA-11 | `test_truncate_content_truncates` | `truncate_content("x" * 200, 100)` | None. | Returns 100 chars + `"\n... (truncated)"`. |
| TC-KA-12 | `test_collect_urls_extracts_from_fields` | `collect_urls([{"url": "https://a.com", "ActionWikiLink": "https://b.com"}])` | None. | Returns `{"https://a.com", "https://b.com"}`. |
| TC-KA-13 | `test_collect_urls_skips_non_http` | `collect_urls([{"url": "ftp://bad.com"}])` | None. | Returns empty set. |
| TC-KA-14 | `test_sanitize_text_removes_control_chars` | `_sanitize_text("hello\x00world\n\n\n\nend")` | None. | Returns `"helloworld\n\nend"`. |
| TC-KA-15 | `test_safe_filename_produces_valid_name` | `_safe_filename("https://lens.msftcloudes.com/dash?id=123")` | None. | Returns string matching `r'^[\w_]+\.txt$'`. |
| TC-KA-16 | `test_analysis_result_str` | `str(AnalysisResult(prompt="hello"))` | None. | Returns `"hello"`. |
| TC-KA-17 | `test_fetch_url_content_cdp_success` | `fetch_url_content("https://example.com")` | Mock `_fetch_via_cdp` returning content. | Returns CDP result with content. |
| TC-KA-18 | `test_fetch_url_content_auth_redirect_bearer_success` | `fetch_url_content(url)` | `_fetch_via_cdp` returns `{"error": "auth_redirect"}`, `_fetch_with_bearer_token` returns content. | Returns bearer result. |
| TC-KA-19 | `test_fetch_url_content_all_auth_fail` | `fetch_url_content(url)` | CDP returns auth_redirect, bearer returns empty, Edge CDP returns empty. | Returns error `"auth_redirect"`. |
| TC-KA-20 | `test_fetch_url_content_fallback_urllib` | `fetch_url_content(url)` | CDP returns empty (no error), urllib returns content. | Returns urllib result. |
| TC-KA-21 | `test_format_sources_card_no_auth` | `format_sources_card(result)` | `AnalysisResult` with 2 `FetchResult` items, all `ok=True`. | String does NOT contain auth hint. |
| TC-KA-22 | `test_format_sources_card_with_auth` | `format_sources_card(result)` | One `FetchResult` has `error="auth_redirect"`. | String contains auth hint emoji. |

---

## Phase 2 — Logic Modules

### File: `test_query_builder_extended.py` → AC: `query_builder.py ≥ 70%`

| ID | Test Name | Function Under Test | Setup / Mocks | Expected Outcome |
|----|-----------|---------------------|---------------|------------------|
| TC-QB-01 | `test_match_string_clause_list_equals` | `_match_string_clause(["a","b"], "equals", "a")` | None. | Returns `True`. |
| TC-QB-02 | `test_match_string_clause_list_not_contains` | `_match_string_clause(["abc"], "not contains", "xyz")` | None. | Returns `True`. |
| TC-QB-03 | `test_match_date_clause_on_or_before` | `_match_date_clause("2026-01-15T00:00:00Z", "on or before", "2026-02-01")` | None. | Returns `True`. |
| TC-QB-04 | `test_match_date_clause_on_or_after` | `_match_date_clause("2026-03-01T00:00:00Z", "on or after", "2026-02-01")` | None. | Returns `True`. |
| TC-QB-05 | `test_match_date_clause_none_value` | `_match_date_clause(None, "equals", "2026-01-01")` | None. | Returns `False`. |
| TC-QB-06 | `test_evaluate_clauses_or_connector` | `evaluate_clauses(items, [clause_where, clause_or])` | Two clauses: Where (field=title, contains "Fix"), Or (field=title, contains "Update"). | Returns items matching either clause. |
| TC-QB-07 | `test_evaluate_clauses_exclude_ussec` | `evaluate_clauses(items, clauses, include_ussec=False)` | Items include one with "USSec" in title. | USSec item excluded. |
| TC-QB-08 | `test_aggregate_results_by_program` | `aggregate_results_by_program(items, programs_lookup)` | Items with `S360_ProgramIds`. | Returns dict keyed by program name with correct counts. |
| TC-QB-09 | `test_save_and_load_clause_cache` | `save_clause_cache` / `load_clause_cache` | `tmp_path` fixture. Save 2 clauses, load them back. | Loaded clauses match saved clauses exactly. |
| TC-QB-10 | `test_clear_clause_cache` | `clear_clause_cache(cache_dir)` | `tmp_path` with a cache file. | Cache file is deleted. |
| TC-QB-11 | `test_load_clause_cache_missing_file` | `load_clause_cache(cache_dir)` | `tmp_path` with no cache file. | Returns `([], True)` (empty list, default ussec flag). |
| TC-QB-12 | `test_clause_row_init_creates_widgets` | `ClauseRow.__init__` | `tk_root` fixture. Create a `ClauseRow` in a Frame. | Instance has `field_combo`, `op_combo`, `value_entry` attributes. |
| TC-QB-13 | `test_clause_row_get_clause` | `ClauseRow.get_clause()` | Set combobox values programmatically. | Returns `QueryClause` with matching field/operator/value. |
| TC-QB-14 | `test_clause_row_set_clause` | `ClauseRow.set_clause(clause)` | Pass a `QueryClause`. | Combobox values match the clause. |
| TC-QB-15 | `test_query_builder_init_builds_ui` | `QueryBuilder.__init__` | `tk_root` fixture. Mock `app.current_data` with sample items. | Instance has `_clause_rows` list with ≥ 1 entry. |
| TC-QB-16 | `test_query_builder_enrich_items` | `QueryBuilder._enrich_items()` | Items with `S360_ProgramIds`, `programs_lookup` provided. | Items get `_resolved_program` key. |

---

### File: `test_copilot_tools.py` → AC: `copilot_tools.py ≥ 70%`

**Note**: All tests require `sys.modules["copilot"]` mock in conftest (see shared fixtures).

| ID | Test Name | Function Under Test | Setup / Mocks | Expected Outcome |
|----|-----------|---------------------|---------------|------------------|
| TC-CT-01 | `test_get_items_returns_detailed` | `_get_items(app)` | `app.current_data = {"detailed_items": [{"id": "1"}]}`. | Returns `[{"id": "1"}]`. |
| TC-CT-02 | `test_get_items_empty_data` | `_get_items(app)` | `app.current_data = {}`. | Returns `[]`. |
| TC-CT-03 | `test_summarise_item_extracts_fields` | `_summarise_item(item)` | Full item dict with all fields. | Returned dict has exactly 10 keys: id, title, service, sla_type, eta_date, due_date, owner, assigned_to, status, kpi. |
| TC-CT-04 | `test_summarise_item_missing_fields` | `_summarise_item({})` | Empty dict. | All values are `""`. |
| TC-CT-05 | `test_truncate_short_text` | `_truncate("short")` | None. | Returns `"short"` unchanged. |
| TC-CT-06 | `test_truncate_long_text` | `_truncate("x" * 10000)` | None. | Length ≤ `_MAX_RESULT_LEN + 20`. Ends with `"(truncated)"`. |
| TC-CT-07 | `test_build_get_summary_no_data` | `_build_get_summary(app)` handler | `app.current_data = {}`. | Handler returns string containing "No data loaded". |
| TC-CT-08 | `test_build_get_summary_with_data` | `_build_get_summary(app)` handler | `app.current_data` with items, service_stats, program_stats. Mock `sfi_reporter.data.is_invalid_eta`. | Returns JSON with `total_items`, `out_of_sla`, `services`, `programs`. |
| TC-CT-09 | `test_build_search_items_no_data` | `_build_search_items(app)` handler | `app.current_data = {"detailed_items": []}`. | Returns `"No data loaded."`. |
| TC-CT-10 | `test_build_search_items_text_match` | `_build_search_items(app)` handler | 3 items, query = "Fix". | Returns JSON with count = 1 (only matching item). |
| TC-CT-11 | `test_build_search_items_sla_filter` | `_build_search_items(app)` handler | 3 items, sla_filter = "OutOfSla". | Returns only OutOfSla items. |
| TC-CT-12 | `test_build_search_items_limit` | `_build_search_items(app)` handler | 10 items, limit = 3. | Returns JSON with count = 3. |
| TC-CT-13 | `test_build_get_item_detail_found` | `_build_get_item_detail(app)` handler | Item with `id="ABC"` in data. | Returns JSON with item fields (no `_` prefixed keys). |
| TC-CT-14 | `test_build_get_item_detail_not_found` | `_build_get_item_detail(app)` handler | No matching item. | Returns `"Item 'XYZ' not found."`. |
| TC-CT-15 | `test_build_list_services_with_data` | `_build_list_services(app)` handler | `service_stats` with 2 services. | Returns JSON list sorted by total desc. |
| TC-CT-16 | `test_build_list_services_no_data` | `_build_list_services(app)` handler | `service_stats = {}`. | Returns `"No service data loaded."`. |
| TC-CT-17 | `test_build_items_for_service_match` | `_build_items_for_service(app)` handler | Items with various services, query = "svc-a". | Returns only matching items. |
| TC-CT-18 | `test_build_update_eta_item_not_found` | `_build_update_eta(app)` handler | Empty items list. | Returns `"Item '...' not found"`. |
| TC-CT-19 | `test_build_web_fetch_empty_url` | `_build_web_fetch()` handler | `args = {"url": ""}`. | Returns `"Error: 'url' parameter is required."`. |
| TC-CT-20 | `test_build_web_fetch_non_http` | `_build_web_fetch()` handler | `args = {"url": "ftp://bad.com"}`. | Returns error about http/https only. |
| TC-CT-21 | `test_build_read_fetched_doc_no_dir` | `_build_read_fetched_doc()` handler | `_current_docs_dir = ""`. | Returns `"Error: No docs directory is set."`. |
| TC-CT-22 | `test_build_read_fetched_doc_path_traversal` | `_build_read_fetched_doc()` handler | `filename = "../etc/passwd"`. Set `_current_docs_dir`. | Returns error about plain filename. |
| TC-CT-23 | `test_build_read_fetched_doc_success` | `_build_read_fetched_doc()` handler | Create a temp file in `_current_docs_dir`. | Returns file content. |
| TC-CT-24 | `test_set_current_docs_dir` | `set_current_docs_dir("/tmp/test")` | None. | `_current_docs_dir` module variable is set. |
| TC-CT-25 | `test_build_tools_returns_8_tools` | `build_tools(app)` | Mock app. | Returns list of length 8. |
| TC-CT-26 | `test_make_tool_async_handler_success` | `_make_tool` async handler | Create tool, run handler via `asyncio.run`. | Returns `ToolResult` with text. |
| TC-CT-27 | `test_make_tool_async_handler_exception` | `_make_tool` async handler | Handler raises `ValueError`. | Returns `ToolResult` with `"Tool error:"` in text. |

---

## Phase 3 — GUI-Heavy Modules

### File: `test_copilot_panel.py` → AC: `copilot_panel.py ≥ 70%`

**Note**: Requires `sys.modules["copilot"]` mock and `tk_root` fixture.

| ID | Test Name | Function Under Test | Setup / Mocks | Expected Outcome |
|----|-----------|---------------------|---------------|------------------|
| TC-CP-01 | `test_async_bridge_start_creates_loop` | `AsyncBridge.start()` | None. | `bridge.loop` is not None; `bridge._thread.is_alive()`. |
| TC-CP-02 | `test_async_bridge_stop` | `AsyncBridge.stop()` | Start first, then stop. | `bridge.loop.is_running()` is False after stop. |
| TC-CP-03 | `test_async_bridge_run_coroutine` | `AsyncBridge.run_coroutine(coro)` | Start bridge, submit `async def dummy(): return 42`. | Future result is `42`. |
| TC-CP-04 | `test_copilot_panel_init` | `CopilotPanel.__init__` | `tk_root`, mock `app`, mock `on_close`. Patch `copilot` SDK. | Panel created without error; has `_chat_display` attribute. |
| TC-CP-05 | `test_copilot_panel_build_ui_widgets` | `CopilotPanel._build_ui` | Same as above. | Panel has `_input_box`, `_send_btn`, `_stop_btn`, `_status_label`. |
| TC-CP-06 | `test_append_message_user` | `panel._append_message("user", "Hello")` | Created panel. | Chat display contains "You:" and "Hello". |
| TC-CP-07 | `test_append_message_assistant` | `panel._append_message("assistant", "Hi there")` | Created panel. | Chat display contains "Copilot:" and "Hi there". |
| TC-CP-08 | `test_append_delta` | `panel._append_delta("chunk1")` | Created panel, start an assistant message first. | Chat display contains "chunk1". |
| TC-CP-09 | `test_finish_assistant_message` | `panel._finish_assistant_message()` | Created panel, append some deltas. | `_partial_response` is reset to `""`. |
| TC-CP-10 | `test_render_markdown_heading` | `panel._render_markdown("# Title\nBody text")` | Created panel. | Chat display contains "Title" with heading tag. |
| TC-CP-11 | `test_render_markdown_bullets` | `panel._render_markdown("- item one\n- item two")` | Created panel. | Chat display contains bullet markers and both items. |
| TC-CP-12 | `test_render_markdown_code_block` | `panel._render_markdown("```\ncode\n```")` | Created panel. | Chat display contains "code" with code formatting tag. |
| TC-CP-13 | `test_insert_inline_md_bold` | `panel._insert_inline_md("**bold text**", "body")` | Created panel. | Chat display contains "bold text". |
| TC-CP-14 | `test_set_status` | `panel._set_status("Ready", "green")` | Created panel. | Status label text is "Ready". |
| TC-CP-15 | `test_set_input_enabled_false` | `panel._set_input_enabled(False)` | Created panel. | Input box state is `"disabled"`. Send button state is `"disabled"`. |
| TC-CP-16 | `test_set_input_enabled_true` | `panel._set_input_enabled(True)` | Created panel, disable first. | Input box state is `"normal"`. |
| TC-CP-17 | `test_on_stop_sets_cancelled` | `panel._on_stop()` | Created panel, set `_cancel_event`. | `_cancel_event.is_set()` is True. |
| TC-CP-18 | `test_on_link_click_opens_browser` | `panel._on_link_click("https://example.com")` | Mock `webbrowser.open`. | `webbrowser.open` called with URL. |
| TC-CP-19 | `test_destroy_stops_bridge` | `panel.destroy()` | Created panel with started bridge. | `_async_bridge.stop()` called. |

---

### File: `test_dialogs_extended.py` → AC: `dialogs.py ≥ 70%`

| ID | Test Name | Function Under Test | Setup / Mocks | Expected Outcome |
|----|-----------|---------------------|---------------|------------------|
| TC-DG-01 | `test_sortable_treeview_ascending` | `SortableTreeview._sort_by_column` | `tk_root`. Insert rows ["B", "A", "C"]. Click sort on col. | First row is "A". |
| TC-DG-02 | `test_sortable_treeview_descending_toggle` | `SortableTreeview._sort_by_column` (twice) | Same as above. Sort col twice. | First row is "C". |
| TC-DG-03 | `test_sortable_treeview_multi_column` | `SortableTreeview.sort_by_columns` | 4 rows with 2 columns. Sort by col1 asc, col2 desc. | Rows ordered by col1 asc, then col2 desc within ties. |
| TC-DG-04 | `test_column_selector_init` | `ColumnSelectorDialog.__init__` | `tk_root`, columns = ["A","B","C"], initially_visible=["A"]. | Dialog created. Checkbox for "A" is selected. |
| TC-DG-05 | `test_column_selector_select_all` | `ColumnSelectorDialog._select_all` | Created dialog. | All checkboxes have `.get() == 1`. |
| TC-DG-06 | `test_column_selector_clear_all` | `ColumnSelectorDialog._clear_all` | Created dialog, select all first. | All checkboxes have `.get() == 0`. |
| TC-DG-07 | `test_column_selector_apply_callback` | `ColumnSelectorDialog._apply` | `on_apply` mock callback. Select 2 columns. | `on_apply` called with list of 2 column names. |
| TC-DG-08 | `test_column_selector_class_methods` | `get_visible_columns` / `reset_visible_columns` | Set visible via `_apply`, read via class method. | `get_visible_columns` returns the selected list. After reset, returns `None`. |
| TC-DG-09 | `test_detail_modal_init` | `DetailModal.__init__` | `tk_root`, title="Test", items = [sample_item]. | Modal created with tree widget containing 1 row. |
| TC-DG-10 | `test_detail_modal_populate_rows` | `DetailModal._populate_rows` | Created modal, call with 3 items. | Tree has 3 children. |
| TC-DG-11 | `test_detail_modal_on_item_double_click` | `DetailModal._on_item_double_click` | Select a row, simulate double-click. Mock `ItemDetailsModal`. | `ItemDetailsModal` instantiated with the item dict. |
| TC-DG-12 | `test_item_details_modal_init` | `ItemDetailsModal.__init__` | `tk_root`, sample item dict with various fields. | Modal created. Text widget contains field labels. |
| TC-DG-13 | `test_item_details_modal_build_content` | `ItemDetailsModal._build_content` | Item with url, ResourceUris, regular fields. | Text widget contains URL link tags and field values. |
| TC-DG-14 | `test_item_details_modal_insert_text_with_links` | `ItemDetailsModal._insert_text_with_links` | Text containing `https://example.com`. | Text widget has link tag at URL position. |
| TC-DG-15 | `test_item_details_modal_insert_resource_uris` | `ItemDetailsModal._insert_resource_uris` | JSON-encoded list of resource URIs. | Text widget contains parsed URI text. |
| TC-DG-16 | `test_single_eta_edit_dialog_init` | `SingleEtaEditDialog.__init__` | `tk_root`, sample item, `on_saved` callback mock. | Dialog has date entry and notes text widget. |
| TC-DG-17 | `test_single_eta_edit_dialog_save_valid` | `SingleEtaEditDialog._on_save` | Set date to valid future date. Mock `validate_eta_date` → `(True, "")`. Mock API. | `on_saved` callback invoked. |
| TC-DG-18 | `test_single_eta_edit_dialog_save_invalid_date` | `SingleEtaEditDialog._on_save` | Set date to "invalid". Mock `validate_eta_date` → `(False, "bad date")`. | Error message shown via `messagebox`. |
| TC-DG-19 | `test_eta_mode_dialog_choose` | `EtaModeDialog._choose("bulk")` | `tk_root`, `on_choice` mock. | `on_choice` called with `"bulk"`. |
| TC-DG-20 | `test_manual_eta_review_show_current` | `ManualEtaReviewDialog._show_current` | 3 items. | UI fields show data for current item (index 0). |
| TC-DG-21 | `test_manual_eta_review_skip` | `ManualEtaReviewDialog._skip` | Start at index 0 of 3. | Current index advances to 1. |
| TC-DG-22 | `test_manual_eta_review_cancel` | `ManualEtaReviewDialog._cancel` | Start review. | Dialog destroyed. `on_complete` called with results so far. |
| TC-DG-23 | `test_bulk_eta_progress_dialog_init` | `BulkEtaProgressDialog.__init__` | `tk_root`, 3 items, `on_complete` mock. | Dialog has progress bar. |
| TC-DG-24 | `test_launch_llm_analysis_function` | `_launch_llm_analysis` | Mock `app` with copilot panel. Mock `analyze_kpi`. | `copilot_panel.send_analysis_prompt` called. |

---

### File: `test_app_coverage.py` → AC: `app.py ≥ 70%`

**Note**: All tests use a heavily-mocked `SFIReporterApp` created via `tk_root` fixture with all external dependencies patched.

| ID | Test Name | Function Under Test | Setup / Mocks | Expected Outcome |
|----|-----------|---------------------|---------------|------------------|
| TC-AP-01 | `test_app_init_creates_instance` | `SFIReporterApp.__init__` | `tk_root`. Patch `get_current_user_alias`, `is_cache_valid`, `read_cache`. | Instance created. `current_data` is dict. |
| TC-AP-02 | `test_app_build_ui_creates_tables` | `SFIReporterApp._build_ui` | Via init. | App has `service_tree`, `program_tree`, `action_tree`. |
| TC-AP-03 | `test_app_build_ui_creates_buttons` | `SFIReporterApp._build_ui` | Via init. | App has `refresh_btn`, `clear_btn`, `retry_btn`. |
| TC-AP-04 | `test_load_cached_data_valid_cache` | `_load_cached_data` | `is_cache_valid` → True. `read_cache` → sample data dict. | `current_data` populated. Tables have rows. |
| TC-AP-05 | `test_load_cached_data_no_cache` | `_load_cached_data` | `is_cache_valid` → False. | `current_data` remains empty. Status says "No cached data". |
| TC-AP-06 | `test_update_tables_empty_data` | `_update_tables({})` | Created app. | All trees have 0 children. |
| TC-AP-07 | `test_update_tables_with_services` | `_update_tables(data_with_services)` | Data dict with `service_stats` (2 services). | Service tree has 2 rows. |
| TC-AP-08 | `test_update_tables_with_programs` | `_update_tables(data_with_programs)` | Data dict with `program_stats`. | Program tree has rows matching programs. |
| TC-AP-09 | `test_update_tables_with_actions` | `_update_tables(data_with_actions)` | Data dict with `detailed_items`. | Action tree has rows matching items. |
| TC-AP-10 | `test_update_tables_filtered_mode` | `_update_tables(data, is_filtered=True)` | Filtered data. | Status shows "filtered" text. |
| TC-AP-11 | `test_on_refresh_disables_button` | `_on_refresh` | Patch `threading.Thread`. | `refresh_btn` state is `"disabled"`. |
| TC-AP-12 | `test_on_refresh_complete_success` | `_on_refresh_complete(data)` | Non-None data dict. | `current_data` updated. Refresh button re-enabled. |
| TC-AP-13 | `test_on_refresh_complete_failure` | `_on_refresh_complete(None)` | None data. | Status shows error message. Refresh button re-enabled. |
| TC-AP-14 | `test_on_clear_cache` | `_on_clear_cache` | Mock `clear_cache`, `messagebox.askyesno` → True. | `clear_cache` called. Tables cleared. |
| TC-AP-15 | `test_on_clear_cache_cancelled` | `_on_clear_cache` | `messagebox.askyesno` → False. | `clear_cache` NOT called. |
| TC-AP-16 | `test_on_query_launches_builder` | `_on_query` | Mock `QueryBuilder`. | `QueryBuilder` instantiated with correct args. |
| TC-AP-17 | `test_on_filter_applied` | `_on_filter_applied(filtered_items, clauses)` | 5 filtered items, 2 clauses. | `_update_tables` called. `_last_filter_clauses` saved. |
| TC-AP-18 | `test_on_service_double_click` | `_on_service_double_click(event)` | Select a service row. Mock `DetailModal`. | `DetailModal` instantiated with items for that service. |
| TC-AP-19 | `test_on_program_double_click` | `_on_program_double_click(event)` | Select a program row. Mock `DetailModal`. | `DetailModal` called with program's items. |
| TC-AP-20 | `test_on_action_double_click` | `_on_action_double_click(event)` | Select an action row. Mock `ItemDetailsModal`. | `ItemDetailsModal` called with item dict. |
| TC-AP-21 | `test_on_kpi_right_click` | `_on_kpi_right_click(event)` | Right-click on KPI row. Mock `_launch_llm_analysis`. | Context menu posted or analysis launched. |
| TC-AP-22 | `test_toggle_copilot_panel_show` | `_toggle_copilot_panel` | Panel not shown. Mock `CopilotPanel`. | `CopilotPanel` created and added to container. |
| TC-AP-23 | `test_toggle_copilot_panel_hide` | `_toggle_copilot_panel` | Panel already shown. | Panel removed from container. |
| TC-AP-24 | `test_on_update_etas` | `_on_update_etas` | Items with invalid ETAs. Mock `EtaModeDialog`. | `EtaModeDialog` instantiated. |
| TC-AP-25 | `test_on_eta_update_complete` | `_on_eta_update_complete(saved=2, skipped=1, failed=0)` | Mock messagebox. | Messagebox shown with "2 saved, 1 skipped". |
| TC-AP-26 | `test_on_retry_failed` | `_on_retry_failed` | `current_data` has `failed_kpis`. Patch thread. | Thread started for retry. |
| TC-AP-27 | `test_on_retry_complete` | `_on_retry_complete(new_rows, still_failed, alias)` | 3 new rows, 1 still failed. | `current_data["detailed_items"]` extended. `failed_kpis` updated. |
| TC-AP-28 | `test_update_status` | `_update_status("Loading...", "blue")` | Created app. | Status label text is "Loading...". |
| TC-AP-29 | `test_main_function` | `main()` | Mock `tk.Tk`, `SFIReporterApp`, `root.mainloop`. | `SFIReporterApp` instantiated. `mainloop` called. |
| TC-AP-30 | `test_reapply_last_filter` | `_reapply_last_filter` | Set `_last_filter_clauses` to 2 clauses. | `evaluate_clauses` called with saved clauses. |
| TC-AP-31 | `test_on_alias_change` | `_on_alias_change` | Change `alias_var` value. | `_load_cached_data` triggered. |
| TC-AP-32 | `test_hide_copilot_panel` | `_hide_copilot_panel` | Panel shown. | Panel destroyed and reference cleared. |

---

## Traceability Matrix

| Acceptance Criterion | Test Cases | Total |
|---------------------|------------|:-----:|
| `logging_config.py` ≥ 70% | TC-LC-01 through TC-LC-08 | 8 |
| `kpi_analyzer.py` ≥ 70% | TC-KA-01 through TC-KA-22 | 22 |
| `query_builder.py` ≥ 70% | TC-QB-01 through TC-QB-16 | 16 |
| `copilot_tools.py` ≥ 70% | TC-CT-01 through TC-CT-27 | 27 |
| `copilot_panel.py` ≥ 70% | TC-CP-01 through TC-CP-19 | 19 |
| `dialogs.py` ≥ 70% | TC-DG-01 through TC-DG-24 | 24 |
| `app.py` ≥ 70% | TC-AP-01 through TC-AP-32 | 32 |
| **Total** | | **148** |

---

## Coverage Estimation

Each test case covers roughly 3–8 statements on average. With 148 test cases:
- **logging_config.py** (42 stmts): 8 tests × ~5 stmts = ~40 stmts → **~95%**
- **kpi_analyzer.py** (523 stmts): 22 tests × ~5 stmts + existing 59% = ~110 + 309 = ~419 stmts → **~80%**
- **query_builder.py** (430 stmts): 16 tests × ~8 stmts + existing 40% = ~128 + 172 = ~300 stmts → **~70%**
- **copilot_tools.py** (202 stmts): 27 tests × ~5 stmts = ~135 stmts → **~67%** ← may need 2-3 extra tests at dev time
- **copilot_panel.py** (392 stmts): 19 tests × ~8 stmts + existing 34% = ~152 + 133 = ~285 stmts → **~73%**
- **dialogs.py** (790 stmts): 24 tests × ~8 stmts + existing 14% = ~192 + 111 = ~303 stmts → **~38%** ← needs expansion at dev time (see note)
- **app.py** (681 stmts): 32 tests × ~8 stmts = ~256 stmts → **~38%** ← needs expansion at dev time (see note)

### Important Note for Developer

For `dialogs.py` (790 stmts) and `app.py` (681 stmts), the test case list above covers the **most critical paths**. The developer should add additional tests during implementation to hit 70%. Specifically:
- **`dialogs.py`**: Add tests for `_build_tree` row population with color-coded ETAs, `_on_item_right_click` context menu, `BulkEtaProgressDialog._start` progress loop, `ManualEtaReviewDialog._accept` save flow, `ManualEtaReviewDialog._show_summary`.
- **`app.py`**: Add tests for `_build_ui` complete widget creation (service/program/action tree column setup), `_refresh_tables_after_eta_update`, `_on_alias_change` debounce, each double-click handler with edge cases (no selection, empty data).

The test cases above provide a concrete starting framework; the developer should use `pytest --cov=sfi_reporter --cov-report=term-missing` iteratively to identify remaining uncovered lines and add targeted tests.
