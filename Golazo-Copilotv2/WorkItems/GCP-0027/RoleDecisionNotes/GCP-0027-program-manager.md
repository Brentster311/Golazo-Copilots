# GCP-0027 Program Manager Notes

## Decision Log

### Key finding: required_outputs is computed but never displayed

During design analysis, discovered that `gcp_status.py` (lines 79-92) already calls `parse_required_outputs()` and `validate_all_outputs()`, returning a `required_outputs` field with full validation state. However, `server.py`'s formatting layer silently drops this data — it never reaches the user.

This means AC #5 ("gcp_status shows missing outputs AND the remediation action") requires TWO fixes:
1. `server.py` must render the `required_outputs` data it currently discards
2. `_generate_next_steps()` must include remediation text based on output validation results

### Key finding: bootstrap-instructions.md is half-updated

The file still references `gcp_mark_dor`/`gcp_mark_dod` with `evidence=` parameters (11+ references) alongside newer output validation docs. This is the primary AC #4 gap.

### Sequencing decision

Chose a 6-step sequential approach:
1. Delete dead code (evidence.py) — already done, verify
2. Update bootstrap instructions — text edit
3. Fix server.py status formatting — render required_outputs
4. Fix gcp_status.py next steps — add remediation
5. Regression check — grep + tests
6. Version bump

Rationale: Steps 3-4 are the only code changes. Everything else is deletion or text updates. Minimal risk.

### No new user stories needed

All work fits within the existing user story scope. The status remediation is covered by AC #5.
