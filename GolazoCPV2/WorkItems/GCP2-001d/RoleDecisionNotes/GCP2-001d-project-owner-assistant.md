# GCP2-001d: Project Owner Assistant Decision Notes

**Work Item**: GCP2-001d - Copilot/MCP Integration  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **MCP tools as integration method**: Model Context Protocol provides:
   - Standard way for Copilot to call external tools
   - Structured request/response format
   - Clear tool descriptions that guide Copilot behavior

2. **Tool descriptions are critical**: The tool description text directly influences how Copilot decides when to call each tool.

3. **Blocking responses for unauthorized skips**: When Copilot tries to skip without consent, the tool returns a "denied" status that guides Copilot to ask the user.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| Prompt engineering only | V1 approach; unreliable enforcement |
| Custom Copilot extension | More complex than MCP tools |

---

## Tradeoffs Accepted

- **Dependent on MCP support**: If MCP changes, integration may need updates.

---

## Known Limitations

- Tool descriptions may need tuning based on Copilot behavior
- Multi-turn consent flows may be awkward via tools

---

## Must-Ask Checklist Responses

- **Interface type**: MCP tools
- **Target platform**: GitHub Copilot environment
- **Data persistence**: Via GCP2-003 state files
- **User type**: Technical (developers using Copilot)
