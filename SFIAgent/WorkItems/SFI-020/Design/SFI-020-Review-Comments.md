# SFI-020 — Review Comments

## Design Review: Right-Click KPI Row → Analyze with LLM (Core)

| Reviewer | Role | Date |
|----------|------|------|
| QA (Golazo) | Quality Assurance | 2026-02-06 |

---

### ✅ Strengths

1. **Clean module separation** — `llm_client.py` and `llm_storage.py` are well-scoped; keeps `tk_app.py` changes minimal
2. **Consistent patterns** — Threading follows `_do_refresh`, storage follows `CacheManager`, modals follow `ItemDetailsModal`
3. **Extensibility stub** — `build_prompt(url_content=None)` future-proofs for SFI-021 at zero cost
4. **Schema versioning** — `schema_version: 1` in saved JSON enables future migration

---

### ⚠️ Issues to Address

#### Issue 1: Concurrent Analysis Guard (Medium)
**Problem**: No guard against multiple simultaneous LLM calls (user right-clicks two different items before first completes).  
**Recommendation**: Add an `_analysis_in_progress` flag on `SFIReporterApp`. While true, context menu shows "Analysis in progress…" (disabled). Reset in the `root.after(0, ...)` callback.

#### Issue 2: Row Selection on Right-Click (Medium)
**Problem**: Design says "the row is selected on right-click" but doesn't specify how. On tkinter, `<Button-3>` does NOT auto-select the treeview row.  
**Recommendation**: In the `<Button-3>` handler, call `tree.identify_row(event.y)` and `tree.selection_set(row_id)` before showing the context menu. If click is on empty space (no row), don't show menu.

#### Issue 3: Empty/Missing Field Handling in Prompt (Low)
**Problem**: `build_prompt` design doesn't specify what happens when key fields are `None`, empty string, or missing from the dict.  
**Recommendation**: `build_prompt` should handle missing fields gracefully — use "N/A" or omit the field from the prompt. Test with a minimal item dict (only `id` present).

#### Issue 4: AnalysisProgressModal Dismissal (Low)
**Problem**: What happens if user closes the progress modal while analysis is running?  
**Recommendation**: Override `WM_DELETE_WINDOW` to either ignore close or cancel the analysis. Document the chosen behavior.

#### Issue 5: Config Error UX (Low)
**Problem**: Design says "clear error message" for missing config but doesn't specify what the message says or where it appears.  
**Recommendation**: Show a `messagebox.showerror` with the specific missing variable name(s) and a brief setup instruction. Example: "Azure OpenAI not configured. Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_DEPLOYMENT environment variables."

---

### ℹ️ Notes for Developer

1. **PyInstaller bundle size**: `openai` package pulls in `httpx`, `pydantic`, etc. Verify the `.exe` size delta after adding the dependency. If >20MB increase, flag for discussion.
2. **Token budget**: GPT-4o has a 128K context window, so truncation is unlikely for a single action item's fields. However, when SFI-021 adds URL content, truncation will become critical. The stub is the right approach.
3. **LLM response parsing**: Don't assume the LLM perfectly follows the section header format. Use a best-effort parser that falls back to displaying the raw response if sections can't be extracted.
4. **DetailModal class name**: The design doc references "DrillDownModal" in the user story but the actual class is `DetailModal`. Use `DetailModal` in code.

---

### Verdict

**APPROVED with conditions** — Address Issues 1–2 (Medium) during development. Issues 3–5 (Low) are recommended but non-blocking.

---

## Architect Notes

**Reviewer**: Architect (Golazo) | **Date**: 2026-02-06

### Architectural Alignment
- ✅ Module separation (`llm_client`, `llm_storage`) follows existing patterns — `data.py` for data, `cache.py` for cache
- ✅ Threading pattern matches `_do_refresh` — no new concurrency model introduced
- ✅ Storage location (`%LOCALAPPDATA%`) consistent with `s360_client.CacheManager`

### API & Data Contracts
- ✅ `AnalysisResult` dataclass defines a clear contract between `llm_client` and `llm_storage`/`AnalysisModal`
- ✅ JSON schema with `schema_version` enables future migration
- ⚠️ **File encoding**: Explicitly use `encoding="utf-8"` on all file reads/writes. Windows default is `cp1252` which will corrupt non-ASCII characters in LLM responses.

### Security & Privacy
- ✅ API key from env vars only; never logged
- ⚠️ **Action item data to LLM**: Action items may contain PII (owner names, aliases). Azure OpenAI enterprise deployments have data processing agreements, but log a warning at DEBUG level noting data is being sent to the LLM.
- ✅ No credentials sent to external URLs (SFI-021 concern, not SFI-020)

### Resilience & Failure Isolation
- ✅ LLM failure doesn't affect core app — context menu is additive
- ✅ Storage failure (disk full, permissions) should be caught and logged but not crash the app
- ⚠️ **Atomic writes for storage**: Use write-to-temp-then-rename pattern (like `column_cache.py`) to prevent corrupted files on crash during write

### Dependency Assessment
- ✅ `openai>=1.0.0` is well-maintained, enterprise-standard
- ⚠️ **Pin `openai` upper bound**: Consider `openai>=1.0.0,<3.0.0` to prevent breaking changes from major version bumps in PyInstaller builds

### Verdict
**APPROVED** — Address ⚠️ items (UTF-8 encoding, atomic writes, dependency pinning) during development. No architectural blockers.
