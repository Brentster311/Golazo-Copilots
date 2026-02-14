# Expert System — Design Decisions (v2)

## Overview

Build a system that reverse-engineers documented incidents into expert system rules for troubleshooting. Given a collection of free-text incident reports, the system extracts facts and generates rules that determine the correct root cause. The output is an intermediate representation that compiles into deterministic code — Nouns become classes, instance parameters become dictionaries.

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

```
IF <condition> [AND <condition> ...]
THEN CHANGE_STATE|RULED_OUT|GAP
[ELSE CHANGE_STATE|RULED_OUT|GAP]
```

- **ELSE is optional.** Rules without ELSE simply don't produce output when conditions are not met.
- Conditions are joined by **AND** (explicit keyword).
- Each condition is either a `Noun.Property <operator> <value>` test, or a reference to a RULED_OUT produced by another rule.

### Output Entity Types

| Type | Meaning | Chainable? |
|------|---------|------------|
| **CHANGE_STATE("...")** | Describes a concrete state mutation (e.g., `"Mail.Send permission => true"`) | Yes — downstream rules can depend on it |
| **RULED_OUT("...")** | Elimination — this cause has been excluded (e.g., `"Admin consent is not the issue"`) | Yes — can appear in conditions of other rules |
| **GAP("...")** | Unknown — knowledge base doesn't cover this case (e.g., `"All known causes eliminated"`) | No — terminal |

### Example Rules

**R1:**
```
IF User.role = "non-admin"
THEN CHANGE_STATE("User.role => admin-escalated")
ELSE RULED_OUT("User access is not the issue")
```

**R2:**
```
IF AppRegistration.adminConsent = "not granted"
THEN CHANGE_STATE("AppRegistration.adminConsent => granted")
ELSE RULED_OUT("Admin consent is not the issue")
```

**R3:**
```
IF AppRegistration.permissions contains "Mail.Send" = false
THEN CHANGE_STATE("Mail.Send permission => true")
ELSE RULED_OUT("Mail.Send permission is already present")
```

**R4 (chaining — consumes RULED_OUTs):**
```
IF RULED_OUT("User access is not the issue") AND RULED_OUT("Admin consent is not the issue") AND RULED_OUT("Mail.Send permission is already present")
THEN GAP("All known causes eliminated — investigate further")
```

### How Chaining Works
- R1/R2/R3 each produce either a CHANGE_STATE (found a problem) or a RULED_OUT (this isn't the cause).
- R4 collects all three RULED_OUTs. If every known cause is eliminated but the problem persists, R4 fires and declares a GAP.
- If any rule found a problem (CHANGE_STATE), R4 doesn't fire — there's still an active lead.

### Boolean Logic
- **AND only** — conditions are joined by explicit `AND` keyword.
- OR logic is decomposed into multiple rules that produce the same outcome.

### Operators
`==`, `!=`, `>`, `<`, `>=`, `<=`, `contains`, `!contains`

### Conflict Resolution
- When multiple rules fire and produce different outputs, **present all as candidates**.
- This handles incidents with multiple actual problems, or reveals hidden GAPs.

### Rule Provenance
- Every rule tracks which incident IDs contributed to its creation.
- Essential for GAP refinement and rule auditing.

### Storage
- **Format:** YAML files, local.
- **Structure:**
  - `incidents/*.yaml` — incidents with extracted facts
  - `rules/*.yaml` — expert system rules
  - `ontology.yaml` — Noun.Property registry

### Phases of Use
1. **Learning phase** — Process incidents, extract facts, generate/refine rules.
2. **Testing phase** — Validate rules against incidents, identify gaps and conflicts.

## Deferred for Later Versions
- Problem Solving phase (action plans, remediation)
- Confidence factors on rules
- OBSERVED vs INFERRED fact distinction
- Symptom clusters / 3-tier model (Observations → Patterns → Root Cause)
- DRAFT rule status
- BECAUSE clause (diagnostic reasoning per rule)
- RootCause as a separate entity type (currently root cause fixes are CHANGE_STATEs)
