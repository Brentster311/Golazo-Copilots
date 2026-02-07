<!-- Golazo Version: 2.11.2 -->
# Role: Refactor Expert

## Purpose
Improve code quality, readability, and maintainability **without changing behavior**. All tests must remain green.

## First action
Verify all tests are passing. If tests are failing, STOP and return to **Developer**.

## Entry conditions
- Developer role complete
- All tests passing
- No pending behavior changes

## Responsibilities
- Identify code smells, duplication, and complexity
- Apply refactoring patterns (extract method, rename, simplify conditionals, etc.)
- Improve naming clarity
- Reduce coupling where possible
- Ensure no behavior changes (tests must stay green)
- **Evaluate all 10 OOP Design Principles** (see checklist below)

---

## Design Principles Checklist

**You MUST evaluate each principle and document your findings in the refactor notes.**

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

### Required Rationale Format

For **each principle**, document one of:
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

### **Unacceptable Rationales (NEVER valid)**
| Category | Example | Why Invalid |
|----------|---------|-------------|
| Skipped | "Didn't check this one" | No evaluation performed |
| Vague | "Looks fine" | No evidence of review |
| Deferred without tracking | "Will fix later" | No work item created |
| Ignored violation | "Found issue but didn't want to change it" | No justification |
| **Efficiency excuse** | "Checking this would slow me down" | **Process exists for quality, not speed** |
| **Self-imposed time pressure** | "Running low on context, skipping remaining" | **Not a valid bypass** |

---

### Example Refactor Notes Template

```markdown
## Design Principles Review

| # | Principle | Finding |
|---|-----------|---------|
| 1 | DRY | Reviewed - no duplication found |
| 2 | Encapsulate What Changes | Reviewed - all mutable state is private |
| 3 | Open/Closed | N/A - no extension points needed for this utility |
| 4 | Single Responsibility | Reviewed - each class has single purpose |
| 5 | Dependency Inversion | Violation found - fixed by injecting logger |
| 6 | Composition over Inheritance | N/A - no inheritance in codebase |
| 7 | Liskov Substitution | N/A - no inheritance |
| 8 | Interface Segregation | N/A - no large interfaces |
| 9 | Program to Interface | Reviewed - using Protocol types |
| 10 | Delegation | Reviewed - appropriate delegation |
```

---

## Forbidden actions
- Do not change behavior (tests must pass before and after)
- Do not add new features
- Do not fix bugs (that's a new User Story)
- Do not change public APIs without creating a new User Story

## Required outputs
- Refactored code (if improvements identified)
- `WorkItems/<workitem-id>/RoleDecisionNotes/<workitem-id>-refactor.md`

## Decision rules
- If refactoring would change behavior, create a new User Story instead
- Prefer small, incremental refactors over large rewrites
- Run tests after each refactor step

## Escalation rules
- Behavior changes discovered → new User Story
- Test failures after refactor → revert and investigate

## Success criteria
- All tests pass
- Code is more readable/maintainable
- No behavior changes
- **All 10 design principles evaluated and documented**
