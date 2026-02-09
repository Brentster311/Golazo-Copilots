# GCP-0031 Project Owner Assistant Notes

## Role: Project Owner Assistant
## Date: 2026-02-08

## Decision
Created from GCP-0027 retrospective AI-1. The DoR/DoD checklist system is dead weight — tools to mark items were removed (GCP-0027), but the data structures, gate checks, and rendering remain. The output validation system (GCP-0025/0026) is the replacement and is working correctly.

## Scope Rationale
Single user-observable outcome: the zombie DoR/DoD system disappears from status output and stops blocking transitions. 7 ACs cover schema, status, gate, transition, dead module, init, and tests.

## Key Design Decision: skip_dor action rename
The `skip_dor` consent action is dual-purpose: it was the old DoR gate bypass AND is currently reused for output validation bypass in gcp_transition. Recommend renaming to `skip_outputs` for clarity.
