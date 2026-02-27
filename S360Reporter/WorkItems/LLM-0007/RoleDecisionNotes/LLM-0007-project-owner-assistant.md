# LLM-0007 — Project Owner Assistant Notes

## Decision: Single story
One user-observable outcome: "fetch_url can render JavaScript before extracting text." The feature is a single `render_js=True` flag on existing API.

## Scope Justification
- Kept to headless rendering only — not browser login automation or interactive flows
- Playwright chosen over Selenium for better async support and Python API
- Optional dependency keeps core library lightweight

## Context
Triggered by LLM-0006 live testing failures on aka.ms/msw (SharePoint) and aka.ms/s360 (Service360) — both are SPAs that return empty HTML shells.
