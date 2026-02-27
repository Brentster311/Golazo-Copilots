# SFI-035 — LLM Analysis Sources Provenance Card

**Status**: BACKLOG

## User Story

- **Title**: Show URL extraction & fetch provenance in LLM analysis output
- **As a**: S360Reporter user analyzing a KPI with the "Analyze with LLM" feature
- **I want**: to see a clear summary of which documentation URLs were extracted from my action items and whether each URL was successfully fetched, before the LLM summary appears
- **So that**: I can trust the LLM's analysis by knowing exactly what source material it had access to, and I can identify when critical documentation was unreachable

- **Out of scope**:
  - Changing the LLM prompt content or model behavior
  - Adding retry logic for failed URL fetches
  - Persisting provenance data to disk or database
  - Modifying what URL fields are extracted (the existing `_URL_FIELDS` tuple)

- **Assumptions**:
  - **Assumption (explicit)**: Interface type is the existing Tk GUI desktop app — no new interface type is introduced. The "Sources" card appears in the existing Copilot Chat panel.
  - **Assumption (explicit)**: Target platform is Windows (matching the existing S360Reporter build target).
  - **Assumption (explicit)**: No data persistence — the provenance info is display-only in the chat panel, same as the LLM response itself.
  - **Assumption (explicit)**: User type is a technical user (security/compliance engineer) who understands URLs and fetch errors.

- **Acceptance Criteria** (bulleted, testable):
  - When the user triggers "Analyze with LLM", a "Sources" summary message appears in the Copilot Chat panel **before** the LLM streaming response begins
  - The Sources summary displays the total count of URLs extracted, how many were successfully fetched, and how many failed
  - Each URL is listed with a status indicator: ✅ for successful fetch (with character count of extracted content), ❌ for failed fetch (with the error reason)
  - If zero URLs are found, the Sources summary says "No documentation URLs found in action items"
  - The `analyze_kpi` function returns structured metadata (not just a prompt string) containing `urls_found`, `fetch_results`, and `prompt`
  - Existing unit tests continue to pass; new unit tests cover the structured return type

- **Non-functional requirements**:
  - The Sources card must render in < 100 ms (it's local data, no I/O)
  - No additional network requests — uses data already collected during the existing fetch phase

- **Telemetry / metrics expected**:
  - Logger.info already captures URL counts; no new telemetry needed

- **Rollout / rollback notes**:
  - Backward-compatible — the prompt content sent to the LLM is unchanged
  - If `send_analysis_prompt` callers pass the old string type, a graceful fallback should still work (defensive coding)
