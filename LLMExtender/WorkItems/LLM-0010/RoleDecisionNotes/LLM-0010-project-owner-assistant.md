# LLM-0010 — Project Owner Assistant Notes

## Origin
The `_summarize_s360.py` debug script contains a hand-rolled 120-iteration polling loop that checks whether the Playwright page URL still contains `login.microsoftonline.com` or `login.windows.net`. This same pattern already exists (partially) in `_fetch_with_browser` via `detect_aad_redirect()`, but it only fires once — it doesn't wait for interactive login to complete.

With the addition of `browser_auth="cdp"` (LLM-0009), the wait-for-login logic is needed in multiple code paths. Extracting it into a reusable helper avoids duplication and ensures consistent timeout/error behavior.

## Scope Decisions
- **Internal helper, not public API**: This is a refactoring that consolidates duplicated logic. External consumers don't need to call it directly.
- **Sync + async variants**: Matching the existing pattern of `_fetch_with_browser` / `_afetch_with_browser`.
- **Separate from LLM-0009**: Can be implemented and tested independently, even though LLM-0009 is the primary consumer.

## Must-Ask Checklist
All items established from prior work items:
- **Interface type**: Python library (internal utility)
- **Target platform**: Cross-platform
- **Data persistence**: In-memory only
- **User type**: Library maintainers
