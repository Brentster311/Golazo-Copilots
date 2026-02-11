**Status**: IN PROGRESS

**User Story**
- Title: Copilot SDK Tkinter Chat App
- As a: Developer with a GitHub Copilot subscription
- I want: A Python Tkinter desktop app that connects to the GitHub Copilot SDK, lets me type a prompt, and displays the streaming response in a chat window
- So that: I can interactively send prompts to GitHub Copilot from a simple desktop GUI and see results in real-time
- Out of scope:
  - Conversation history persistence across app restarts
  - Custom tool definitions
  - File attachments or image support
  - Multi-session management
  - Authentication UI (relies on pre-configured `copilot` CLI auth)
- Assumptions:
  - **Assumption (explicit)**: GitHub Copilot CLI is installed and authenticated (`copilot --version` works)
  - **Assumption (explicit)**: Python 3.9+ is available with tkinter bundled
  - **Assumption (explicit)**: Model `gpt-4.1` will be used as default (configurable)
  - **Assumption (explicit)**: In-memory conversation only; no persistence
- Acceptance Criteria (bulleted, testable):
  - [ ] App launches a Tkinter window with a chat display area, text input field, and Send button
  - [ ] User can type a prompt and press Send (or Enter) to submit
  - [ ] Response streams into the chat area in real-time via `assistant.message_delta` events
  - [ ] Chat area shows both user messages and assistant responses with clear visual distinction
  - [ ] Error states (connection failure, SDK errors) display an error message in the chat area
  - [ ] App gracefully shuts down the CopilotClient on window close
- Non-functional requirements:
  - UI must remain responsive during streaming (no freezing)
  - Async SDK calls run in a background thread to avoid blocking tkinter main loop
- Telemetry / metrics expected: None
- Rollout / rollback notes: Single-file app; rollback = delete file
