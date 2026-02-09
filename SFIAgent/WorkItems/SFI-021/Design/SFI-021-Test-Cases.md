# SFI-021 — Test Cases

## Mapping: Acceptance Criteria → Test Cases

| AC# | Acceptance Criterion | Test Case(s) |
|-----|---------------------|-------------|
| AC-1 | All non-empty URL fields are fetched before calling the LLM | TC-21-1, TC-21-2 |
| AC-2 | Fetched content stripped to plain text and included in prompt | TC-21-3 |
| AC-3 | Per-URL 10s timeout; unreachable URLs skipped | TC-21-4, TC-21-5 |
| AC-4 | 401/403 URLs skipped gracefully | TC-21-6 |
| AC-5 | Total content truncated to stay within token limits | TC-21-7 |

---

## TC-21-1: Extract URLs from all known fields

**Type**: Unit  
**Target**: `fetch_action_item_urls()`

**Setup**: Action item dict with all 6 URL fields populated:
- `ResourceURIs`: `"https://example.com/resource"`
- `ActionWikiLink`: `"https://wiki.example.com/page"`
- `CustomGroupingLink`: `"https://example.com/group"`
- `AssetTypeLink0`: `"https://example.com/asset0"`
- `AssetTypeLink1`: `"https://example.com/asset1"`
- `AssetTypeLink2`: `"https://example.com/asset2"`

**Mock**: `llm_extender.url_fetcher.fetch_url` returns `"content"` for all calls

**Expected**:
- `fetch_url` called 6 times (once per URL)
- Returns dict with 6 entries mapping URL → `"content"`

**Failure message**: `"Expected 6 URLs fetched, got {n}"`

---

## TC-21-2: Skip empty/None URL fields

**Type**: Unit  
**Target**: `fetch_action_item_urls()`

**Setup**: Action item with only `ActionWikiLink` populated; all others empty/None/missing

**Mock**: `llm_extender.url_fetcher.fetch_url` returns `"wiki content"`

**Expected**:
- `fetch_url` called exactly 1 time
- Returns `{"https://wiki.example.com/page": "wiki content"}`

**Failure message**: `"Expected 1 URL fetched for sparse item, got {n}"`

---

## TC-21-3: Fetched content appears in LLM prompt

**Type**: Unit  
**Target**: `build_prompt(item, url_content=...)`

**Setup**: Existing TC-4 pattern — pass `url_content` dict to `build_prompt()`

**Expected**:
- User message contains `"Additional Context from URLs"`
- User message contains the fetched content text
- User message contains the source URL

**Failure message**: `"URL content not found in LLM prompt"`

*Note: This is already covered by existing TC-4 in test_llm_client.py. Verified.*

---

## TC-21-4: Timed-out URL is skipped

**Type**: Unit  
**Target**: `fetch_action_item_urls()`

**Setup**: Item with 2 URLs. Mock `fetch_url`:
- URL 1: returns `"good content"`
- URL 2: raises `ProviderError("timed out")`

**Expected**:
- Returns dict with only 1 entry (the successful URL)
- No exception raised

**Failure message**: `"Timed out URL should be skipped, not raise"`

---

## TC-21-5: All URLs fail gracefully

**Type**: Unit  
**Target**: `fetch_action_item_urls()`

**Setup**: Item with 2 URLs. Mock `fetch_url` to raise `ProviderError` for both.

**Expected**:
- Returns empty dict `{}`
- No exception raised

**Failure message**: `"All-fail scenario should return empty dict"`

---

## TC-21-6: Auth-gated URL (401/403) skipped

**Type**: Unit  
**Target**: `fetch_action_item_urls()`

**Setup**: Item with 1 URL. Mock `fetch_url` to raise `ProviderError("HTTP 403")`

**Expected**:
- Returns empty dict
- No exception raised

**Failure message**: `"Auth-gated URL should be skipped gracefully"`

---

## TC-21-7: Content truncation in prompt

**Type**: Unit  
**Target**: `build_prompt(item, url_content=...)`

**Setup**: Pass `url_content` with a 5000-char content string

**Expected**:
- Content in prompt is truncated (contains `"[truncated]"`)
- Total URL content section does not exceed the truncation limit

**Failure message**: `"Large URL content should be truncated in prompt"`

---

## TC-21-8: ResourceURIs with multiple URLs

**Type**: Unit  
**Target**: `fetch_action_item_urls()`

**Setup**: `ResourceURIs = "https://a.com/1;https://b.com/2"`

**Mock**: `fetch_url` returns `"content"` for each

**Expected**:
- Both URLs extracted and fetched
- Returns dict with 2 entries

**Failure message**: `"Multiple ResourceURIs should be split and fetched"`

---

## TC-21-9: No URL fields populated

**Type**: Unit  
**Target**: `fetch_action_item_urls()`

**Setup**: Action item with no URL fields (all empty/missing)

**Expected**:
- Returns empty dict `{}`
- `fetch_url` never called

**Failure message**: `"Item with no URLs should return empty dict without fetching"`

---

## TC-21-10: analyze_item passes url_content through

**Type**: Unit  
**Target**: `analyze_item(item, config, url_content=...)`

**Setup**: Mock Azure OpenAI client. Pass `url_content` dict.

**Expected**:
- `build_prompt` receives the `url_content` parameter
- The resulting prompt sent to OpenAI contains URL content section

**Failure message**: `"url_content should flow through analyze_item to the prompt"`
