# GCP2-005c: Visual Studio Extension

**Status**: BACKLOG  
**Priority**: Low  
**Size**: M  
**Created**: 2026-01-27  
**Parent**: GCP2-005

---

## User Story

- **Title**: Visual Studio Extension
- **As a**: Developer using Visual Studio
- **I want**: A Golazo extension that shows workflow status
- **So that**: I can see my current role and progress without checking files

- **Out of scope**:
  - React WebView UI (GCP2-005b)
  - VS Code extension (GCP2-005a)
  - Agent implementation (GCP2-001)

- **Assumptions**:
  - **Assumption (explicit)**: Extension spawns Golazo agent as child process
  - **Assumption (explicit)**: WebView2 hosts React UI from GCP2-005b
  - **Assumption (explicit)**: Visual Studio 2022+ required for WebView2

- **Acceptance Criteria**:
  - [ ] Status bar shows: work item ID, current role, DoR/DoD summary
  - [ ] Click status bar opens tool window
  - [ ] Tool window hosts React WebView via WebView2
  - [ ] Extension spawns and manages Golazo agent process
  - [ ] Extension communicates via Golazo Protocol (JSON-RPC)
  - [ ] Menu item registered: View ? Golazo Workflow
  - [ ] Info bar notifications on role transitions

- **Non-functional requirements**:
  - Extension activation time < 2 seconds
  - Status bar updates within 500ms of state change
  - Graceful handling of agent crashes

- **Telemetry / metrics expected**:
  - None for MVP

- **Rollout / rollback notes**:
  - Publish to VS marketplace; users install via Extensions menu

---

## Extension Structure

```
Golazo.VisualStudio/
??? Golazo.VisualStudio.csproj
??? source.extension.vsixmanifest
??? GolazoPackage.cs
??? ToolWindows/GolazoToolWindow.cs
??? Resources/webview/
```

---

## Dependencies

- GCP2-001c (Golazo Protocol)
- GCP2-005b (Shared WebView UI)
5. [ ] Tool window registered in View menu
6. [ ] Window hosts React WebView via WebView2
7. [ ] Window communicates with extension via WebView2 messaging
8. [ ] Window dockable (default: right side)

### Agent Connection
9. [ ] Extension spawns Golazo agent on load
10. [ ] Extension communicates via Golazo Protocol (JSON-RPC)
11. [ ] Extension handles agent crashes gracefully
12. [ ] Extension reconnects if agent restarts

### Commands
13. [ ] Menu: View ? Golazo Workflow
14. [ ] Command: Golazo.ShowStatus
15. [ ] Command: Golazo.SwitchWorkItem
16. [ ] Command: Golazo.CreateWorkItem

### Notifications
17. [ ] Info bar notification on role transition
18. [ ] Info bar notification on DoR/DoD completion

## Extension Structure

```
Golazo.VisualStudio/
??? Golazo.VisualStudio.csproj
??? source.extension.vsixmanifest
??? GolazoPackage.cs           # Package entry point
??? StatusBar/
?   ??? GolazoStatusBar.cs     # Status bar integration
??? ToolWindows/
?   ??? GolazoToolWindow.cs    # Tool window definition
?   ??? GolazoToolWindowControl.xaml  # WebView2 host
??? Services/
?   ??? AgentService.cs        # Agent process management
?   ??? ProtocolClient.cs      # JSON-RPC client
??? Commands/
?   ??? GolazoCommands.cs      # Command handlers
??? Resources/
    ??? webview/               # Built React app (from GCP2-005b)
```

## Status Bar Format

```
?? GCP2-005c | Developer | DoR ? | DoD 3/7
```

## Visual Studio APIs Used

- `IVsStatusbar` for status bar
- `ToolWindowPane` for tool window
- `Microsoft.Web.WebView2.Wpf` for WebView2
- `OleMenuCommandService` for commands
- `IVsInfoBarUIFactory` for notifications

## WebView2 Integration

```csharp
public partial class GolazoToolWindowControl : UserControl
{
    private WebView2 _webView;
    
    public async Task InitializeAsync()
    {
        await _webView.EnsureCoreWebView2Async();
        _webView.CoreWebView2.WebMessageReceived += OnWebMessageReceived;
        _webView.NavigateToString(GetWebViewHtml());
    }
    
    public void SendStateUpdate(GolazoState state)
    {
        var json = JsonSerializer.Serialize(new { type = "state", payload = state });
        _webView.CoreWebView2.PostWebMessageAsJson(json);
    }
}
```

## Out of Scope

- React WebView UI (GCP2-005b)
- VS Code extension (GCP2-005a)
- Agent implementation (GCP2-001)

## Dependencies

- GCP2-001c (Golazo Protocol for communication)
- GCP2-005b (Shared WebView UI)

## Technical Notes

- C# / .NET (target VS 2022+)
- VSIX packaging
- WebView2 for hosting React UI
- Spawn agent as child process
- AsyncPackage for async initialization
- Consider MVVM pattern for tool window
