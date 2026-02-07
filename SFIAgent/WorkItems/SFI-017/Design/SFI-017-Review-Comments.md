# SFI-017 — Review Comments

## Design Review

### Clarity & Completeness ✅
- Design doc clearly defines clause model, field type detection, operator sets, and cache format
- Integration point is well-scoped (single button + import in tk_app.py)

### Feasibility ✅
- Pure `evaluate_clauses()` function is the right approach — trivially testable
- Separate module keeps tk_app.py manageable

### Risks & Edge Cases Identified

1. **And/Or evaluation order**: Design says "flat And/Or" but doesn't specify precedence. Recommendation: evaluate left-to-right, no precedence (standard query builder behavior). Each clause narrows (And) or widens (Or) the result set.

2. **Empty clause handling**: What happens if user clicks Run Query with a clause that has no field/operator/value selected? Recommendation: skip incomplete clauses silently (don't error).

3. **Date comparison timezone**: `is_invalid_eta` already handles `Z` → `+00:00` conversion. The `resolve_date_expression` function should produce timezone-aware datetimes consistent with the existing pattern.

4. **Case sensitivity for string operations**: `equals` and `contains` should be case-insensitive to match user expectations.

5. **List-valued fields**: Some fields like `S360_ProgramIds` contain lists. The `contains` operator should check if any element in the list matches (not stringify the list).

6. **Program name resolution in results**: The results summary groups by program. Items may have multiple program IDs. Each item should appear under each of its programs (consistent with main page behavior).

## Architect Notes

### Architectural Alignment ✅
- New module follows existing patterns (separate concerns, pure functions)
- Uses existing `SortableTreeview`, `DetailModal` — no duplicate widgets

### Security / Privacy ✅
- No new network calls — client-side filtering only
- Cache file is in same %TEMP% directory as existing data cache

### Dependency Choices ✅
- No new dependencies — uses only stdlib + existing app modules

### Recommendations
- Ensure `evaluate_clauses` is imported from `query_builder` for use in tests without tkinter
- Consider making `get_field_type` configurable (e.g., dict) rather than hardcoded suffix matching — future-proofs for non-standard field names
