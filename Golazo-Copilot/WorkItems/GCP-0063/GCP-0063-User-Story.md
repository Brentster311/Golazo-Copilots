**Status**: IMPLEMENTED

**User Story**
- Title: Align Golazo execution mode by role and close subagent policy gaps
- As a: Project owner
- I want: the workflow instructions and code paths to enforce that design roles run inline (and may ask questions), while non-design roles default to subagents
- So that: ambiguous design decisions are handled interactively and implementation roles remain efficient with delegated execution
- Out of scope:
  - Introducing a parallel multi-agent swarm architecture
  - Re-introducing explicit DoR/DoD state objects
  - Enabling design-role execution as subagents by default
- Assumptions:
  - Assumption (explicit): This work item maps to prior fix list items where 1, 2, 3 are approved, 6 and 7 are rejected.
  - Assumption (explicit): Design roles are exactly POA, Program Manager, Domain Expert, Quality Assurance, and Architect.
  - Assumption (explicit): "Inline roles are permitted to ask questions" applies only to inline roles.
- Acceptance Criteria (bulleted, testable):
  - `domain-expert.md` is included in both bootstrap role-copy list and status deployed-to-source mapping.
  - Orchestrator and handoff docs use one consistent fallback policy for subagent failures.
  - Documentation explicitly states: POA, PM, DE, QA, Architect run inline and may ask user questions.
  - Documentation explicitly states: non-design roles run as subagents by default.
  - Contradictory wording that blocks POA clarification questions is removed or narrowed to subagent roles only.
- Non-functional requirements:
  - Preserve deterministic gate enforcement and transition integrity.
  - Keep changes minimal and backward compatible with current workflow profile logic.
- Telemetry / metrics expected:
  - Reduced mid-role clarification failures on design phases.
  - Reduced gate retry loops caused by missing clarification in early roles.
- Rollout / rollback notes:
  - Rollout by updating instruction docs and targeted Python mappings.
  - Rollback by restoring previous docs and list entries if policy causes regressions.

## Closure

- Summary of what was delivered:
  - Added `domain-expert.md` to bootstrap role copy list.
  - Added `domain-expert.md` to status deployed-source mapping.
  - Unified role execution and fallback policy wording across orchestrator/handoff/bootstrap instruction surfaces.
- Acceptance criteria pass/fail status:
  - AC1: PASS
  - AC2: PASS
  - AC3: PASS
  - AC4: PASS
  - AC5: PASS
- Future work items:
  - Consider a follow-up work item to modularize `golazo_status.py` based on refactor audit recommendation.
  - Consider a follow-up work item to add policy parity checks across orchestrator/handoff/bootstrap docs.
- Final status confirmation:
  - Implemented and closed for approved scope (items 1, 2, 3). Rejected items (6, 7) were not implemented as part of this work item.
