# GCP2-008: Configuration System

**Status**: BACKLOG  
**Priority**: High  
**Size**: M  
**Created**: 2026-01-31  
**Parent**: None (Foundation)

---

## User Story

- **Title**: Configuration System for Per-Repo Customization
- **As a**: Project Owner
- **I want**: Workflow rules (roles, transitions, DoR/DoD items) to be configurable via a YAML file
- **So that**: Teams can customize Golazo without forking the core Python package

- **Out of scope**:
  - GUI for editing config
  - Config validation beyond schema
  - Runtime config reloading

- **Assumptions**:
  - **Assumption (explicit)**: Config file is `golazo.yaml` or `.golazo/config.yaml`
  - **Assumption (explicit)**: Sensible defaults when no config file exists
  - **Assumption (explicit)**: Config is read once at machine initialization

- **Acceptance Criteria**:
  - [ ] `GolazoConfig` class loads from YAML file
  - [ ] `GolazoConfig` provides defaults when file doesn't exist
  - [ ] `GolazoStateMachine` reads roles, transitions, DoR/DoD from config
  - [ ] Config schema documented
  - [ ] Existing tests pass with default config
  - [ ] New tests verify custom config loading

- **Non-functional requirements**:
  - Config loading must be fast (< 50ms)
  - Clear error messages for invalid config

---

## Rationale

### Problem
Current implementation has hardcoded constants in `machine.py`:

```python
VALID_ROLES = ["project-owner", "program-manager", ...]  # Hardcoded
TRANSITIONS = {"project-owner": ["program-manager"], ...}  # Hardcoded
DOR_ITEMS = ["userStory", "designDoc", ...]  # Hardcoded
```

If Retrospective suggests workflow changes, users would need to fork `machine.py`, creating divergent versions.

### Solution
Move these to a per-repo configuration file:

```yaml
# golazo.yaml
roles:
  - project-owner
  - program-manager
  - security-reviewer  # Team A added this
  - tester
  # ...

transitions:
  project-owner: [program-manager]
  program-manager: [security-reviewer, tester]  # Customized
  # ...

dor:
  items: [userStory, designDoc, reviewComments, testCases]
```

### Analogy
Like ESLint:
- `eslint` package = universal, versioned
- `.eslintrc.json` = per-repo rules

Like Golazo V2:
- `golazo` package = universal, versioned, `pip install golazo`
- `golazo.yaml` = per-repo workflow configuration

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| GCP2-001a (State Machine) | Upstream | ? Complete |

**Downstream impact**:
- GCP2-001b (Consent) - consent phrases from config
- GCP2-007 (Profiles) - profile definitions from config

---

## Implementation Notes

Refactors `machine.py` to:
1. Add `GolazoConfig` class with `load()` method
2. Replace module-level constants with config properties
3. Pass config to `GolazoStateMachine.__init__()`

Existing behavior preserved when no config file exists (defaults match current hardcoded values).
