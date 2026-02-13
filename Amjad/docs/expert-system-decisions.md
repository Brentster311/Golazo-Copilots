# Expert System — Design Decisions (v1)

## Overview

Build a system that reverse-engineers documented incidents into expert system rules for troubleshooting. Given a collection of free-text incident reports, the system extracts facts and generates rules that determine the correct root cause.

## Scope

- **Phase 1 (in scope): Troubleshooting** — From symptoms/observations, follow a diagnostic rule chain to identify a root cause.
- **Phase 2 (deferred): Problem Solving** — Once root cause is identified, determine and execute the appropriate resolution.

## Core Decisions

### Fact Extraction
- **Method:** AI-assisted — the system proposes `Noun.Property = value` facts from free-text incidents, the user confirms/corrects.
- **Incident format:** Free text. Individual incidents may be incomplete (missing steps or root cause).

### Ontology (Noun.Property)
- **Approach:** Iteratively defined. Starts empty. If a matching Noun.Property exists, reuse it; otherwise add a new one.
- **Registry:** Maintained in `ontology.yaml` to prevent drift (e.g., `Server.CPU` vs `Server.CPUUsage`).
- **Parameterized Nouns:** Nouns use a single parameter for instance identity: `Noun(instance).Property`
  - `*` = wildcard (any instance of this type, generalized)
  - LLM defaults to generalized (`*`); user can specialize during confirmation
  - Single parameter only — no multi-parameter constructors
  - Examples: `Server(*).CPUUsage > 90` (any server), `Server(WebApp01).CPUUsage > 90` (specific server)

### Rule Format

**Positive rule (sets a fact or root cause):**
```
RULE <id> (status: CONFIRMED|GAP, sources: [incident-ids])
  IF <Noun.Property> <operator> <value> [AND|OR ...]
  THEN <Noun.Property> = <value>
  BECAUSE <reasoning>
```

**Elimination rule (narrows candidates):**
```
RULE <id> (status: CONFIRMED|GAP, sources: [incident-ids])
  IF <Noun.Property> <operator> <value> [AND|OR ...]
  THEN RULEOUT <RootCauseName>
  BECAUSE <reasoning>
```

### Rule Types
| Type | Purpose |
|------|---------|
| **Positive** | Sets a property value or assigns a root cause (`THEN X = Y`) |
| **RULEOUT** | Eliminates a root cause candidate, preserving diagnostic reasoning |

### Rule Statuses
| Status | Meaning |
|--------|---------|
| **CONFIRMED** | Fully supported by incident evidence |
| **GAP** | Bridges known facts across an unknown middle ("magic happens here") — has defined inputs and outputs but the intermediate logic is unresolved |

### GAP Rules
When an incident reveals the beginning and end of a diagnostic chain but not the middle, the system creates an explicit GAP rule:

```
RULE R-007a (status: CONFIRMED, sources: [INC-012])
  IF Database.ConnectionPool.Active > 90%
  THEN GAP-007 = TRUE

RULE R-007b (status: GAP, sources: [INC-012])
  REQUIRES GAP-007 = TRUE
  PRODUCES Database.ConnectionPoolExhausted = TRUE
  NOTE: "Unknown intermediate steps"

RULE R-007c (status: CONFIRMED, sources: [INC-012])
  IF Database.ConnectionPoolExhausted = TRUE
  THEN RootCause = "Connection Pool Exhaustion"
```

New incidents iteratively refine GAP rules by filling in intermediate steps.

### Boolean Logic
- **Flat only** — each rule uses either all `AND` or all `OR`, never mixed.
- Mixed logic is decomposed into multiple rules that set the same outcome.

### Operators
`==`, `!=`, `>`, `<`, `>=`, `<=`, `contains`, `!contains`

### Conflict Resolution
- When multiple rules fire and assign different root causes, **present all as candidates**.
- This handles incidents with multiple actual problems, or reveals previously misidentified root causes / hidden GAPs.

### BECAUSE Clause
- Present on all rules (positive and RULEOUT).
- Captures the diagnostic reasoning behind the rule.
- Makes the entire rule chain explainable during testing.

### Rule Provenance
- Every rule tracks which incident IDs contributed to its creation.
- Essential for GAP refinement and rule auditing.

### RootCause as Entity
- RootCause is modeled as an entity, not a bare string.
- Properties: `Name`, `ActionPlan` (placeholder for Problem Solving phase).
- Stored in `rootcauses.yaml`.

### Storage
- **Format:** YAML files, local.
- **Structure:**
  - `incidents/*.yaml` — incidents with extracted facts
  - `rules/*.yaml` — expert system rules
  - `ontology.yaml` — Noun.Property registry
  - `rootcauses.yaml` — RootCause entities

### Phases of Use
1. **Learning phase** — Process incidents, extract facts, generate/refine rules.
2. **Testing phase** — Validate rules against incidents, identify gaps and conflicts.

## Deferred for Later Versions
- Problem Solving phase (action plans, remediation)
- Confidence factors on rules
- OBSERVED vs INFERRED fact distinction
- Symptom clusters / 3-tier model (Observations → Patterns → Root Cause)
- DRAFT rule status
