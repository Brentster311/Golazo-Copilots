# SFI-036 — Remove tk_app.py monolith and consolidate on app.py

**Status**: IMPLEMENTED

## User Story

- **Title**: Remove dead monolith `tk_app.py` and retarget all imports to decomposed modules
- **As a**: S360Reporter developer
- **I want**: to delete the 3,132-line `tk_app.py` monolith and update all imports to use the decomposed modules (`app.py`, `services.py`, `models.py`, `formatters.py`, `dialogs.py`)
- **So that**: the codebase has a single source of truth for each symbol, eliminating the 3,100+ lines of duplicated code and preventing future drift between the monolith and the decomposed modules

- **Out of scope**:
  - Changing any runtime behavior or UI
  - Refactoring the decomposed modules themselves (services.py, models.py, etc.)
  - Adding new features or LLM functionality
  - Modifying the `app.py` SFIReporterApp class

- **Assumptions**:
  - **Assumption (explicit)**: All symbols previously in `tk_app.py` already exist in the decomposed modules (`services.py`, `models.py`, `formatters.py`, `dialogs.py`, `app.py`). If any are missing, they must be added to the appropriate module before `tk_app.py` can be deleted.
  - **Assumption (explicit)**: `app.py:main` is the correct and only entry point going forward.
  - **Assumption (explicit)**: Interface type is the existing Tk GUI desktop app (no change).
  - **Assumption (explicit)**: Target platform is Windows (no change).
  - **Assumption (explicit)**: No data persistence changes — this is purely a code organization cleanup.

- **Acceptance Criteria** (bulleted, testable):
  - `tk_app.py` is deleted from `GUI/src/sfi_reporter/`
  - `pyproject.toml` entry point is updated from `sfi_reporter.tk_app:main` → `sfi_reporter.app:main`
  - Both `.spec` files (`S360Reporter.spec`, `build/S360Reporter.spec`) reference `app.py` instead of `tk_app.py`
  - All production imports (`query_builder.py`, `_diagnose.py`, `_diag2.py`) are retargeted to the correct decomposed modules
  - All test file imports (~8 test files, ~60+ import references) are retargeted to the correct decomposed modules
  - All `mocker.patch()` paths in tests are updated from `sfi_reporter.tk_app.*` to the actual module locations
  - `python -m sfi_reporter.app` launches the application successfully

- **Non-functional requirements**:
  - Zero behavior change — the app must look and behave identically before and after
  - All existing tests must pass after the import retargeting

- **Telemetry / metrics expected**:
  - None (no runtime changes)

- **Rollout / rollback notes**:
  - This is a breaking change for any external code importing from `sfi_reporter.tk_app` — but there are no known external consumers
  - Rollback: restore `tk_app.py` from git history

## Scope Justification

This is a single vertical slice: delete one file and fix all references. The outcome is observable by confirming the file is gone, the app launches, and tests pass.

## Migration Map

| Source (tk_app.py) | Target Module |
|---|---|
| `SFIReporterApp`, `main` | `sfi_reporter.app` |
| `do_refresh`, `get_service_owners`, `get_org_mapping`, `aggregate_by_owner`, `collect_services_for_owner`, `filter_items_by_service`, `filter_items_by_program`, `filter_items_by_id`, `_serialize_org_data_for_cache`, `_deserialize_org_data_from_cache` | `sfi_reporter.services` |
| `OrgAncestry`, `REQUIRED_COLUMNS`, `COLUMN_DISPLAY_NAMES`, `SLA_STATUS_MAP`, `FIELD_GROUPS` | `sfi_reporter.models` |
| `format_field_label`, `format_field_value`, `extract_urls_from_text`, `clean_html_from_title`, `parse_resource_uris`, `group_item_fields`, `_resolve_sla_display`, `_resolve_eta_status`, `get_available_columns`, `filter_item_columns`, `select_all_columns`, `clear_all_columns`, `validate_visible_columns`, `get_empty_columns`, `is_manager_view`, `parse_owners_field`, `extract_direct_reports` | `sfi_reporter.formatters` |
| `DetailModal`, `ItemDetailsModal`, `SortableTreeview`, `ColumnSelectorDialog`, `SingleEtaEditDialog`, `EtaModeDialog`, `ManualEtaReviewDialog`, `BulkEtaProgressDialog` | `sfi_reporter.dialogs` |

## Files Requiring Changes

| File | Change |
|---|---|
| `GUI/src/sfi_reporter/tk_app.py` | DELETE |
| `pyproject.toml` | Entry point → `sfi_reporter.app:main` |
| `GUI/S360Reporter.spec` | Analysis target → `app.py` |
| `GUI/build/S360Reporter.spec` | Analysis target → `app.py` |
| `GUI/src/sfi_reporter/query_builder.py` | Retarget 2 imports |
| `GUI/_diagnose.py` | Retarget imports |
| `GUI/_diag2.py` | Retarget import |
| `GUI/tests/test_tk_app.py` | Retarget all imports + patch paths |
| `GUI/tests/test_detail_modal_colors.py` | Retarget imports |
| `GUI/tests/test_sfi_023.py` | Retarget imports |
| `GUI/tests/test_sfi_024.py` | Retarget imports |
| `GUI/tests/test_sfi_026.py` | Retarget imports |
| `GUI/tests/test_sfi_026_live.py` | Retarget imports |
| `GUI/tests/test_sfi_028.py` | Retarget imports |
| `GUI/tests/test_sfi_029.py` | Retarget imports |
| `BUILD_MANIFEST.md` | Documentation update |
