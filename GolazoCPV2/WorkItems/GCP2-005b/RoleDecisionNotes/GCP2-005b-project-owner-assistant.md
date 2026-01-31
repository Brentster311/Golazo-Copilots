# GCP2-005b: Project Owner Assistant Decision Notes

**Work Item**: GCP2-005b - Shared React WebView  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **React + TypeScript**: Modern stack with good tooling and type safety.

2. **Vite for bundling**: Fast builds, simple configuration.

3. **CSS variables for theming**: Enables adaptation to VS Code and VS themes.

4. **postMessage for communication**: Standard WebView communication pattern.

5. **Single bundle output**: Same HTML/JS/CSS used by both IDE extensions.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| Vanilla JS | Less maintainable for complex UI |
| Svelte/Vue | Less ecosystem support for WebView contexts |
| Separate builds per IDE | Duplicated effort |

---

## Tradeoffs Accepted

- **Bundle size**: React adds ~40KB; acceptable for rich UI.
- **Build step required**: Must build WebView before extensions can use it.

---

## Known Limitations

- Theme adaptation requires CSS variable mapping per IDE
- Complex state requires careful postMessage handling

---

## Must-Ask Checklist Responses

- **Interface type**: React WebView (embedded in IDE extensions)
- **Target platform**: Runs inside VS Code and Visual Studio WebView
- **Data persistence**: Receives state from host extension
- **User type**: Technical (developers viewing workflow status)
