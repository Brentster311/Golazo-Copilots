# SFI-016 — Project Owner Assistant Notes

## Decision: Single Work Item
The singleton client fix and KPI retry feature are tightly coupled — both address resilience of the KPI fetch pipeline. The singleton prevents redundant token acquisition that was causing log noise, and the retry feature handles the cases where individual KPI fetches still fail despite the singleton fix. Shipping one without the other would be incomplete.

## Scope Justification
- **Singleton client**: Small change (10 lines in `data.py`) but high-impact — eliminates ~25 redundant `az account get-access-token` calls per refresh.
- **KPI retry UI**: Moderate change (~130 lines in `tk_app.py`) but directly user-visible — users previously had no indication that some KPIs silently failed.
- **Test fixes**: Required to maintain CI green — 6 tests needed mock updates for the new `tuple` return type.

## Must-Ask Checklist Resolution
- **Interface type**: Tkinter desktop — established in SFI-001 through SFI-015.
- **Target platform**: Windows — established.
- **Data persistence**: JSON file cache at `%TEMP%/sfireporter/` — established.
- **User type**: Technical (Microsoft engineers using S360) — established.

No questions needed; all answers carry forward from prior work items.
