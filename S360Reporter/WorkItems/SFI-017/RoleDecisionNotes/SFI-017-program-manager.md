# SFI-017 — Program Manager Notes

## Decisions

1. **Separate module `query_builder.py`**: Keeps query builder logic isolated from the already-large `tk_app.py` (2168 lines). Follows SRP. Only integration point is a button + import.

2. **Pure `evaluate_clauses()` function**: The core filtering logic is a standalone function that takes items + clauses and returns filtered items. This is trivially testable without any tkinter dependency.

3. **Non-modal Toplevel**: Unlike DetailModal which uses `grab_set()`, the query builder should be non-modal so users can keep the main page visible while building queries.

4. **Field type detection by name**: Rather than inspecting actual values, we detect date fields by checking if the key ends in `Date`, `Time`, `Eta`. This is reliable for the S360 column naming convention and avoids parsing every value.

5. **No nested grouping in v1**: Flat And/Or keeps both implementation and UX simple. Each clause is evaluated in order.

6. **Cache format includes USSec checkbox state**: So the full query state is restored on reopen.
