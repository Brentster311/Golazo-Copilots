# SFI-033 — Architect Decision Notes

## Architectural Decisions
1. **Phase 0 first** — Remove old LLM code before adding Copilot panel. Clean subtraction reduces noise in subsequent diffs.
2. **Single new module** — `copilot_panel.py` encapsulates all Copilot SDK interaction. No Copilot imports leak into app.py or dialogs.py.
3. **AsyncBridge as internal detail** — Lives inside `copilot_panel.py`, not exposed as a shared utility. If other modules need async later, it can be extracted.
4. **Stub preserves menu contract** — `_launch_llm_analysis(parent, item)` signature unchanged, just body replaced. Right-click menus in app.py and dialogs.py need no changes.
5. **Optional dependency** — `github-copilot-sdk` is optional. Panel detects import failure and shows instructions. No hard crash.

## Security Review
- Removing AzureCliCredential flow eliminates a credential surface
- Copilot SDK uses existing CLI token — no new secret storage
- No data sent to Azure OpenAI endpoints anymore

## No Blocking Issues
Design is architecturally sound. Proceed to developer role.

## Capability Registry Impact (gcp_capabilities)
5 capabilities affected by the changed files:

| Capability | Impact | Mitigation |
|---|---|---|
| **reporter-llm** | Directly affected — this capability IS being removed | Intentional — replaced by Copilot panel |
| **reporter-web-app** | Directly affected — Streamlit web UI | Separate codebase path; no shared LLM code with Tkinter app |
| **reporter-tk-app** | Transitively affected | Right-click menu preserved (stubbed); all other UI unchanged |
| **reporter-build** | Transitively affected | PyInstaller spec may need update to remove llm_client/llm_storage; add copilot_panel |
| **reporter-tests** | Transitively affected | LLM test files deleted; remaining tests must pass |
