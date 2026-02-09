# GCP-0031 Architect Notes

## Role: Architect
## Date: 2026-02-08

## Key Decisions

### D1: Pydantic extra="ignore" for backward compat
Old state.json files with dor/dod fields must not crash on load. Using `model_config = ConfigDict(extra="ignore")` on WorkItemState. Need to verify no existing model_config first.

### D2: Consent action rename is atomic
All `skip_dor` → `skip_outputs` changes must happen in one commit. The string appears in: gcp_consent.py, gcp_transition.py, server.py, and ~15 test files.

### D3: _generate_next_steps simplification
Remove `dor_complete`, `dod_complete`, `dor_missing` params. Keep `state` and `required_outputs`. Definition phase: output remediation + "transition when ready". Development: role-specific. Completion: "in completion phase".

## Approval
Design approved with AR-1/2/3 notes in Review Comments. No scope changes.
