# GCP-0008: Workflow Profiles

## User Story

**As a** developer with varying workflow needs,  
**I want to** choose between different workflow profiles (complete, express, spike),  
**So that** I can match process rigor to the task at hand.

---

## Acceptance Criteria

### AC1: Profile Selection at Init
- [ ] `gcp_init({ workItemId: "feature-x", profile: "complete" })` sets profile
- [ ] `gcp_init({ workItemId: "bugfix", profile: "express" })` for lighter workflow
- [ ] `gcp_init({ workItemId: "spike", profile: "spike" })` for exploration
- [ ] Default profile: "complete"

### AC2: Complete Profile (Full Workflow)
- [ ] All roles required in sequence:
  ```
  project-owner -> program-manager -> quality-assurance -> architect ->
  developer -> refactor-expert -> builder -> documentor
  ```
- [ ] All DoR items required before development:
  - userStory, designDoc, reviewComments, testCases
- [ ] All DoD items tracked:
  - branchCreated, testsWrittenFirst, testsPass, buildPasses, 
    docsUpdated, refactorComplete, committed

### AC3: Express Profile (Reduced Gates)
- [ ] Streamlined role sequence:
  ```
  project-owner -> architect -> developer -> builder
  ```
- [ ] Reduced DoR (optional reviewComments):
  - userStory, designDoc, testCases (reviewComments optional)
- [ ] Reduced DoD:
  - testsPass, buildPasses, committed

### AC4: Spike Profile (Minimal Process)
- [ ] Minimal roles:
  ```
  developer -> builder
  ```
- [ ] No DoR gate (can start coding immediately)
- [ ] Minimal DoD:
  - buildPasses (just needs to compile/run)
- [ ] Warning on init: "Spike profile has minimal gates. Use for exploration only."

### AC5: Profile Affects Transition Validation
- [ ] `gcp_transition` validates against profile's role sequence
- [ ] Skipping roles in express/spike doesn't require consent
- [ ] Complete profile enforces full sequence

### AC6: Profile Affects Gate Enforcement
- [ ] DoR gate only blocks if profile requires it
- [ ] DoD items only tracked if profile includes them

### AC7: Profile Visible in Status
- [ ] `gcp_status()` shows active profile:
  ```json
  {
    "profile": "express",
    "profileDescription": "Reduced gates for smaller changes",
    "gates": {
      "dorRequired": true,
      "dodItems": ["testsPass", "buildPasses", "committed"]
    }
  }
  ```

### AC8: Profile Cannot Change After Init
- [ ] Profile is set at work item creation
- [ ] Attempting to change profile returns error:
  - "Profile cannot be changed after initialization. Create a new work item if different profile needed."
- [ ] Rationale: Changing mid-stream would invalidate workflow state

### AC9: Custom Profiles via gcp.yaml (Future-Ready)
- [ ] Schema supports custom profiles:
  ```yaml
  profiles:
    custom-light:
      roles: [project-owner, developer, builder]
      dor: [userStory]
      dod: [testsPass, committed]
  ```
- [ ] NOTE: Custom profile loading is future scope, but schema ready

---

## Technical Notes

### Profile Definitions
```typescript
interface WorkflowProfile {
  name: string;
  description: string;
  roles: string[];
  transitions: Record<string, string[]>;
  dor: {
    required: string[];
    optional: string[];
  };
  dod: {
    required: string[];
    optional: string[];
  };
  gates: {
    dorRequired: boolean;
    dodRequired: boolean;
  };
}

const PROFILES: Record<string, WorkflowProfile> = {
  complete: {
    name: "complete",
    description: "Full Golazo Copilot workflow with all gates",
    roles: ["project-owner", "program-manager", "quality-assurance", "architect",
            "developer", "refactor-expert", "builder", "documentor"],
    transitions: {
      "project-owner": ["program-manager"],
      "program-manager": ["quality-assurance"],
      // ... full matrix
    },
    dor: {
      required: ["userStory", "designDoc", "reviewComments", "testCases"],
      optional: []
    },
    dod: {
      required: ["branchCreated", "testsWrittenFirst", "testsPass", 
                 "buildPasses", "docsUpdated", "refactorComplete", "committed"],
      optional: []
    },
    gates: { dorRequired: true, dodRequired: true }
  },
  
  express: {
    name: "express",
    description: "Reduced gates for smaller changes",
    roles: ["project-owner", "architect", "developer", "builder"],
    transitions: {
      "project-owner": ["architect"],
      "architect": ["developer"],
      "developer": ["builder"],
      "builder": []
    },
    dor: {
      required: ["userStory", "designDoc", "testCases"],
      optional: ["reviewComments"]
    },
    dod: {
      required: ["testsPass", "buildPasses", "committed"],
      optional: []
    },
    gates: { dorRequired: true, dodRequired: true }
  },
  
  spike: {
    name: "spike",
    description: "Minimal process for exploration",
    roles: ["developer", "builder"],
    transitions: {
      "developer": ["builder"],
      "builder": []
    },
    dor: {
      required: [],
      optional: ["userStory"]
    },
    dod: {
      required: ["buildPasses"],
      optional: []
    },
    gates: { dorRequired: false, dodRequired: false }
  }
};
```

### Profile-Aware Validation
```typescript
function canTransition(state: WorkItemState, targetRole: string): ValidationResult {
  const profile = PROFILES[state.profile];
  
  // Check if role exists in profile
  if (!profile.roles.includes(targetRole)) {
    return { 
      allowed: false, 
      reason: `Role '${targetRole}' not available in ${profile.name} profile` 
    };
  }
  
  // Check if transition is valid for profile
  const allowedTransitions = profile.transitions[state.currentRole];
  if (!allowedTransitions.includes(targetRole)) {
    return { 
      allowed: false, 
      reason: `Cannot transition from ${state.currentRole} to ${targetRole} in ${profile.name} profile`
    };
  }
  
  // Check DoR gate if crossing to development
  if (profile.gates.dorRequired && isDevelopmentRole(targetRole)) {
    if (!isDoRComplete(state, profile)) {
      return {
        allowed: false,
        reason: "DoR must be complete",
        missing: getMissingDoR(state, profile)
      };
    }
  }
  
  return { allowed: true };
}
```

---

## Dependencies

- **GCP-0001**: Profile set at init
- **GCP-0002**: Profile affects transition validation
- **GCP-0003**: Profile affects which DoR/DoD items are tracked

---

## Out of Scope

- Loading custom profiles from gcp.yaml (Future work item)
- Profile migration (changing profile mid-flight) (Not planned)

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
