# GCP-0059 QA Review Comments

## Overall Assessment
- Design is implementable and aligned to the story objective of standardizing bootstrap outputs under `.github/agents/golazo-copilot`.
- The critical path contract is mostly clear and testable:
  - Spine file: `.github/agents/golazo-copilot/orchestrator.md`
  - Roles folder: `.github/agents/golazo-copilot/roles/...`

## Strengths
- Functional requirements map directly to observable filesystem outcomes.
- Non-functional requirements include idempotency, error quality, and compatibility constraints.
- Test strategy summary in design aligns with required behavior toggles (`include_roles=true|false`).

## Blocking Clarification to Fix Before/With Implementation
1. **Filename contradiction in the design doc**
   - The design alternatives section says: "requirement is explicit that spine must be `golazo-copilot.md`".
   - User story and functional requirements explicitly require `orchestrator.md`.
   - QA decision: treat `.github/agents/golazo-copilot/orchestrator.md` as authoritative and correct design wording to remove ambiguity.

## Architect Notes
- Authoritative output contract for this work item is:
  - `.github/agents/golazo-copilot/orchestrator.md`
  - `.github/agents/golazo-copilot/roles/...`
- Resolved stale references to legacy/incorrect targets for implementation planning and validation:
  - Replace any `golazo-copilot.md` mention with `orchestrator.md`.
  - Replace any `.github/roles/...` destination references with `.github/agents/golazo-copilot/roles/...`.
- Scope lock (architect decision): bootstrap output path and naming changes only; no role-content/semantic changes and no unrelated production behavior changes.
- Contract enforcement guidance:
  - Use explicit constants for agents root, spine path, and roles path.
  - Validate both positive creation paths and negative assertions for legacy paths in the same run.

## Quality Gaps / Recommendations
1. Add explicit assertions that **legacy spine path is not created/updated** in the same run where new path is valid.
2. Add explicit error taxonomy checks for path-resolution failure vs write failure vs copy failure (per telemetry expectations).
3. Validate idempotency with repeated bootstrap runs and stable content for unchanged artifacts.
4. Validate docs/help text for exact literals (folder and filename), including no stale references to legacy paths.

## Risk-Focused Testability Notes
- Path normalization/casing risks should be covered with path-join based assertions (not hard-coded separators).
- Permission/IO failures must verify actionable, deterministic messages and no partial artifacts.
- Role copy toggle must verify both positive creation and negative non-creation behavior.

## Handoff Guidance (Architect/Developer)
- Use single-source constants/helpers for output contracts:
  - `agents_root = .github/agents/golazo-copilot`
  - `spine = agents_root/orchestrator.md`
  - `roles = agents_root/roles`
- Keep behavior backward compatible for options while updating only path/filename contracts.
- Ensure docs and tests ship in the same change to prevent contract drift.
