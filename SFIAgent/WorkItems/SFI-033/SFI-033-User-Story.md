# SFI-033: Replace LLM Explorer with GitHub Copilot Chat Side Panel

**Status**: IN PROGRESS

## User Story
- **Title**: Replace LLM Explorer with GitHub Copilot Chat Side Panel
- **As a**: SFI Reporter user (manager or IC)
- **I want**: a side panel chat interface powered by GitHub Copilot SDK that replaces the current Azure OpenAI LLM configuration and analysis workflow
- **So that**: I can interact with a Copilot-powered chat assistant directly within SFI Reporter without needing to configure Azure OpenAI endpoints

## Out of Scope
- Full Copilot-powered analysis of action items (the "Analyze with LLM" right-click will show "not yet implemented" placeholder)
- Chat history persistence between sessions
- Multiple simultaneous chat sessions

## Assumptions
- **Confirmed**: The "open"/"LLM" button is always enabled. When clicked, the panel checks for `github-copilot-sdk` and Copilot CLI availability. If either is missing, the panel displays instructions to the user (e.g., "Install github-copilot-sdk" or "Run `copilot auth login`") rather than crashing.
- **Confirmed**: The ghcpsdk app at `C:\...\ghcpsdk\app.py` serves as the reference implementation for Copilot SDK integration (AsyncBridge pattern, CopilotClient, session management, streaming).
- **Confirmed**: The side panel matches the existing SFI Reporter system/light theme rather than the dark theme from ghcpsdk.

## Acceptance Criteria
- [ ] The "⚙️ Configure LLM" toolbar button is replaced with an "open" / "LLM" split label button that toggles the Copilot chat side panel
- [ ] Clicking the button opens a right-side panel containing a Copilot chat interface (input bar, chat display, model selector, connection status)
- [ ] The side panel has its own close button (X) that hides the panel
- [ ] The "🤖 Analyze with LLM" right-click menu items (KPI tree and detail modal) remain but show a messagebox with "Not yet implemented" when clicked
- [ ] The `ConfigureLLMDialog` is no longer launched from anywhere in the UI
- [ ] The `llm_client.py` module is removed
- [ ] The `llm_extender/` module is removed
- [ ] All references to `ConfigureLLMDialog`, `LLMConfig`, `AnalysisResult`, `analyze_item`, `fetch_action_item_urls`, and related imports are cleaned up
- [ ] The Copilot chat panel uses the AsyncBridge pattern from ghcpsdk for non-blocking SDK communication
- [ ] All existing SFIReporter tests that don't test removed LLM code continue to pass

## Non-functional Requirements
- Side panel must not block the main Tkinter event loop during Copilot SDK calls
- Panel show/hide should be instant with no layout jank

## Telemetry / Metrics Expected
- None (desktop app, no telemetry)

## Rollout / Rollback Notes
- New dependency: `github-copilot-sdk` added to pyproject.toml
- Rollback: Copilot panel can be reverted independently; `llm_client.py`, `llm_extender/`, and `ConfigureLLMDialog` removal is permanent and not rolled back
