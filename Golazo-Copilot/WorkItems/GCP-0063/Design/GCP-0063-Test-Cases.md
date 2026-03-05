# Test Cases — GCP-0063

## Coverage Mapping
Acceptance criteria are referenced as AC1..AC5 from the user story.

### AC1 — `domain-expert.md` included in bootstrap role-copy list
1. **TC-AC1-1 (Static list membership)**
   - Precondition: Source available.
   - Steps: Open `golazo_bootstrap.py`; inspect `DEFAULT_ROLES`.
   - Expected: `domain-expert.md` is present exactly once.
   - Failure message: "DEFAULT_ROLES missing domain-expert.md"

### AC2 — `domain-expert.md` included in status deployed-to-source mapping
2. **TC-AC2-1 (Static mapping membership)**
   - Steps: Open `golazo_status.py`; inspect `_DEPLOYED_TO_SOURCE`.
   - Expected: mapping entry exists for `.github/agents/golazo-copilot/roles/domain-expert.md` -> `golazo_copilot.roles.defaults/domain-expert.md`.
   - Failure message: "_DEPLOYED_TO_SOURCE missing domain-expert mapping"

### AC3 — Docs state design roles inline and question-enabled
3. **TC-AC3-1 (Orchestrator doc policy check)**
   - Steps: Inspect `.github/agents/Golazo-Copilot.md`.
   - Expected: Explicit statement that POA/PM/DE/QA/Architect run inline and may ask user questions.
   - Failure message: "Design-role inline/question policy missing or incomplete"

4. **TC-AC3-2 (Handoff protocol policy check)**
   - Steps: Inspect `WorkItems/Golazo-Subagent-Handoff-Protocol.md`.
   - Expected: Same design-role inline/question policy appears consistently.
   - Failure message: "Handoff protocol lacks aligned design-role inline policy"

### AC4 — Docs state non-design roles subagent-default
5. **TC-AC4-1 (Role matrix consistency)**
   - Steps: Inspect orchestrator + handoff docs.
   - Expected: Developer/Refactor/Documenter/Builder default to subagent execution.
   - Failure message: "Non-design subagent-default policy missing or contradictory"

### AC5 — Contradictory POA question-blocking wording removed/narrowed
6. **TC-AC5-1 (Question-policy conflict check)**
   - Steps: Inspect orchestrator and handoff docs for no-question rules.
   - Expected: no-question rule is scoped to subagent roles; inline design roles remain question-enabled.
   - Failure message: "Question policy still blocks POA or inline design-role clarifications"

## Negative/Regression Tests
7. **TC-REG-1 (Out-of-scope unchanged)**
   - Steps: Verify no introduced requirements for DoR model reintroduction or added regression-test initiative beyond story scope.
   - Expected: Implementation remains limited to approved fixes 1,2,3.

## Execution Notes
- These are design-level verification tests; implementation-phase checks should rerun all AC tests after code/doc edits.
