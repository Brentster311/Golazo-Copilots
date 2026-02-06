# GCP-0013: Add Version Interface to Server

**Status**: BACKLOG

---

## User Story

- **Title**: Add Version Interface to MCP Server
- **As a**: Developer using Golazo Copilot
- **I want**: To query the installed version of golazo-copilot via MCP
- **So that**: I can verify which version is running and troubleshoot version-related issues

---

## Out of Scope
- Version update/upgrade functionality
- Version compatibility checking between client and server
- Changelog retrieval

---

## Assumptions
- **Assumption (explicit)**: Version is read from the package's `__version__` attribute (standard Python pattern)
- **Assumption (explicit)**: The version tool follows the same pattern as other gcp_* tools

---

## Acceptance Criteria

- [ ] New MCP tool `gcp_version` is available when server starts
- [ ] `gcp_version()` returns the current package version string (e.g., "2.8.0")
- [ ] Response includes package name and version in a structured format
- [ ] Tool is listed when user asks "What MCP tools do you have?"
- [ ] Tool works without any parameters

---

## Non-Functional Requirements
- Response time < 10ms (just reading a module attribute)
- No external dependencies or network calls

---

## Telemetry / Metrics Expected
- None required for this feature

---

## Rollout / Rollback Notes
- Additive change, no breaking changes
- Rollback: simply deploy previous version
