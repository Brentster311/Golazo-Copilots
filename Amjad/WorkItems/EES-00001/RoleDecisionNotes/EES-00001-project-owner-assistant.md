# EES-00001 — Project Owner Assistant Decision Notes

## Work Item ID
- **ID:** EES-00001
- **ID validated against pattern:** `^[a-zA-Z0-9_-]+$` — PASS

## Must-Ask Checklist Resolution
| Question | Answer | Source |
|----------|--------|--------|
| Interface type | GUI (ultimate); CLI for this first slice | User confirmed GUI; CLI assumed for v1 slice with rationale |
| Target platform | Windows only | User confirmed |
| Data persistence | Local YAML files | User confirmed ("local, easiest to iterate over") |
| User type | Technical (developers/engineers) | User confirmed |
| Implementation language | Python | User confirmed |

## Decomposition Decision
The full system was decomposed because it contains multiple user-observable outcomes:
1. Incident ingestion + fact extraction + rule generation (this story)
2. GAP rule detection and refinement
3. RULEOUT rule generation
4. Rule evaluation / testing phase
5. GUI for incident processing and rule management

Each slice is independently implementable and testable.

## Scope Decisions
- **CLI for first slice:** The user selected GUI as the final interface, but the core engine logic must exist before a GUI can wrap it. CLI provides the fastest path to a testable vertical slice. This is documented as an explicit assumption.
- **Single incident processing:** Batch processing deferred to keep the first slice simple and verifiable.
- **Deferred features:** Confidence factors, symptom clusters, OBSERVED/INFERRED distinction, and DRAFT status were explicitly deferred during brainstorming. These are captured in the decisions doc at `docs/expert-system-decisions.md`.

## Key Design Decisions from Brainstorming
These decisions were made collaboratively before the work item was created and are documented in `docs/expert-system-decisions.md`:
- Two-phase model: Troubleshooting (in scope) → Problem Solving (deferred)
- Rule format: `IF <Noun.Property> <op> <value> [AND|OR] THEN <outcome> BECAUSE <reason>`
- Rule types: Positive and RULEOUT (RULEOUT deferred to future story)
- Rule statuses: CONFIRMED and GAP (GAP deferred to future story)
- Boolean logic: Flat AND or flat OR only, no mixing/nesting
- Operators: `==`, `!=`, `>`, `<`, `>=`, `<=`, `contains`, `!contains`
- Conflict resolution: Present all matching root causes as candidates
- GAP rules: Explicit placeholder bridging known→unknown→known
- BECAUSE clause on all rules for explainability
- Rule provenance: Every rule tracks source incident IDs
- RootCause modeled as entity (Name, ActionPlan placeholder)
- Ontology iteratively defined, starts empty
- Storage: Local YAML files

## All Decomposed Work Items
| Work Item | Title | Status | Dependencies |
|-----------|-------|--------|--------------|
| EES-00001 | Core Learning Loop — Incident to Rules | IN PROGRESS | None |
| EES-00002 | GAP Rule Detection and Refinement | BACKLOG | EES-00001 |
| EES-00003 | RULEOUT Rule Generation | BACKLOG | EES-00001 |
| EES-00004 | Rule Evaluation Engine (Testing Phase) | BACKLOG | EES-00001, EES-00002, EES-00003 |
| EES-00005 | GUI for Incident Processing and Rule Management | BACKLOG | EES-00001–EES-00004 |

EES-00002 and EES-00003 are independent of each other but both depend on EES-00001. EES-00004 depends on all three. EES-00005 wraps the full engine.

## Risks
- AI-assisted fact extraction quality depends on LLM capability; user confirmation step mitigates this
- Ontology drift possible without strict matching; case-insensitive matching partially mitigates
