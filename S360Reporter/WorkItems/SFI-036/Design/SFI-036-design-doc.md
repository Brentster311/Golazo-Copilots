# SFI-036 Design Doc — Remove tk_app.py monolith

## Summary

Delete the 3,132-line `tk_app.py` monolith and retarget all imports to the decomposed modules (`app.py`, `services.py`, `models.py`, `formatters.py`, `dialogs.py`). Update entry points and build configs.

## Problem Statement

The SFI-030 refactor decomposed `tk_app.py` into 5 focused modules but left the original monolith in place. All 12+ consuming files still import from `tk_app.py`, creating 3,100+ lines of dead duplicated code and risk of divergence.

## Business Case

- **Why now**: Every future change risks being made in the wrong file. The copilot panel and LLM button only exist in `app.py`, proving the drift has already occurred.
- **Impact**: Eliminates confusion, reduces LOC by ~3,100.
- **KPIs**: Zero behavior change; all tests pass; single entry point.

## Stakeholders

- Developer (maintainer) — primary beneficiary

## Functional Requirements

1. Delete `GUI/src/sfi_reporter/tk_app.py`  
2. Update `pyproject.toml` entry point → `sfi_reporter.app:main`  
3. Update both `.spec` files → `app.py`  
4. Retarget all imports in production code (2 files)  
5. Retarget all imports in test code (8 files)  
6. Update all `mocker.patch` paths in tests  

## Non-Functional Requirements

- Zero behavior change
- All existing tests pass
- App launches identically

## Proposed Approach

### Phase 1: Verify decomposed modules (already done)
All 40 symbols confirmed present in the decomposed modules.

### Phase 2: Retarget imports
Update each file using the migration map from the User Story.

### Phase 3: Update configs
- `pyproject.toml` L30
- `S360Reporter.spec` L5
- `build/S360Reporter.spec` L5
- `BUILD_MANIFEST.md`

### Phase 4: Delete tk_app.py

### Phase 5: Verify
- `python -m sfi_reporter.app` launches
- `pytest GUI/tests/` passes

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Keep `tk_app.py` as re-export shim | Still leaves 3,100 lines; or creates a thin shim that masks the real modules, hiding import errors |
| Gradual migration (file by file) | Unnecessary complexity for a straightforward rename |

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Missing symbol in decomposed module | All 40 verified present before implementation |
| External consumer imports from tk_app | No known external consumers; git revert if needed |
| Test patch paths wrong | Run full test suite after changes |

## Dependencies

- All decomposed modules must be present (confirmed)

## Migration / Rollback

- **Migration**: Single commit; no data migration needed
- **Rollback**: `git revert` restores `tk_app.py`

## Observability

- No runtime changes; no new logging needed

## Test Strategy

- Run existing test suite — 100% pass rate required
- Manual smoke test: launch app, verify UI is identical

## Import Retargeting Reference

| Symbol | Target Module |
|---|---|
| `SortableTreeview` | `sfi_reporter.dialogs` |
| `DetailModal` | `sfi_reporter.dialogs` |
| `ItemDetailsModal` | `sfi_reporter.dialogs` |
| `EtaModeDialog` | `sfi_reporter.dialogs` |
| `ManualEtaReviewDialog` | `sfi_reporter.dialogs` |
| `ColumnSelectorDialog` | `sfi_reporter.dialogs` |
| `SingleEtaEditDialog` | `sfi_reporter.dialogs` |
| `BulkEtaProgressDialog` | `sfi_reporter.dialogs` |
| `do_refresh` | `sfi_reporter.services` |
| `get_service_owners` | `sfi_reporter.services` |
| `get_org_mapping` | `sfi_reporter.services` |
| `aggregate_by_owner` | `sfi_reporter.services` |
| `collect_services_for_owner` | `sfi_reporter.services` |
| `filter_items_by_service` | `sfi_reporter.services` |
| `filter_items_by_program` | `sfi_reporter.services` |
| `filter_items_by_id` | `sfi_reporter.services` |
| `is_manager_view` | `sfi_reporter.services` |
| `parse_owners_field` | `sfi_reporter.services` |
| `extract_direct_reports` | `sfi_reporter.services` |
| `_serialize_org_data_for_cache` | `sfi_reporter.services` |
| `_deserialize_org_data_from_cache` | `sfi_reporter.services` |
| `OrgAncestry` | `sfi_reporter.models` |
| `REQUIRED_COLUMNS` | `sfi_reporter.models` |
| `COLUMN_DISPLAY_NAMES` | `sfi_reporter.models` |
| `FIELD_GROUPS` | `sfi_reporter.models` |
| `_resolve_sla_display` | `sfi_reporter.models` |
| `_resolve_eta_status` | `sfi_reporter.models` |
| `get_available_columns` | `sfi_reporter.models` |
| `filter_item_columns` | `sfi_reporter.models` |
| `select_all_columns` | `sfi_reporter.models` |
| `clear_all_columns` | `sfi_reporter.models` |
| `validate_visible_columns` | `sfi_reporter.models` |
| `get_empty_columns` | `sfi_reporter.models` |
| `format_field_label` | `sfi_reporter.formatters` |
| `format_field_value` | `sfi_reporter.formatters` |
| `extract_urls_from_text` | `sfi_reporter.formatters` |
| `clean_html_from_title` | `sfi_reporter.formatters` |
| `parse_resource_uris` | `sfi_reporter.formatters` |
| `group_item_fields` | `sfi_reporter.formatters` |
| `write_cache` | `sfi_reporter.cache` (patch target for tests) |
