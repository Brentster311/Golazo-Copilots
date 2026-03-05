# GCP-0033 Architect Notes

## Key Decisions

### D1: Use VALID_ROLES from transitions.py
Reuse the existing `VALID_ROLES` list to know the complete set of workflow roles. This avoids duplication.

### D2: Backward transitions create duplicate history entries
A role can appear multiple times in `role_history` (backward transitions). Use the latest entry for each role to determine status. Track by building a dict keyed on role name.

## Approval
Design approved. No concerns.
