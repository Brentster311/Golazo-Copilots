# SFI-021 — Design Review Comments

## Reviewer: Quality Assurance
## Date: 2026-02-08

---

## Overall Assessment

The design is **clear, minimal, and well-scoped**. The approach of delegating URL fetching to `llm-extender` is sound and avoids duplication. The existing `url_content` parameter in `build_prompt()` and `analyze_item()` means the integration surface is small.

## Findings

### ✅ Strengths

1. **Minimal changeset**: Only 3 files touched, existing infrastructure already supports `url_content`
2. **Parallel fetching with ThreadPoolExecutor**: Correct approach for staying within the 30-second budget
3. **Best-effort design**: Graceful degradation when URLs are unreachable
4. **No credential forwarding**: Good security posture

### ⚠️ Minor Concerns (no scope change needed)

1. **`ResourceURIs` field format**: The design assumes this is a single URL string. In the sample data it appears as a single URL, but the field name is plural. If it's semicolon/comma-delimited or JSON array, the extraction logic should handle that.
   - **Recommendation**: `fetch_action_item_urls()` should split `ResourceURIs` on common delimiters (`,`, `;`, whitespace) and validate each as a URL.

2. **Total timeout enforcement**: The design mentions a 30-second total cap but `ThreadPoolExecutor` with per-URL 10s timeouts on 6 URLs in parallel could still hit ~10s. The design should clarify whether there's an explicit total timeout wrapper or if the parallelism is sufficient.
   - **Recommendation**: The parallelism (6 workers for 6 URLs) naturally keeps total time ≤ 10s worst case. Document this.

3. **Progress modal status**: Should show "Fetching URL content (3/6)..." style updates for user feedback during the fetch phase.
   - **Recommendation**: Optional; the fetch phase is fast enough that a single status message is acceptable for v1.

### ✅ No Scope Changes Required

All concerns are implementation details within the existing user story scope.

## Approval

**Design approved** — proceed to test case definition and implementation.

---

## Architect Notes

### Reviewer: Architect
### Date: 2026-02-08

### Architectural Alignment
- The design correctly extends the existing SFI-020 pipeline at a single integration point (`_launch_llm_analysis`)
- `llm-extender` is an appropriate choice — it's an internal library already designed for this exact use case
- The `fetch_action_item_urls()` function is a pure function (input: item dict → output: dict[str, str]) with no side effects on the application state — clean contract

### API / Data Contracts
- **Input**: Action item `dict` with optional URL fields (6 known keys)
- **Output**: `dict[str, str]` mapping URL → plain text content
- **Error contract**: Function never raises — all errors caught internally and logged. Returns partial results.
- **Existing contract preserved**: `analyze_item(item, config, url_content=...)` already accepts this shape

### Security & Privacy
- ✅ No credentials sent to arbitrary URLs (verified: `fetch_url()` default has no auth header)
- ✅ No user data exposed in URL requests (only User-Agent header)
- ⚠️ **Default behavior check**: `llm_extender.url_fetcher.fetch_url()` follows up to 10 redirects by default. An attacker-controlled URL could redirect to an internal endpoint. **Mitigation**: This is acceptable for v1 since URLs come from S360 action items (trusted source), not user input. Document this assumption.

### Resilience
- ✅ Per-URL timeout prevents single-URL hang
- ✅ `ThreadPoolExecutor` with `max_workers=6` bounds concurrency
- ✅ Graceful degradation — empty `url_content` dict produces same analysis as pre-SFI-021

### Dependency
- `llm-extender` as a `pyproject.toml` dependency is correct
- The library's `fetch_url` uses `httpx` which is already an indirect dependency via the LLMExtender lib — no new transitive dependency conflicts

### Verdict
**Approved** — no architectural changes needed. One documentation note about redirect-following trust model added above.

