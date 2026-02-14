# SFI-035 — Architect Decision Notes

## Decisions
1. **Typed `FetchResult` dataclass**: Recommended using a proper dataclass instead of `dict` for fetch result entries. This gives IDE autocompletion and catches key typos at construction time.

2. **No new module**: The `AnalysisResult` and `FetchResult` dataclasses live in `kpi_analyzer.py` alongside the existing functions. No need for a separate models file for 2 small dataclasses.

3. **`format_sources_card` as a pure function in `kpi_analyzer.py`**: The formatting logic for the sources card should be a standalone function that takes an `AnalysisResult` and returns a `str`. This keeps it testable without Tk dependencies. The copilot_panel just calls `_append_message("system", text)`.

4. **Contract boundary**: `analyze_kpi` is the only function whose return type changes. `build_analysis_prompt` signature stays the same. This minimizes blast radius.

## Security
- No new attack surface. Provenance text is rendered in a disabled Tk Text widget via existing `_append_message` method.

## No escalation
No architectural changes needed. No new User Stories required.
