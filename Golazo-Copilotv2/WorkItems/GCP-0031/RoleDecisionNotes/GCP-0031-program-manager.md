# GCP-0031 Program Manager Notes

## Role: Program Manager
## Date: 2026-02-08

## Key Decisions
- 10-step sequential approach: delete dead module first, then modify types, then consumers
- Rename `skip_dor` → `skip_outputs` rather than just deleting (it's reused for output validation bypass)
- Backward compat via Pydantic `extra="ignore"` — old state files load without error
- `_generate_next_steps` simplified to only use `state` + `required_outputs` params

## Sequencing Rationale
Delete checklists.py first because it's a leaf dependency. Then types.py (root model), then consumers outward. Tests last since they'll break until production is fixed.
