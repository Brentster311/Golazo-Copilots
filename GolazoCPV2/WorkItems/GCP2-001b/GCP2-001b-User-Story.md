# GCP2-001b: Consent-Based Enforcement

**Status**: BACKLOG  
**Priority**: High  
**Size**: M  
**Created**: 2026-01-27  
**Parent**: GCP2-001

---

## User Story

- **Title**: Consent-Based Enforcement
- **As a**: Developer using Golazo V2
- **I want**: The agent to only skip roles when I explicitly request it
- **So that**: I maintain control over workflow deviations and the agent never skips autonomously

- **Out of scope**:
  - State machine logic (GCP2-001a)
  - Protocol/CLI commands (GCP2-001c)
  - Copilot/MCP integration (GCP2-001d)
  - Natural language understanding via LLM (pattern matching only for MVP)

- **Assumptions**:
  - **Assumption (explicit)**: Skip detection uses keyword/phrase matching, not LLM inference
  - **Assumption (explicit)**: Audit log stored in state.json `deviations` array
  - **Assumption (explicit)**: User's exact words captured as reason for audit trail

- **Acceptance Criteria**:
  - [ ] `ConsentEnforcer` class detects explicit skip requests from user messages
  - [ ] Ambiguous requests (e.g., "just fix it") trigger clarification prompt
  - [ ] All skips confirmed back to user with list of roles being skipped
  - [ ] Warning shown when skipping quality gates (Tester, Architect)
  - [ ] All deviations logged with timestamp, role, and user's exact words
  - [ ] `get_deviations()` returns audit trail from state file
  - [ ] Agent takes no action until clarification is received for ambiguous requests

- **Non-functional requirements**:
  - Skip detection must be deterministic (same input → same output)
  - Pattern matching must be case-insensitive
  - Audit log must be append-only (no deletion of deviation records)

- **Telemetry / metrics expected**:
  - None for MVP

- **Rollout / rollback notes**:
  - Core enforcement mechanism; must be stable before Copilot integration

---

## API Design

```python
class ConsentEnforcer:
    def __init__(self, state_machine: GolazoStateMachine):
        """Initialize with state machine reference."""
    
    def analyze_request(self, user_message: str) -> RequestAnalysis:
        """Analyze user message for skip intent."""
    
    def get_clarification_prompt(self, analysis: RequestAnalysis) -> str:
        """Generate clarification prompt for ambiguous requests."""
    
    def process_skip_request(self, roles_to_skip: list[str], reason: str) -> SkipResult:
        """Process explicit skip request. Logs deviation."""
    
    def get_deviations(self) -> list[Deviation]:
        """Return all logged deviations for current work item."""

@dataclass
class RequestAnalysis:
    type: str  # 'normal', 'explicit_skip', 'ambiguous', 'profile_select'
    detected_skips: list[str]
    suggested_action: str  # 'proceed', 'clarify', 'confirm_skip'
```

---

## Skip Detection Patterns

### Explicit Skip (Allow)
- "Skip the architect role"
- "I don't need a design doc"
- "Skip to developer"
- "Use express mode"
- "Fast-track this"

### Ambiguous (Clarify)
- "Just fix this"
- "Quick fix"
- "This is simple"
- "Don't need all that"

### Normal (Proceed with workflow)
- "Add a null check to GetUser"
- "Fix the bug in line 42"

---

## Dependencies

- GCP2-001a (State machine for transitions)
- GCP2-003 (State schema for audit log storage)
- "This is simple"
- "Don't need all that"

### Normal (Proceed with workflow)
- "Add a null check to GetUser"
- "Fix the bug in line 42"
- "Implement the new feature"

## Out of Scope

- State machine logic (GCP2-001a)
- Protocol/CLI (GCP2-001c)
- Copilot integration (GCP2-001d)

## Dependencies

- GCP2-001a (State machine for transitions)
- GCP2-003 (State schema for audit log storage)

## Technical Notes

- Pattern matching for common skip phrases
- May use LLM for nuanced intent detection (optional enhancement)
- Audit log stored in `state.json` under `deviations` array
