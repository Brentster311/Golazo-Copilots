# GCP-0065 Program Manager Notes

## Request Interpretation
User specified migration behavior: when `capabilities.yaml` is found outside `WorkItems/`, move it to the canonical `WorkItems/` location.

## Scope Decisions
- Included automatic migration from legacy path to canonical path.
- Included conflict scenario handling requirement where both legacy and canonical files exist.
- Kept schema changes and broader capability redesign out of scope.

## Delivery Sequencing
1. Centralize resolver logic.
2. Add migration behavior.
3. Add deterministic conflict handling and messaging.
4. Expand tests for path permutations.

## Risk Calls
- File move semantics can vary by platform and permissions; explicit error messaging and tests are required.
