# Design Doc — GCP-0063

## Summary
This change aligns Golazo execution policy and implementation with a role-based mode model:
- **Design roles** (POA, Program Manager, Domain Expert, Quality Assurance, Architect) run **inline** and may ask user questions.
- **Non-design roles** run as **subagents** by default.

The work scope includes approved fix items 1, 2, and 3 only:
1. Add missing `domain-expert.md` to bootstrap role list.
2. Add missing `domain-expert.md` to status deployed-to-source mapping.
3. Unify fallback policy documentation.

Rejected items (6, 7) remain out of scope.

## Problem statement
Current workflow behavior and documentation contain policy gaps and contradictions:
- Role list parity issue: `domain-expert` is part of workflow roles but absent in key deployment/mapping lists.
- Inconsistent fallback semantics between orchestrator and handoff docs.
- Clarification contract conflict: POA requires question-asking while subagent contract forbids asking questions.

These gaps make it unclear whether subagents are being used correctly and reduce confidence in deterministic role execution.

## Business case (why now, impact, KPIs)
### Why now
The project owner explicitly requested policy clarification and selected a concrete operating model by role.

### Impact
- Reduces ambiguity in early role execution.
- Preserves throughput in implementation/testing roles.
- Improves trust that instructions, tooling, and workflow state all agree.

### KPIs
- 100% role list parity for deployed role files vs workflow role set.
- 0 documented contradictions between orchestrator policy and handoff policy for fallback.
- Reduced clarification-related retries in design-phase roles (qualitative/observational initially).

## Stakeholders
- Project Owner
- Orchestrator agent operator (host Copilot)
- Role executors (inline and subagent pathways)
- Maintainers of Golazo instruction and MCP tooling

## Functional requirements
1. `domain-expert.md` must be included in bootstrap role-copy list.
2. `domain-expert.md` must be included in status deployed-source version map.
3. Documentation must define design roles as inline-only with question-asking permitted.
4. Documentation must define non-design roles as subagent-default.
5. Fallback policy must be consistent between orchestrator and handoff protocol docs.
6. Subagent no-question rule must be narrowed so it does not block inline design-role clarification.

## Non-functional requirements
- Maintain deterministic gate enforcement and transition integrity.
- Keep changes minimal and backward compatible with current profile sequencing.
- Preserve clear auditability in role notes and workflow artifacts.

## Proposed approach (high level)
### A) Python list parity fixes
- Update `DEFAULT_ROLES` in bootstrap tool to include `domain-expert.md`.
- Update `_DEPLOYED_TO_SOURCE` in status tool to include `domain-expert.md` mapping.

### B) Orchestration policy documentation alignment
- Update orchestrator instructions and handoff protocol to:
  - encode design-role inline policy,
  - encode non-design-role subagent default,
  - encode single consistent fallback behavior,
  - allow question-asking for inline roles.

### C) Scope guardrails
- Explicitly keep DoR wording refactor and extra regression-test work out of scope for this item.

## Alternatives considered
1. **Keep subagent-default for all roles**
   - Rejected: conflicts with PO requirement that design roles run inline.
2. **Switch to full multi-agent system**
   - Rejected: explicitly out of scope and unnecessary for sequential gated workflow.
3. **Inline-only for all roles**
   - Rejected: loses efficiency benefits for lower-ambiguity execution roles.

## Risks, mitigations, open questions
### Risks
- Drift between docs and future code updates may reintroduce policy mismatch.
- Role-mode policy may be interpreted differently if not centrally documented.

### Mitigations
- Keep policy stated in one canonical orchestrator instruction file and mirrored verbatim in handoff doc.
- Keep mapping/list parity synchronized with role order source of truth.

### Open questions
- None blocking for this work item; policy decisions were explicitly provided by project owner.

## Dependencies
- Existing role files under `.github/agents/golazo-copilot/roles/`.
- Tooling modules:
  - `golazo_bootstrap.py`
  - `golazo_status.py`
- Instruction docs:
  - `.github/agents/Golazo-Copilot.md`
  - `WorkItems/Golazo-Subagent-Handoff-Protocol.md`

## Migration / rollout / rollback plan
### Rollout
1. Apply targeted doc and Python-list updates.
2. Validate transitions still pass with required outputs.
3. Confirm status/version mapping now includes `domain-expert.md`.

### Rollback
- Revert changed docs and list entries if policy causes workflow regressions.

## Observability plan
- Use `golazo_status` to verify role progression and required outputs.
- Observe whether design roles now complete with fewer clarification loops.
- Track any fallback invocations and whether behavior matches selected policy.

## Test strategy summary
- Validate static list coverage (manual/assertion-based) for bootstrap and status mappings.
- Validate docs contain aligned policy statements (manual grep or content checks).
- Execute targeted workflow steps (POA → PM → DE) to verify practical role-mode intent is clear and actionable.
