# GCP2-005a: VS Code Extension

**Status**: BACKLOG  
**Priority**: Low  
**Size**: M  
**Created**: 2026-01-27  
**Parent**: GCP2-005

---

## User Story

- **Title**: VS Code Extension
- **As a**: Developer using VS Code
- **I want**: A Golazo extension that shows workflow status
- **So that**: I can see my current role and progress without checking files

- **Out of scope**:
  - React WebView UI (GCP2-005b)
  - Visual Studio extension (GCP2-005c)
  - Agent implementation (GCP2-001)

- **Assumptions**:
  - **Assumption (explicit)**: Extension spawns Golazo agent as child process
  - **Assumption (explicit)**: WebView hosts React UI from GCP2-005b
  - **Assumption (explicit)**: Status bar uses native VS Code API

- **Acceptance Criteria**:
  - [ ] Status bar shows: work item ID, current role, DoR/DoD summary
  - [ ] Click status bar opens sidebar panel
  - [ ] Sidebar panel hosts React WebView from GCP2-005b
  - [ ] Extension spawns and manages Golazo agent process
  - [ ] Extension communicates via Golazo Protocol (JSON-RPC)
  - [ ] Commands registered: Show Status, Switch Work Item, Create Work Item
  - [ ] Notifications shown on role transitions

- **Non-functional requirements**:
  - Extension activation time < 1 second
  - Status bar updates within 500ms of state change
  - Graceful handling of agent crashes

- **Telemetry / metrics expected**:
  - None for MVP

- **Rollout / rollback notes**:
  - Publish to VS Code marketplace; users install via Extensions panel

---

## Extension Structure

```
golazo-vscode/
??? package.json
??? src/
?   ??? extension.ts
?   ??? statusBar.ts
?   ??? sidebarPanel.ts
?   ??? agentClient.ts
??? webview/dist/
```

---

## Dependencies

- GCP2-001c (Golazo Protocol)
- GCP2-005b (Shared WebView UI)
5. [ ] Sidebar panel registered in activity bar
6. [ ] Panel hosts React WebView (from GCP2-005b)
7. [ ] Panel communicates with extension via `postMessage`

### Agent Connection
8. [ ] Extension spawns Golazo agent on activation
9. [ ] Extension communicates via Golazo Protocol (JSON-RPC)
10. [ ] Extension handles agent crashes gracefully
11. [ ] Extension reconnects if agent restarts

### Commands
12. [ ] Command: `Golazo: Show Status` opens sidebar
13. [ ] Command: `Golazo: Switch Work Item` shows picker
14. [ ] Command: `Golazo: Create Work Item` prompts for ID

### Notifications
15. [ ] Notification on role transition
16. [ ] Notification on DoR/DoD completion

## Extension Structure

```
golazo-vscode/
??? package.json          # Extension manifest
??? src/
?   ??? extension.ts      # Entry point
?   ??? statusBar.ts      # Status bar management
?   ??? sidebarPanel.ts   # WebView panel
?   ??? agentClient.ts    # Protocol client
?   ??? commands.ts       # Command handlers
??? webview/              # Built React app (from GCP2-005b)
?   ??? dist/
??? resources/
    ??? icons/
```

## Status Bar Format

```
[?? GCP2-005a | Developer | DoR ? | DoD 3/7]
```

Click behavior:
- Left click: Open sidebar panel
- Hover: Show tooltip with full status

## VS Code APIs Used

- `vscode.window.createStatusBarItem()`
- `vscode.window.registerWebviewViewProvider()`
- `vscode.commands.registerCommand()`
- `vscode.window.showQuickPick()`
- `vscode.window.showInputBox()`
- `vscode.window.showInformationMessage()`

## Out of Scope

- React WebView UI (GCP2-005b)
- Visual Studio extension (GCP2-005c)
- Agent implementation (GCP2-001)

## Dependencies

- GCP2-001c (Golazo Protocol for communication)
- GCP2-005b (Shared WebView UI)

## Technical Notes

- TypeScript
- VS Code Extension API
- Spawn agent as child process
- Use `@anthropic-ai/sdk` patterns for JSON-RPC if helpful
- Bundle with esbuild or webpack
