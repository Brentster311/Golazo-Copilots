# SFI-020 Review Comments

**Work Item**: SFI-020  
**Reviewer Role**: Program Manager (self-review) + Architect considerations  
**Date**: 2026-02-06

---

## Design Review Summary

The design introduces three concerns (LLM integration, persistent storage, UI) with clear module boundaries. Overall assessment: **Approved with notes**.

---

## Review Items

### ✅ Approved — Context Menu Pattern
- Using `<Button-3>` with `identify_row()` + `selection_set()` is the standard tkinter right-click pattern.
- Creating `tk.Menu` on-demand (not cached) avoids stale state issues.
- Binding on both `tree_kpis` and `DrillDownModal._tree` covers all KPI row surfaces.

### ✅ Approved — Module Separation
- `llm_client.py` (API concerns) and `llm_storage.py` (persistence) are cleanly separated from `tk_app.py` (UI).
- Each module is independently testable with mocks.

### ✅ Approved — Threading Model
- Follows the proven `_do_refresh` pattern: daemon thread + `root.after(0, callback)`.
- Progress modal prevents user from triggering concurrent analyses on the same item.

### ✅ Approved — Storage in `%LOCALAPPDATA%`
- Durable across reboots (unlike `%TEMP%`).
- Consistent with `s360_client` cache location.
- Atomic write via `.tmp` + `os.replace()` prevents corruption.
- `schema_version` field enables future migration.

### ⚠️ Note — `openai` Package Dependency
- The `openai` SDK pulls in `httpx`, `pydantic`, `anyio`, etc.
- **Action**: After implementation, verify PyInstaller build size increase is acceptable. Add hidden imports to `.spec` if needed.

### ⚠️ Note — Prompt Token Budget
- Action items can have large `Remediation` and `Details` fields.
- **Action**: Developer should implement a truncation utility that prioritizes: Title → SLA/Dates → Ownership → Remediation (truncated) → Details (truncated). Target ≤3000 input tokens.

### ⚠️ Note — Error UX for Missing Config
- First-time users will not have env vars set.
- **Action**: The error message for missing `AZURE_OPENAI_ENDPOINT` / `AZURE_OPENAI_API_KEY` should include clear setup instructions (not just "missing env var").

### ⚠️ Note — Concurrent Analysis Guard
- Design doesn't explicitly prevent the user from right-clicking another row while analysis is in-flight.
- **Action**: The progress modal's `grab_set()` should block interaction with the parent window. Verify this in implementation.

### ✅ Approved — Security
- API key never logged or displayed.
- Data stays within Azure tenant.
- Masked `__repr__` on `LLMConfig`.

### ✅ Approved — Disclaimer
- "AI-generated analysis — verify before acting" footer is appropriate for enterprise use.

---

## Architect Considerations

### Interface Boundary
- `analyze_item()` takes a raw `dict` (action item). Consider whether a typed dataclass would be better for maintainability.
- **Decision**: Keep `dict` for now — it matches how `detailed_items` are stored throughout the app. A typed model could be a refactoring story later.

### Extensibility for SFI-021
- The prompt builder (`build_prompt()`) should accept an optional `url_content: dict[str, str]` parameter (defaulting to `None`) so SFI-021 can plug in without changing the function signature.
- **Action**: Developer should add this parameter stub now even though it won't be used until SFI-021.

### Extensibility for SFI-022
- `llm_storage.py` already provides `load_analysis()` and `analysis_exists()` — SFI-022 will consume these directly.
- No additional prep needed.
