# SFI-008 — Architect Notes
Retroactive review. URL extraction is display-only (no data mutation). HTML regex is scoped to S360's limited anchor format — not general-purpose HTML parsing. `webbrowser.open()` delegates to OS. No security concerns.
