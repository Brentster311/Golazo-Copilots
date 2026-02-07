# SFI-017 — Test Cases

## TC-01: evaluate_clauses — Basic string equals filter
**Maps to**: AC-2, AC-4
- Given items with various `ActionOwnerName` values
- When clause = `(Where, ActionOwnerName, equals, "John Doe")`
- Then only items where `ActionOwnerName == "John Doe"` (case-insensitive) are returned

## TC-02: evaluate_clauses — String contains filter
**Maps to**: AC-4
- Given items with various `title` values
- When clause = `(Where, title, contains, "compliance")`
- Then only items containing "compliance" (case-insensitive) in title are returned

## TC-03: evaluate_clauses — String not equals filter
**Maps to**: AC-4
- Given items with `SlaType` values
- When clause = `(Where, SlaType, not equals, "OutOfSla")`
- Then items where `SlaType != "OutOfSla"` are returned

## TC-04: evaluate_clauses — Date on or before filter
**Maps to**: AC-4
- Given items with `dueDate` values including future and past dates
- When clause = `(Where, dueDate, on or before, "2026-02-13")`
- Then only items with dueDate ≤ 2026-02-13 are returned

## TC-05: evaluate_clauses — @Today expression
**Maps to**: AC-4
- Given items with various `dueDate` values
- When clause = `(Where, dueDate, on or before, "@Today - 7")`
- Then items with dueDate ≤ (today - 7 days) are returned

## TC-06: evaluate_clauses — Multiple And clauses
**Maps to**: AC-2
- Given items with various fields
- When clauses = [(Where, SlaType, equals, "OutOfSla"), (And, ActionOwnerName, equals, "John")]
- Then only items matching BOTH conditions are returned

## TC-07: evaluate_clauses — Or clause
**Maps to**: AC-2
- Given items with service names "Svc-A" and "Svc-B"
- When clauses = [(Where, S360_ServiceTreeServiceName, equals, "Svc-A"), (Or, S360_ServiceTreeServiceName, equals, "Svc-B")]
- Then items from either service are returned

## TC-08: evaluate_clauses — USSec Shadow exclusion
**Maps to**: AC-5 (from user story — now implicit in USSec checkbox)
- Given items including one titled "USSec Shadow Action Item"
- When `include_ussec=False`
- Then USSec shadow items are excluded from results

## TC-09: evaluate_clauses — USSec Shadow inclusion
**Maps to**: AC-5
- Given items including one titled "USSec Shadow Action Item"
- When `include_ussec=True`
- Then USSec shadow items are included

## TC-10: evaluate_clauses — Empty/incomplete clauses skipped
**Maps to**: AC-2 (edge case)
- Given a clause with empty field/operator/value
- When evaluated
- Then clause is skipped, all items returned

## TC-11: evaluate_clauses — No clauses returns all items
**Maps to**: AC-7
- Given items and empty clause list
- When evaluated
- Then all items returned (minus USSec if excluded)

## TC-12: get_field_type — Date fields detected
**Maps to**: AC-4
- `dueDate` → "date"
- `EtaDate` → "date"
- `createdDate` → "date"
- `closedDate` → "date"
- `OriginalPublishTime` → "date"

## TC-13: get_field_type — String fields detected
**Maps to**: AC-4
- `title` → "string"
- `SlaType` → "string"
- `ActionOwnerName` → "string"

## TC-14: resolve_date_expression — Valid expressions
**Maps to**: AC-4
- `"@Today - 7"` → today minus 7 days
- `"@Today - 0"` → today
- `"@Today - 30"` → today minus 30 days

## TC-15: resolve_date_expression — Invalid expressions return None
**Maps to**: AC-4
- `"not a date"` → None
- `"@Tomorrow - 5"` → None

## TC-16: Clause cache save/load round-trip
**Maps to**: AC-7 (cached query persistence)
- Given clauses saved to JSON
- When loaded back
- Then clauses match original (field, operator, value, connector)

## TC-17: Clause cache — Clear deletes file
**Maps to**: AC-7
- Given a cached clauses file exists
- When `clear_clause_cache()` is called
- Then file is deleted

## TC-18: evaluate_clauses — List-valued field with contains
**Maps to**: AC-4 (edge case)
- Given an item where `S360_ProgramIds` is `["guid-1", "guid-2"]`
- When clause = `(Where, S360_ProgramIds, contains, "guid-1")`
- Then item is included

## TC-19: evaluate_clauses — None/missing field values
**Maps to**: AC-4 (edge case)
- Given an item where `EtaDate` is None
- When clause = `(Where, EtaDate, on or before, "@Today - 7")`
- Then item is excluded (None cannot satisfy date comparison)

## TC-20: Aggregate results by program
**Maps to**: AC-5
- Given filtered items with known program IDs and a program_names lookup
- When aggregated
- Then each program shows correct Total, Out of SLA, Invalid ETA counts
