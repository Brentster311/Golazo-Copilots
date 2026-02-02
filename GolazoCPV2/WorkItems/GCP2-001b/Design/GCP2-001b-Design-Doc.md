# GCP2-001b: Consent Enforcement - Design Document

**Work Item**: GCP2-001b  
**Version**: 1.0  
**Created**: 2026-01-31  
**Author**: Program Manager

---

## Summary

Implement a `ConsentEnforcer` class that detects explicit skip requests, handles ambiguous requests with clarification prompts, and logs all deviations to the state file. This ensures the agent never skips workflow roles without explicit user consent.

---

## Problem Statement

The Golazo workflow has gates (DoR, role sequence) but the LLM might interpret vague user requests as permission to skip. We need:
- Deterministic detection of skip intent
- Clarification for ambiguous requests
- Audit trail of all deviations

Without this, the agent could autonomously skip critical roles like Tester or Architect.

---

## Business Case

### Why Now?
GCP2-001a provides the state machine but no consent layer. Before CLI/MCP integration, we need to ensure skips require explicit consent.

**Blocking**: Must complete before GCP2-001c (CLI) and GCP2-001d (MCP).

### Impact
| Metric | Before | After |
|--------|--------|-------|
| Skip detection | LLM interpretation (non-deterministic) | Pattern matching (deterministic) |
| Audit trail | None | Full deviation log |
| Ambiguous handling | LLM guesses | Explicit clarification |

---

## Requirements

### Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1 | `ConsentEnforcer` class with pattern-based skip detection | AC-1 |
| FR-2 | Ambiguous requests return clarification prompt | AC-2, AC-7 |
| FR-3 | Confirmed skips list affected roles | AC-3 |
| FR-4 | Warning for quality gate roles (tester, architect) | AC-4 |
| FR-5 | Log deviations with timestamp, role, user's exact words | AC-5 |
| FR-6 | `get_deviations()` returns audit trail | AC-6 |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Deterministic detection | Same input ? same output |
| NFR-2 | Case-insensitive matching | "SKIP" = "skip" |
| NFR-3 | Append-only audit log | No deletion of deviations |

---

## Proposed Approach

### High-Level Design

```
???????????????????????????????????????????????????????????????
?                    ConsentEnforcer                          ?
???????????????????????????????????????????????????????????????
? - machine: GolazoStateMachine                               ?
? - explicit_patterns: list[Pattern]                          ?
? - ambiguous_patterns: list[Pattern]                         ?
???????????????????????????????????????????????????????????????
? + analyze_request(message) ? RequestAnalysis                ?
? + get_clarification_prompt(analysis) ? str                  ?
? + record_deviation(action, reason) ? None                   ?
? + force_transition(target, reason) ? tuple[bool, str]       ?
? + get_deviations() ? list[dict]                             ?
???????????????????????????????????????????????????????????????
           ?
           ?
    GolazoStateMachine (GCP2-001a)
```

### Pattern Categories

```python
EXPLICIT_SKIP_PATTERNS = [
    r"skip\s+(the\s+)?(\w+)\s+role",
    r"skip\s+to\s+(\w+)",
    r"don'?t\s+need\s+(a\s+)?(design\s+doc|test|review)",
    r"fast[- ]?track",
    r"use\s+express\s+mode",
]

AMBIGUOUS_PATTERNS = [
    r"just\s+fix",
    r"quick\s+fix",
    r"this\s+is\s+simple",
    r"don'?t\s+need\s+all\s+that",
]

QUALITY_GATE_ROLES = ["tester", "architect"]
```

### Request Analysis Flow

```
User message
     ?
     ?
??????????????????????
? Match explicit     ???Yes??> RequestAnalysis(type='explicit_skip')
? skip patterns?     ?
??????????????????????
     ? No
     ?
??????????????????????
? Match ambiguous    ???Yes??> RequestAnalysis(type='ambiguous')
? patterns?          ?
??????????????????????
     ? No
     ?
RequestAnalysis(type='normal')
```

### Deviation Record Format

```python
{
    "action": "skip_role",           # What was done
    "reason": "just fix it",         # User's exact words
    "skipped_roles": ["tester"],     # What was skipped
    "from_role": "program-manager",  # Where we were
    "to_role": "developer",          # Where we went
    "timestamp": "2026-01-31T..."    # When
}
```

---

## Data Classes

```python
@dataclass
class RequestAnalysis:
    """Result of analyzing a user request for skip intent."""
    type: str  # 'normal', 'explicit_skip', 'ambiguous'
    detected_skips: list[str]  # Roles detected for skipping
    confidence: str  # 'high', 'low'
    matched_pattern: str | None  # The pattern that matched

@dataclass  
class SkipResult:
    """Result of processing a skip request."""
    success: bool
    skipped_roles: list[str]
    warning: str | None  # Warning if quality gate skipped
    deviation_logged: bool
```

---

## Clarification Prompts

| Analysis Type | Prompt Template |
|---------------|-----------------|
| ambiguous | "It sounds like you want to skip some workflow steps. To proceed, please explicitly confirm: 'Skip to {suggested_role}' or tell me which roles to skip." |
| quality_gate_warning | "?? You're about to skip {role}, which is a quality gate. This will be logged. Confirm with 'Yes, skip {role}' or say 'No, continue normally'." |

---

## Implementation Phases

| Phase | Deliverable | Description |
|-------|-------------|-------------|
| 1 | Pattern matching | `analyze_request()` with regex patterns |
| 2 | Clarification prompts | `get_clarification_prompt()` |
| 3 | Deviation logging | `record_deviation()` to state |
| 4 | Force transition | `force_transition()` with consent bypass |
| 5 | Quality gate warnings | Special handling for tester/architect |

---

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| LLM-based intent detection | More flexible | Non-deterministic | Rejected for MVP |
| No clarification prompts | Simpler | Risky autonomous skips | Rejected |
| Strict keyword matching | Very deterministic | Too rigid | Rejected |
| Regex patterns | Deterministic, flexible | Complexity | **Selected** |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Patterns miss edge cases | Medium | Medium | Start conservative, expand |
| User frustration with prompts | Low | Medium | Clear, concise prompts |
| Deviation log grows large | Low | Low | Pagination in get_deviations |

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| GCP2-001a (State Machine) | Upstream | ? Complete |
| GCP2-003 (State Persistence) | Upstream | ? Complete |

**Downstream dependents**:
- GCP2-001c (CLI) - wraps consent enforcer
- GCP2-001d (MCP) - exposes consent tools

---

## Test Strategy Summary

| Test Type | Coverage |
|-----------|----------|
| Unit tests | Each pattern, each analysis type |
| Edge cases | Mixed intent, case variations |
| Integration | With state machine transitions |

---

## File Location

```
src/golazo/
??? __init__.py
??? state.py      # GCP2-003 (existing)
??? machine.py    # GCP2-001a (existing)
??? consent.py    # GCP2-001b (new)
```
