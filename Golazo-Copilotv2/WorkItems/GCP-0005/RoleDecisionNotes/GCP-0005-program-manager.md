# GCP-0005: Program Manager Decision Notes

**Note**: This document was created retroactively to complete the artifact trail.

## Design Summary

Created `gcp_consent` tool for recording deviations with justification.

## Technical Approach

- Store deviations in state.json under `deviations[]` array
- Generate unique deviation IDs
- Validate reason length (min 10 chars)
- Track consumption and expiration

## Dependencies

- GCP-0001 (state persistence)
- GCP-0003 (gcp_transition for force flag integration)
