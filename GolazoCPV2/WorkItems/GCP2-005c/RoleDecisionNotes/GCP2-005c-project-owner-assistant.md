# GCP2-005c: Project Owner Assistant Decision Notes

**Work Item**: GCP2-005c - Visual Studio Extension  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **C# / .NET implementation**: Standard for Visual Studio extensions.

2. **WebView2 for hosting React UI**: Modern WebView control for Windows.

3. **Tool window for sidebar**: VS convention for dockable panels.

4. **Native status bar**: Uses VS Shell APIs.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| WPF-only UI | Would require separate UI development from VS Code |
| VSIX with web technologies | WebView2 is the supported approach |

---

## Tradeoffs Accepted

- **Windows only**: Visual Studio extension only works on Windows.
- **WebView2 dependency**: Must be installed on user's machine (usually present on modern Windows).

---

## Known Limitations

- Visual Studio 2022+ required for WebView2 support
- Theme integration requires mapping VS theme to CSS variables

---

## Must-Ask Checklist Responses

- **Interface type**: Visual Studio extension
- **Target platform**: Windows (Visual Studio)
- **Data persistence**: Via agent (GCP2-003)
- **User type**: Technical (developers using Visual Studio)
