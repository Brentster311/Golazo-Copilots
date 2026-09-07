# GCP-0079 Program Manager Notes

## Design Decision

Use one backward-compatible `initial_role` creation input. The orchestrator presents the choice; the tool remains authoritative for eligibility and persistence.

## Sequencing

Tests should establish constructor and tool behavior first, followed by dispatch schema/forwarding, then orchestrator and README contracts.

## Operational Considerations

No migration is required. Existing creation calls continue to initialize at POA, and Planner-initialized state uses the current schema and role loader.