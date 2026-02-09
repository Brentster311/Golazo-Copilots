# LLM-0009 — Project Owner Assistant Notes

## Origin
During live testing of `_summarize_s360.py`, we discovered that:
1. `browser_auth="aad"` (device-code flow) fails with Conditional Access error **530033** — device code tokens don't carry device compliance claims
2. `channel="msedge"` (Playwright-managed Edge) fails with error **53000** — Playwright launches a fresh profile without device identity/WAM registration
3. The **only** working approach was connecting to the user's **real Edge browser** (which has device compliance via WAM) using Chrome DevTools Protocol (CDP)

The workaround required ~40 lines of manual process management, CDP wiring, and tab-finding logic in the debug script. This should be a first-class library feature.

## Scope Decisions
- **Windows-first**: Edge paths and user-data-dir are OS-specific. Covering Windows first captures >90% of the internal Microsoft developer audience. Cross-platform is a future story.
- **Edge-only**: CDP works with any Chromium browser, but device compliance is tied to the Edge profile on managed Windows devices. Supporting Chrome/Brave is not useful for this use case.
- **Kill-and-relaunch**: Edge ignores `--remote-debugging-port` when already running. The only reliable approach is to kill existing instances and relaunch. We mitigate UX impact with `--restore-last-session`.

## Must-Ask Checklist
All items are already established from prior work items (LLM-0001 through LLM-0008):
- **Interface type**: Python library
- **Target platform**: Windows (cross-platform later)
- **Data persistence**: In-memory only
- **User type**: Technical (developers)
