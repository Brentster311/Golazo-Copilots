# SFI-007: Program Manager Notes

## Date: 2026-02-04

## Design Decisions

### Modal vs In-Place Expansion
Chose modal for consistency with existing drill-down pattern and simpler implementation.

### Field Grouping
Organized 30 fields into logical groups:
1. Identity (title, IDs)
2. Status (SLA, classification)
3. Dates (due, ETA, published)
4. Ownership (assigned to, action owner)
5. Service/Program (service IDs, program IDs)
6. Other (remaining fields)

### Empty Field Handling
Hide fields with empty/null values to reduce clutter.

### Text vs Treeview for Display
Using scrollable Text widget for flexibility - fields vary in length and structure (some are lists).

## Implementation Complexity
- Low complexity: Follows established modal pattern
- Main work: Field grouping and formatting logic

## Next Steps
Proceed to Quality Assurance for review and test cases.
