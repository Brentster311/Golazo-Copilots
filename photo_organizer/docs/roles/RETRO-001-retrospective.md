# Retrospective: RETRO-001

## Trigger
**Process Violation**: Project Owner Assistant made an assumption about CLI vs GUI interface without asking the user, despite this being a fundamental UX decision with clear ambiguity.

## Evidence

### What Happened
1. User requested: "easy way to view photos"
2. Project Owner Assistant created assumption: `Assumption (explicit): Simple GUI using tkinter`
3. User was never asked about interface preference (CLI vs GUI)
4. Entire workflow completed with wrong assumption baked in

### Rule That Should Have Applied
From `.github/roles/project-owner-assistant.md`:
> "If ambiguity exists, ask targeted questions; otherwise propose Assumption (explicit) defaults."

### Why It Failed
The word "otherwise" is ambiguous. It was interpreted as "if I can make a reasonable guess" rather than "if asking is not feasible."

---

## Root Cause Analysis

| Factor | Description |
|--------|-------------|
| **Ambiguous instruction** | "otherwise" doesn't clearly define when to ask vs assume |
| **Missing classification** | No guidance on which decisions are "must-ask" vs "can-assume" |
| **Speed over correctness** | Prioritized completing the workflow over validating requirements |

---

## Proposed Changes

### Change 1: Clarify the decision rule in `project-owner-assistant.md`

**Current text:**
```markdown
## Decision rules
- Prefer smaller scope that is shippable and testable.
- If ambiguity exists, ask targeted questions; otherwise propose **Assumption (explicit)** defaults.
```

**Proposed text:**
```markdown
## Decision rules
- Prefer smaller scope that is shippable and testable.
- If ambiguity exists:
  1. **MUST ASK** for fundamental decisions (interface type, target platform, data persistence, security model)
  2. **MAY ASSUME** for implementation details (specific libraries, internal naming, folder structure)
  3. When assuming, label clearly as **Assumption (explicit)** and explain why asking wasn't required
- Never assume user interface type (CLI, GUI, web, API) - always ask.
```

### Change 2: Add "Must-Ask Checklist" to `project-owner-assistant.md`

**Add new section:**
```markdown
## Must-Ask Checklist (never assume these)

Before creating a user story, confirm the following with the user if not explicitly stated:

- [ ] **Interface type**: CLI, GUI, web, API, or library?
- [ ] **Target platform**: Windows, Mac, Linux, cross-platform?
- [ ] **Data persistence**: Files, database, cloud, or in-memory only?
- [ ] **User type**: Technical (developers) or non-technical (end users)?

If any of these are ambiguous, STOP and ask before proceeding.
```

---

## Suggested Diff for `.github/roles/project-owner-assistant.md`

```diff
 ## Decision rules
 - Prefer smaller scope that is shippable and testable.
-- If ambiguity exists, ask targeted questions; otherwise propose **Assumption (explicit)** defaults.
+- If ambiguity exists:
+  1. **MUST ASK** for fundamental decisions (interface type, target platform, data persistence, security model)
+  2. **MAY ASSUME** for implementation details (specific libraries, internal naming, folder structure)
+  3. When assuming, label clearly as **Assumption (explicit)** and explain why asking wasn't required
+- Never assume user interface type (CLI, GUI, web, API) - always ask.
 - A request is too large if it contains more than one user-observable outcome.
+
+## Must-Ask Checklist (never assume these)
+
+Before creating a user story, confirm the following with the user if not explicitly stated:
+
+- [ ] **Interface type**: CLI, GUI, web, API, or library?
+- [ ] **Target platform**: Windows, Mac, Linux, cross-platform?
+- [ ] **Data persistence**: Files, database, cloud, or in-memory only?
+- [ ] **User type**: Technical (developers) or non-technical (end users)?
+
+If any of these are ambiguous, STOP and ask before proceeding.
```

---

## Action Items

1. **Apply the proposed changes** to `.github/roles/project-owner-assistant.md`
2. **Restart WIP-001** with proper requirements gathering (ask about GUI)
3. **Update existing artifacts** to reflect correct requirements

---

## Prevention

With these changes, the next time a user says "easy way to view photos", the Project Owner Assistant will:
1. Check the Must-Ask Checklist
2. See "Interface type" is not specified
3. STOP and ask: "Would you like CLI, GUI, or both?"

This prevents the entire workflow from proceeding with invalid assumptions.
