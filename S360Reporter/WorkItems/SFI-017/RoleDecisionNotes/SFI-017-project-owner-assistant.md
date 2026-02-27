# SFI-017 — Project Owner Assistant Notes

## Decisions

1. **Single story, not split**: The feedback contained multiple filter needs plus a summary view. These all converge on a single user-observable outcome — a query builder window — so they belong in one story with 7 acceptance criteria.

2. **Generic clause-based builder, not fixed filters**: User provided an ADO/IcM query editor screenshot as reference. Instead of fixed dropdowns for Program/Service/Lead, the form should allow adding arbitrary clauses on any field with And/Or logic. This is more powerful and extensible.

3. **Clause model**: Each clause = `(And/Or, Field, Operator, Value)`. First clause has no connector. Operators are contextual: string fields → equals/not equals/contains; date fields → on or before/on or after/equals + `@Today - N` expressions.

4. **New Toplevel window, not inline**: User explicitly said "off the main page, let's create a new form." This matches the existing modal pattern (DetailModal, ItemDetailsModal) and avoids disrupting the current layout.

5. **Client-side filtering only**: Data is already loaded in memory via `fetch_full_data()`. No need for new API calls — just filter the `action_items` list.

6. **USSec Shadow exclusion as default-on checkbox**: User said "never include" — providing an override checkbox is more flexible and testable.

7. **Value combobox populated from data**: For each selected field, the value dropdown is populated with distinct values from the loaded dataset. User can also type free-text or date expressions.

8. **Summary grouped by Program**: The feedback specifically asked for "Total/OutOfSLA/InvalidETA by program" — this becomes the results table below the clause builder.

9. **Flat And/Or only for v1**: No nested grouping/parentheses. Keeps implementation simple. Can be a future enhancement.

10. **Clause caching via existing cache directory**: Clauses are persisted to `%TEMP%/GUI/query_clauses.json` using the same cache directory as the existing data cache (`cache.py:get_cache_dir()`). JSON format — simple list of `{connector, field, operator, value}` dicts. Auto-restored on form open, auto-saved on Run Query. Clear button removes the cache file. No save/load UX needed.

## Must-Ask Checklist

- [x] **Interface type**: Tkinter GUI (established — existing app)
- [x] **Target platform**: Windows (established — exe distribution)
- [x] **Data persistence**: In-memory (already loaded from S360 API + cached to %TEMP%)
- [x] **User type**: SFI leads/managers (technical, Microsoft internal)
