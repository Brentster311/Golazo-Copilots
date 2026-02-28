# GCP-0021: Extend Refactor Role with OOP Design Principles Checklist

**Status**: IMPLEMENTED

---

## User Story

- **Title**: Add OOP Design Principles Checklist to Refactor Expert Role
- **As a**: Developer using the Golazo workflow
- **I want**: The refactor-expert role to include a checklist of 10 OOP design principles to evaluate during refactoring
- **So that**: Code reviews consistently check for common design issues and the refactoring phase produces higher-quality code

---

## Problem Statement

The current refactor-expert role provides general guidance ("identify code smells, duplication, complexity") but lacks a specific, actionable checklist. This leads to inconsistent refactoring depth depending on the AI assistant's interpretation.

Adding a structured checklist of proven OOP design principles ensures:
- Consistent evaluation across all work items
- Educational value for developers reviewing the notes
- Documented rationale for refactoring decisions

---

## Out of Scope
- Automated static analysis tools integration (future work)
- Language-specific linting rules
- Enforcement/blocking based on principle violations

---

## Assumptions
- **Assumption (explicit)**: The checklist is advisory (not blocking) but requires documented rationale for each principle
- **Assumption (explicit)**: All 10 principles apply to any OOP codebase (Python, Java, C#, TypeScript, etc.)
- **Assumption (explicit)**: The role file is located at `golazo-instructions/roles/refactor-expert.md`

---

## Acceptance Criteria

- [x] Refactor-expert role file includes a "Design Principles Checklist" section
- [x] Checklist contains all 10 principles with brief actionable descriptions
- [x] Each principle includes guidance on what to look for
- [x] Role file specifies required rationale format for each principle
- [x] Role file lists acceptable and unacceptable rationales explicitly
- [x] Existing refactor-expert responsibilities are preserved (no behavior removed)

---

## Rationale Framework

### Required Format
Every principle in the refactor notes must have one of:
1. **"Reviewed - no issues found"** (clean)
2. **"N/A - [reason]"** (not applicable to this code)
3. **"Violation found - [action taken or work item created]"** (addressed or tracked)

### Acceptable Rationales
| Category | Example |
|----------|---------|
| Not Applicable | "No inheritance in this codebase - Liskov/Composition N/A" |
| Already Clean | "Reviewed DRY - no duplication found" |
| Scope Limitation | "SRP violation exists but fixing would change behavior - created GCP-XXXX" |
| Intentional Design | "Hard-coded dependency kept for simplicity - single-use script, DI not justified" |
| Partial Fix | "Found 3 DRY violations, fixed 2, third requires major refactor - documented" |

### Unacceptable Rationales (NEVER valid)
| Category | Example | Why Invalid |
|----------|---------|-------------|
| Skipped | "Didn't check this one" | No evaluation performed |
| Vague | "Looks fine" | No evidence of review |
| Deferred without tracking | "Will fix later" | No work item created |
| Ignored violation | "Found issue but didn't want to change it" | No justification |
| **Efficiency excuse** | "Checking this would slow me down" | **Process exists for quality, not speed** |
| **Self-imposed time pressure** | "Running low on context, skipping remaining" | **Not a valid bypass** |

---

## Non-Functional Requirements
- Checklist should be concise (1-2 lines per principle) to avoid overwhelming the role file
- Principles should be language-agnostic

---

## Telemetry / Metrics Expected
- None (documentation-only change)

---

## Rollout / Rollback Notes
- No breaking changes
- Role file update only
- Rollback: Revert role file to previous version

---

## Technical Notes

### The 10 OOP Design Principles

| # | Principle | Look For |
|---|-----------|----------|
| 1 | **DRY** (Don't Repeat Yourself) | Duplicate code blocks; consider extraction. Beware coupling unrelated things. |
| 2 | **Encapsulate What Changes** | Change-prone code exposed publicly; default to private access. |
| 3 | **Open/Closed** | Classes requiring modification to add features; prefer extension points. |
| 4 | **Single Responsibility** | Classes with multiple reasons to change; split by functionality. |
| 5 | **Dependency Inversion** | Hard-coded dependencies; prefer injection over instantiation. |
| 6 | **Composition over Inheritance** | Deep inheritance hierarchies; prefer composition for flexibility. |
| 7 | **Liskov Substitution** | Subclasses that break when substituted for parent; ensure behavioral compatibility. |
| 8 | **Interface Segregation** | Large interfaces forcing unused implementations; split into focused interfaces. |
| 9 | **Program to Interface** | Concrete types in signatures; use abstractions for flexibility. |
| 10 | **Delegation** | Classes doing too much; delegate to specialized classes. |

### File to Update
`golazo-instructions/roles/refactor-expert.md`

---

## Related Work Items
- GCP-0020: Block Transition Without Role Notes (established role notes enforcement)

---

## Closure
- Summary: Backfilled during closure reconciliation.
- Acceptance Criteria: Validation deferred to original implementation records.
- Future Work Items: None.
- Final Status: IMPLEMENTED.
