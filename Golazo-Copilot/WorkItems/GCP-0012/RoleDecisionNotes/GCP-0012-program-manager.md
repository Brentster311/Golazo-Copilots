# GCP-0012: Program Manager Decision Notes

**Note**: This document was created retroactively to complete the artifact trail.

## Design Summary

Allow backward transitions to any earlier role while maintaining forward sequence enforcement.

## Technical Approach

- Modify transition validation logic
- Allow backward moves to any prior role
- Preserve DoR/DoD progress (no rollback)
- Track in role_history

## Dependencies

- GCP-0002 (gcp_transition base implementation)
