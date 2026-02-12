# SFI-033 — Project Owner Assistant Decision Notes

## Scope Decision
Single story — the work has one user-observable outcome: the LLM config button becomes a Copilot chat panel toggle. The "Analyze with LLM" stub is a minor change bundled in because it's directly downstream of removing the old LLM config.

## Key Decisions
1. **Keep `llm_client.py` and `llm_extender/`** — These will be re-integrated in a future story when Copilot-powered analysis replaces the Azure OpenAI pipeline. Removing them now would be wasteful churn.
2. **Stub the right-click analysis** — Rather than removing the menu items (which users know about), show "not yet implemented" so users know the feature is being reworked.
3. **Reference ghcpsdk template** — The `AsyncBridge` + `CopilotClient` + streaming pattern is proven and maps cleanly to a side panel widget.
4. **Must-ask checklist**: Interface=Tkinter GUI, Platform=Windows, Persistence=none new, User=technical — all inherited from existing app context.
