# SFI-033 — Program Manager Decision Notes

## Design Decisions
1. **New module `copilot_panel.py`** rather than embedding all chat logic in app.py — keeps app.py manageable and follows SFI-030 module refactoring pattern.
2. **AsyncBridge pattern** directly ported from ghcpsdk — proven approach for async SDK + Tkinter.
3. **Stub rather than remove analysis** — preserves menu item for future re-implementation with Copilot SDK.
4. **Optional dependency** — `github-copilot-sdk` as optional; panel shows error if unavailable rather than crashing the app.
