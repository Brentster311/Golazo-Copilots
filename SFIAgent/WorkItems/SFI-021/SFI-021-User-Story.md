# SFI-021: URL Content Enrichment for LLM Analysis

**Status**: BACKLOG

---

## User Story

**Title**: Enrich LLM analysis by fetching content from action item URLs

**As a**: SFI engineer using the SFIReporter desktop app  
**I want**: The "Analyze with LLM" feature to automatically follow URLs embedded in the action item (wiki links, remediation links, asset links) and include that content in the analysis  
**So that**: The LLM produces a more accurate and actionable analysis based on the full context of the remediation ask, not just the summary fields

---

## Out of Scope

- Crawling beyond the direct URLs (no following links within fetched pages)
- Caching fetched URL content for reuse across analyses
- Authenticating to SSO-protected URLs (best-effort only)
- Rendering HTML/rich content in the analysis modal
- Modifying the analysis modal layout (uses existing SFI-020 modal)

---

## Assumptions

- **Assumption (explicit)**: SFI-020 (core Analyze with LLM) is already implemented — this story enhances the LLM prompt with richer content
- **Assumption (explicit)**: URL fields to follow include: `ResourceURIs`, `ActionWikiLink`, `CustomGroupingLink`, `AssetTypeLink0`, `AssetTypeLink1`, `AssetTypeLink2`
- **Assumption (explicit)**: URL fetching is best-effort — unreachable or auth-gated URLs are skipped gracefully; the LLM works with whatever content is available
- **Assumption (explicit)**: Fetched content will be cleaned (HTML stripped to text) and truncated to fit within LLM token limits
- **Assumption (explicit)**: URL fetching happens on the same background thread as the LLM call, with per-URL timeouts

---

## Acceptance Criteria

- [ ] When "Analyze with LLM" is triggered, all non-empty URL fields in the action item are fetched before calling the LLM
- [ ] Fetched URL content is stripped to plain text and included in the LLM prompt as additional context
- [ ] Each URL fetch has a 10-second timeout; unreachable URLs are skipped without blocking the analysis
- [ ] If a URL requires authentication and returns a 401/403, it is skipped gracefully with a note in the analysis
- [ ] The total content sent to the LLM is truncated to stay within token limits (with a clear truncation strategy)

---

## Non-Functional Requirements

- Per-URL timeout of 10 seconds maximum
- Total URL fetching phase should not exceed 30 seconds (parallel fetching preferred)
- No credentials should be sent to arbitrary URLs
- Should work on Windows (primary platform)

---

## Telemetry / Metrics Expected

- Count of URLs attempted vs. successfully fetched per analysis
- Average URL fetch time
- Count of auth-gated / timed-out URLs

---

## Rollout / Rollback Notes

- Feature enhances SFI-020 but is independently toggleable
- Rollback: remove URL fetching from the analysis pipeline; LLM falls back to data-only analysis
