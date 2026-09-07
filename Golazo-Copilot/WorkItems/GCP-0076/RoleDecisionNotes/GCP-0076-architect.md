# GCP-0076 Architect Decision Notes

## Approval

Approved with a shared resolver boundary in `golazo_capabilities.py`. Path constants and resolution behavior have one owner; callers choose read-only lookup or mutating ensure/migration according to responsibility.

## Key Decisions

- Canonical always wins over legacy.
- Status is read-only.
- Setup and capability-query paths may migrate legacy data.
- The registry template remains packaged data but is written only to the canonical path.
- Nested workspace registries are independent and must not be globally deduplicated.

## Impact Review

The existing registry identifies only bootstrap skill installation. Missing impact coverage for core capability operations confirms the need to populate the canonical registry in this work item.
