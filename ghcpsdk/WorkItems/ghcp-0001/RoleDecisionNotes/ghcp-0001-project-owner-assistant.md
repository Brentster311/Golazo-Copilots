# Decision Notes — Project Owner Assistant

## Work Item: ghcp-0001

### Decisions Made
- **Interface type**: Tkinter GUI (user-specified)
- **Target platform**: Windows (user's current OS), but Tkinter is cross-platform
- **Data persistence**: In-memory only (no database or file persistence needed for basic prompt/response)
- **User type**: Technical developer with Copilot subscription

### Scope Rationale
Single user story — one user-observable outcome: send a prompt and see the streamed response in a desktop GUI. No decomposition needed.

### Key Design Choices
- Python Copilot SDK (`github-copilot-sdk`) for the backend integration
- asyncio + threading pattern to keep Tkinter responsive while SDK runs async
- Streaming enabled for real-time response display
- Single session per app lifecycle; session created on first send
