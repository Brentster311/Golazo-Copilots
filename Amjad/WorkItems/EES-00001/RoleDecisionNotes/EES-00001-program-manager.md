# EES-00001 — Program Manager Decision Notes

## Design Doc Summary
Created design doc covering all PM responsibilities: summary, problem statement, business case, stakeholders, functional/non-functional requirements, proposed approach with YAML schemas, alternatives considered, risks/mitigations, dependencies, rollout/rollback, observability, and test strategy.

## Key Design Decisions Made

### YAML Schema Design
- Defined concrete schemas for all four file types: `incidents/*.yaml`, `rules/*.yaml`, `ontology.yaml`, `rootcauses.yaml`
- Rules store conditions as structured objects (noun, property, operator, value) rather than raw strings — enables programmatic evaluation in EES-00004

### CLI Interaction Model
- Sequential confirm/edit/reject/specialize flow for each proposed fact
- Root cause confirmation as separate step
- Summary printed at end with metrics

### Data Flow
- Linear pipeline: Load → Extract → Confirm → Ontology Update → Rule Generation → Persist
- No side effects until user confirms — LLM proposals are ephemeral until accepted

### Atomic Writes
- YAML writes use temp file + rename to prevent corruption from partial writes

### Parameterized Nouns
- Nouns use a single parameter for instance identity: `Noun(instance).Property`
- `*` wildcard = any instance of this type (generalized)
- LLM defaults to generalized (`*`) proposals; user can specialize during confirmation
- Single parameter only — no multi-parameter constructors
- Ontology tracks noun types and properties, not instances

## Deferred to Architect
- LLM provider selection
- Incident ID and Rule ID generation strategies
- Project structure / module layout
- Error handling patterns

## No Scope Changes
All requirements trace directly to User Story acceptance criteria. No scope expansion.
