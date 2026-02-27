# GCP-0055 — Developer Notes

## Implementation
- Introduced profile role sequencing in `core/transitions.py`:
  - `PROFILE_ROLES`
  - `get_role_order_for_profile(profile)`
  - profile-derived forward transition map generation.
- Updated transition evaluation to be profile-aware:
  - `validate_transition(..., profile=...)`
  - `is_backward_transition(..., profile=...)`
- Updated runtime transition tool to pass `state.profile` to transition checks.
- Updated `golazo_status` role progress computation to use profile-specific role order.

## Additional Reliability Fixes
- Fixed `golazo_bootstrap` capability template overwrite logic for `force=True`.
- Hardened bootstrap test cleanup on Windows with retry-based directory removal.
