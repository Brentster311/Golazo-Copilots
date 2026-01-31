# GCP2-005: Project Owner Assistant Decision Notes

**Work Item**: GCP2-005 - IDE Extensions (Epic)  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **Hybrid architecture**: Shared Python agent + shared React WebView + native IDE shells.

2. **Split into three sub-stories**: VS Code, WebView, Visual Studio can be developed somewhat independently.

3. **WebView first**: Shared UI component enables parallel IDE extension development.

4. **Status bar is native per IDE**: Simple status bar uses native APIs for better integration feel.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| Separate implementations per IDE | Duplicated logic, divergent behavior |
| Native UI per IDE | Two UI codebases to maintain |
| CLI + file watching only | No real-time updates |

---

## Tradeoffs Accepted

- **WebView feels less native**: Acceptable for rich workflow panel; status bar is native.
- **React dependency**: Adds build complexity but provides rich UI capabilities.

---

## Known Limitations

- JetBrains IDE support not included (future consideration)
- WebView requires bundling React app

---

## Must-Ask Checklist Responses

- **Interface type**: IDE extensions (VS Code TypeScript, VS C#) + React WebView
- **Target platform**: VS Code (cross-platform), Visual Studio (Windows)
- **Data persistence**: Via GCP2-003 state files (read by extensions)
- **User type**: Technical (developers)
