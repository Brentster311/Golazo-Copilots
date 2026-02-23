# GCP-0050 — Program Manager Notes

## Design Decisions
- Preserve existing sections (forbidden actions, file naming, gate enforcement) — they're proven
- New orchestrator sections go between forbidden actions and operational sections
- Target ≤150 lines to keep within Copilot's reliable instruction-following range
