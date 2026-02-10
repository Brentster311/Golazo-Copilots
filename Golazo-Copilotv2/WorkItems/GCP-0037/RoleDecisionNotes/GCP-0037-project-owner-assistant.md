# GCP-0037 — Project Owner Assistant Notes

## Decision
Created as a direct outcome of GCP-0036 retrospective. The version sync algorithm was not updated when we moved from dynamic to static version stamping.

## Scope Rationale
- Single story: one observable outcome (improved stale file reporting)
- The "Capability Index" process improvement suggested in the retro is out of scope — that's a process change, not a product change

## Assumptions Justified
- Source files in the installed package are the authority because that's what bootstrap copies from
- TechBestPractices.md exclusion is necessary because it has no version comment by design
