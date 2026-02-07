# GCP-0002: Role Transitions

**Status**: IMPLEMENTED

## User Story

**As a** developer using Golazo Copilot,  
**I want to** transition between workflow roles by saying "Move to [role]",  
**So that** I can progress through the workflow with validated state changes.

---

## Acceptance Criteria

### AC1: MCP Tool `gcp_transition` Changes Role
- [ ] Calling `gcp_transition({ role: "program-manager" })` from `project-owner`:
  - Updates `currentRole` to "program-manager"
  - Closes previous role in `roleHistory` (sets `exitedAt`)
  - Adds new entry to `roleHistory` with `enteredAt`, `exitedAt: null`
  - Updates `updatedAt` timestamp
  - Saves state to `state.json`
- [ ] Returns success with new role instructions

### AC2: Transition Validation (Allowed Transitions)
- [ ] Only valid transitions are allowed based on workflow:
  ```
  project-owner -> program-manager
  program-manager -> quality-assurance
  quality-assurance -> architect
  architect -> developer (requires DoR complete)
  developer -> refactor-expert
  refactor-expert -> builder
  builder -> documentor
  documentor -> (complete)
  ```
- [ ] Invalid transitions return error:
  - `"Cannot transition from 'project-owner' to 'developer'. Must go through program-manager, quality-assurance, architect first."`

### AC3: DoR Gate Enforcement
- [ ] Transition to `developer` blocked if DoR incomplete:
  - Returns: `{ success: false, error: "DoR must be complete before Development phase", missing: ["testCases"] }`
- [ ] Lists which DoR items are missing
- [ ] Suggests: "Complete missing items or use gcp_consent to record deviation"

### AC4: Phase Transitions
- [ ] Transitions update `currentPhase` when crossing phase boundaries:
  - `definition` phase: project-owner, program-manager, quality-assurance, architect
  - `development` phase: developer, refactor-expert, builder
  - `completion` phase: documentor
- [ ] Phase stored in state for quick reference

### AC5: Role Instructions Returned
- [ ] Successful transition returns new role's instruction content
- [ ] Instructions loaded from:
  1. Local `.github/roles/{role}.md` if exists
  2. Default from `golazo-copilot` package

### AC6: Backward Transitions (Rework)
- [ ] Backward transitions allowed with warning:
  - `gcp_transition({ role: "architect" })` from `developer`
  - Returns: `{ success: true, warning: "Moving backward to rework. Previous progress preserved." }`
- [ ] Does NOT reset DoR/DoD items (preserves progress)

---

## Technical Notes

### MCP Tool Definition
```typescript
{
  name: "gcp_transition",
  description: "Transition to a new role in the Golazo Copilot workflow",
  inputSchema: {
    type: "object",
    properties: {
      role: {
        type: "string",
        enum: ["project-owner", "program-manager", "quality-assurance", 
               "architect", "developer", "refactor-expert", "builder", "documentor"],
        description: "Target role to transition to"
      },
      force: {
        type: "boolean",
        default: false,
        description: "Force transition even if gates not met (requires prior consent)"
      }
    },
    required: ["role"]
  }
}
```

### Transition Matrix
```typescript
const TRANSITIONS: Record<string, string[]> = {
  "project-owner": ["program-manager"],
  "program-manager": ["quality-assurance", "project-owner"],
  "quality-assurance": ["architect", "program-manager"],
  "architect": ["developer", "quality-assurance"],  // developer requires DoR
  "developer": ["refactor-expert", "architect"],
  "refactor-expert": ["builder", "developer"],
  "builder": ["documentor", "refactor-expert"],
  "documentor": ["builder"]  // can go back for fixes
};
```

### Response Schema
```typescript
interface TransitionResponse {
  success: boolean;
  error?: string;
  missing?: string[];  // DoR/DoD items if gate blocked
  warning?: string;    // For backward transitions
  currentRole: string;
  currentPhase: string;
  roleInstructions: string;  // Markdown content
}
```

---

## Dependencies

- **GCP-0001**: Requires initialized work item with state.json

---

## Out of Scope

- DoR/DoD marking (GCP-0003)
- Consent/deviation recording for forced transitions (GCP-0005)
- Custom transition rules via gcp.yaml (GCP-0008)

---

## Definition of Ready Checklist

- [ ] User Story document exists (this file)
- [ ] Design Doc exists
- [ ] Review Comments from QA and Architect exist
- [ ] Test Cases document exists

## Definition of Done Checklist

- [ ] Feature branch created
- [ ] Test code written before production code
- [ ] All automated tests pass
- [ ] Build passes
- [ ] Docs updated
- [ ] Refactor pass complete
- [ ] Changes committed
