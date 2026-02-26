# SFI-040 Domain Expert Notes

## Domain Expertise Assessment
No specialized domain expert consultation required.

## Justification
- Change is a local Tkinter UI presentation adjustment (column order + derived display value).
- No distributed systems, security model, API contract, data store, or compliance impact.
- Existing data fields (`score`, `cost`) are already present; no domain-model change is introduced.

## Guidance for downstream reviewers
- Validate numeric formatting consistency for `Score/Min` across all table branches.
- Ensure zero-cost behavior is explicitly rendered as `∞` as requested.
