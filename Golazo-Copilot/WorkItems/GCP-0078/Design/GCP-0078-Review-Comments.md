# GCP-0078 Review Comments

## Decision

Approved. The design addresses every material finding from the README truth audit without broadening into runtime workflow changes.

## Risks and Mitigations

- **Planner ambiguity:** Explain that Planner belongs to Complete but new state currently starts at Project Owner Assistant; do not imply users begin in Planner.
- **Bypass ambiguity:** Distinguish supported output-gate bypass from the unavailable public role-note bypass.
- **Git overstatement:** Separate MCP proposal recording from agent-executed Git commands and enumerate unsupported automation concisely.
- **Brittle tests:** Assert contract-bearing phrases and source-derived role/tool facts, not full paragraphs.

## Workflow Note

Express transitions directly from POA to QA while QA instructions expect a Program Manager design artifact. Program Manager is unavailable in this profile, so the accompanying minimal design records the documentation-only implementation directly.
