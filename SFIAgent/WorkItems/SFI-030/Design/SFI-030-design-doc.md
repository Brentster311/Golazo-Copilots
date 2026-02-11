# Design Doc — SFI-030: Refactor tk_app.py into Focused Modules

## Summary

Split `tk_app.py` (3813 lines, 14 classes, 34 functions) into 6 modules with clear dependency layering. Pure structural refactor — no behavior changes.

## Problem Statement

`tk_app.py` is a monolith containing data models, API logic, business aggregation, 10+ Tk dialog classes, and the main application class. This makes navigation, testing, and code review difficult.

## Proposed Module Split

```
models.py        ← OrgAncestry, constants, column config, display resolvers
formatters.py    ← format_field_label, extract_urls, clean_html, group_item_fields, parse_resource_uris
services.py      ← org mapping, service owners, aggregation, do_refresh, filter functions, settings I/O
dialogs.py       ← All modal dialogs: ColumnSelector, DetailModal, ItemDetailsModal, SortableTreeview,
                    SingleEtaEditDialog, EtaModeDialog, ManualEtaReviewDialog, BulkEtaProgressDialog,
                    SubscriptionPickerDialog, ConfigureLLMDialog, AnalysisProgressModal, AnalysisModal
app.py           ← SFIReporterApp, main(), _load_llm_config, _launch_llm_analysis helpers
tk_app.py        ← Re-export shim (all public names from above modules)
```

### Dependency Graph (no cycles)

```
models.py  (zero internal deps)
    ↑
formatters.py  (imports models for constants only)
    ↑
services.py  (imports models, formatters, data.py, cache.py)
    ↑
dialogs.py  (imports models, formatters, services, tkinter)
    ↑
app.py  (imports all above + query_builder)
    ↑
tk_app.py  (re-exports everything for backward compat)
```

## Implementation Plan

### Phase 1: Create `models.py`
Extract from tk_app.py lines 1–186:
- `OrgAncestry` NamedTuple
- All constants: `REQUIRED_COLUMNS`, `COLUMN_DISPLAY_NAMES`, `SLA_STATUS_MAP`, `_SLA_DISPLAY_MAP`, `COLUMN_ID_MAP`, `COLUMN_WIDTHS`, `COLUMN_ANCHORS`, `URL_PATTERN`, `HTML_ANCHOR_PATTERN`, `FIELD_GROUPS`
- `_resolve_sla_display`, `_resolve_eta_status`
- Column management functions: `get_available_columns`, `filter_item_columns`, `select_all_columns`, `clear_all_columns`, `validate_visible_columns`, `get_empty_columns`

### Phase 2: Create `formatters.py`
Extract from tk_app.py lines 851–1008:
- `format_field_label`, `format_field_value`
- `extract_urls_from_text`, `clean_html_from_title`
- `parse_resource_uris`, `group_item_fields`

### Phase 3: Create `services.py`
Extract from tk_app.py lines 31–834:
- Serialization: `_serialize_org_data_for_cache`, `_deserialize_org_data_from_cache`
- Settings: `_load_setting`, `_save_setting`
- Business logic: `is_manager_view`, `parse_owners_field`, `get_org_mapping`, `extract_direct_reports`, `aggregate_by_owner`, `collect_services_for_owner`
- API: `get_service_owners`, `do_refresh`
- Filters: `filter_items_by_service`, `filter_items_by_program`, `filter_items_by_id`

### Phase 4: Create `dialogs.py`
Extract from tk_app.py lines 1009–2544, 3600–3733:
- `ColumnSelectorDialog`, `DetailModal`, `ItemDetailsModal`
- `SortableTreeview`
- `SingleEtaEditDialog`, `EtaModeDialog`, `ManualEtaReviewDialog`, `BulkEtaProgressDialog`
- `SubscriptionPickerDialog`, `ConfigureLLMDialog`
- `AnalysisProgressModal`, `AnalysisModal`

### Phase 5: Create `app.py`
Extract from tk_app.py lines 2545–3598, 3734–3813:
- `_load_llm_config`
- `SFIReporterApp` class
- `_launch_llm_analysis`, `_on_analysis_complete`, `_on_analysis_error`
- `main()`

### Phase 6: Reduce `tk_app.py` to re-export shim
```python
"""Backward-compatible re-exports — all public names from sub-modules."""
from sfi_reporter.models import *
from sfi_reporter.formatters import *
from sfi_reporter.services import *
from sfi_reporter.dialogs import *
from sfi_reporter.app import *
```

### Phase 7: Update PyInstaller spec
Change entry point from `tk_app.py` to `app.py` and add new modules to `hiddenimports`.

## External Consumers (must keep working via tk_app.py re-exports)

| Symbol | Imported By |
|--------|-------------|
| `OrgAncestry` | test_sfi_026, test_sfi_026_live, test_sfi_029, _diagnose.py |
| `get_org_mapping` | test_sfi_029, _diagnose.py |
| `get_service_owners` | test_sfi_029, _diagnose.py |
| `aggregate_by_owner` | test_sfi_026, test_sfi_029 |
| `collect_services_for_owner` | test_sfi_026 |
| `do_refresh` | test_sfi_026_live, _diag2.py, _diagnose.py |
| `_serialize_org_data_for_cache` | test_sfi_026, test_sfi_026_live |
| `_deserialize_org_data_from_cache` | test_sfi_026 |
| `_resolve_sla_display` | test_sfi_023 |
| `group_item_fields`, `FIELD_GROUPS` | test_detail_modal_colors |
| `ItemDetailsModal` | test_detail_modal_colors |
| `SortableTreeview`, `DetailModal` | query_builder.py |
| `SFIReporterApp` | (entry point only) |

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Circular imports | Strict dependency layering enforced; `dialogs.py` lazy-imports `services` where needed |
| PyInstaller misses new modules | Add to `hiddenimports` in spec file |
| Tests break | Re-export shim ensures `from sfi_reporter.tk_app import X` still works |

## Test Strategy

- All existing tests must pass unchanged (re-exports handle backward compat)
- PyInstaller build must succeed
- No new tests needed (pure structural refactor)
