# GCP2-001a: Core State Machine

**Status**: BACKLOG  
**Priority**: High  
**Size**: M  
**Created**: 2026-01-27  
**Parent**: GCP2-001

---

## User Story

- **Title**: Core State Machine
- **As a**: Golazo V2 agent
- **I want**: A programmatic state machine that tracks workflow progress
- **So that**: Role transitions are validated and enforced consistently

- **Out of scope**:
  - Consent detection logic (GCP2-001b)
  - Audit logging of deviations (GCP2-001b)
  - Protocol/CLI commands (GCP2-001c)
  - Copilot/MCP integration (GCP2-001d)

- **Assumptions**:
  - **Assumption (explicit)**: Custom state machine implementation (no external library)
  - **Assumption (explicit)**: Single work item active at a time (multi-session in GCP2-006)
  - **Assumption (explicit)**: State persisted via GCP2-003 schema

- **Acceptance Criteria**:
  - [ ] `GolazoStateMachine` class implemented with role/phase tracking
  - [ ] `current_role` and `current_phase` properties return current state
  - [ ] `can_transition(target)` validates transitions and returns (bool, reason)
  - [ ] `transition(target)` performs valid transitions and updates state file
  - [ ] `check_dor()` and `check_dod()` return checklist status
  - [ ] Transitions blocked when DoR incomplete at Development phase boundary
  - [ ] State loaded from / saved to `WorkItems/<id>/state.json`

- **Non-functional requirements**:
  - State machine operations must be synchronous and deterministic
  - No external dependencies beyond Python standard library
  - Clear error messages for invalid transitions

- **Telemetry / metrics expected**:
  - None for MVP

- **Rollout / rollback notes**:
  - Core component; must be stable before dependent work items proceed

---

## API Design

```python
class GolazoStateMachine:
    def __init__(self, work_item_id: str, state_path: Path = None):
        """Load or create state for work item."""
    
    @property
    def current_role(self) -> str:
        """Current active role (e.g., 'developer')."""
    
    @property
    def current_phase(self) -> str:
        """Current phase (design/development/release)."""
    
    @property
    def profile(self) -> str:
        """Workflow profile (complete/express/spike)."""
    
    def can_transition(self, target_role: str) -> tuple[bool, str]:
        """Check if transition is valid. Returns (allowed, reason)."""
    
    def transition(self, target_role: str) -> bool:
        """Perform transition if valid. Returns success."""
    
    def check_dor(self) -> dict:
        """Return DoR checklist with status."""
    
    def check_dod(self) -> dict:
        """Return DoD checklist with status."""
    
    def mark_dor_item(self, item: str, complete: bool) -> None:
        """Mark a DoR item as complete/incomplete."""
    
    def mark_dod_item(self, item: str, complete: bool) -> None:
        """Mark a DoD item as complete/incomplete."""
```

---

## State Transitions (Complete Profile)

```
Design Phase:
  project-owner ? program-manager ? tester ? architect

Development Phase:
  architect ? developer ? refactor-expert

Release Phase:
  refactor-expert ? builder ? documentor ? [complete]
```

---

## Dependencies

- GCP2-003 (State schema for persistence)
