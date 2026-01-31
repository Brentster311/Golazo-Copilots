# GCP2-005a: Project Owner Assistant Decision Notes

**Work Item**: GCP2-005a - VS Code Extension  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **TypeScript implementation**: Standard for VS Code extensions.

2. **Spawn agent as child process**: Extension manages agent lifecycle.

3. **WebView for sidebar panel**: Hosts shared React UI from GCP2-005b.

4. **Native status bar**: Uses VS Code API for native look and feel.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| Pure TreeView UI | Less rich than WebView; harder to match VS version |
| Connect to external agent | More complex setup for users |

---

## Tradeoffs Accepted

- **Child process management**: Extension must handle agent crashes/restarts.

---

## Known Limitations

- Agent must be installed separately (or bundled)
- WebView styling must adapt to VS Code themes

---

## Must-Ask Checklist Responses

- **Interface type**: VS Code extension
- **Target platform**: Cross-platform (VS Code runs everywhere)
- **Data persistence**: Via agent (GCP2-003)
- **User type**: Technical (developers using VS Code)
