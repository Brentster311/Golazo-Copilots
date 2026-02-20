# GCP-0045 User Story

**Status**: IMPLEMENTED

**User Story**

- **Title**: Add Golazo Workflow Trigger Phrase Recognition to Copilot Instructions
- **As a**: Golazo Copilot user
- **I want**: The copilot-instructions.md to contain explicit trigger-phrase rules so the AI immediately calls `gcp_create_workitem` when I say "new workitem", "new work item", provide a work-item ID pattern (e.g., `YYY-XXX`), or say "complete mode"
- **So that**: The Golazo workflow starts on the first message without requiring me to repeat myself, eliminating wasted cycles and maintaining process confidence

- **Out of scope**:
  - Changes to the MCP server or Python codebase
  - Changes to role files or gate logic
  - Any new MCP tools or API changes
  - Handling ambiguous partial matches (e.g., the word "item" alone)

- **Assumptions**:
  - **Assumption (explicit)**: Interface type is the `.github/copilot-instructions.md` file — this is an instruction-file change, not a code change. Obvious from the nature of the request.
  - **Assumption (explicit)**: Target platform is cross-platform (VS Code on any OS). The instructions file is platform-agnostic markdown.
  - **Assumption (explicit)**: Data persistence is file-based (editing an existing markdown file). No database or cloud involved.
  - **Assumption (explicit)**: The trigger phrases are case-insensitive from the AI's perspective (natural language matching, not regex).
  - **Assumption (explicit)**: The work-item ID pattern `YYY-XXX` refers to the existing pattern `^[A-Za-z]{1,4}-\d{3,}$` already defined in the project-owner-assistant role file.

- **Acceptance Criteria (bulleted, testable)**:
  - A new clearly-labeled section exists in `.github/copilot-instructions.md` that lists the trigger phrases ("new workitem", "new work item", a recognized work-item ID pattern, "complete mode") and instructs the AI to IMMEDIATELY call `gcp_create_workitem` without asking for confirmation
  - The section is placed in a high-visibility location (before or near the "REQUIRED: Before EVERY Response" section) so the AI processes it early in its instruction set
  - The instruction explicitly states "Do not ask for confirmation" to prevent the failure mode observed in the retrospective
  - The existing copilot-instructions content is preserved — no functional regressions to other sections

- **Non-functional requirements**:
  - Instructions must be concise and unambiguous so the AI can parse them reliably
  - Must not conflict with any existing FORBIDDEN ACTIONS or gate enforcement rules

- **Telemetry / metrics expected**:
  - Success = zero "repeated ask" cycles when a user provides a trigger phrase in a new conversation
  - Manual validation: test by starting a fresh chat and saying "new workitem: <description>"

- **Rollout / rollback notes**:
  - Rollout: Merge updated `copilot-instructions.md` — takes effect immediately on next chat session
  - Rollback: Revert the added section from `copilot-instructions.md`

---

## Retrospective Context (Motivation)

From a retrospective on another project:

> **CRITICAL: Failure to Recognize Golazo Workflow Trigger**
>
> Issue: When the user said "new workitem: when I hit the trends button…" and "this will be CVT-002 btw", I did NOT initiate the Golazo workflow. The user had to ask THREE times before I started the proper gcp_create_workitem flow.
>
> Root cause: I treated the user's message as an ad-hoc feature request rather than recognizing the explicit "new workitem" and "CVT-002" cues as a Golazo workflow trigger.
>
> Impact: Wasted 3 message cycles. Eroded user confidence in process adherence.

**Required fix — Trigger phrases**: When the user says "new workitem", "new work item", provides a `<workitemid>` matching `YYY-XXX` pattern, or says "complete mode", IMMEDIATELY call `gcp_create_workitem`. Do not ask for confirmation.
