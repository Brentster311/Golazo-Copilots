# SFI-034 Test Cases

## TC-1: Prompt construction with multiple items
**Maps to**: AC-3 (analysis prompt includes all items for KPI)
- **Setup**: Create 5 mock items with `_kpi_id="KPI-A"`, varying services/owners/SLA/ETA
- **Action**: Call `build_analysis_prompt(items, fetched_docs={})`
- **Expected**: Returned prompt contains all 5 item IDs, titles, services, owners, SLA types, ETA dates
- **Failure message**: "Prompt missing item data for KPI items"

## TC-2: Prompt construction with fetched docs
**Maps to**: AC-3 (includes content fetched from URL fields)
- **Setup**: Create 2 mock items with `url="https://example.com/doc"` and `ActionWikiLink="https://wiki.example.com/guide"`
- **Action**: Call `build_analysis_prompt(items, fetched_docs={"https://example.com/doc": "First doc...", "https://wiki.example.com/guide": "Second doc..."})`
- **Expected**: Prompt includes both URLs and their text content in the Documentation section
- **Failure message**: "Fetched documentation not included in prompt"

## TC-3: URL deduplication
**Maps to**: AC-3
- **Setup**: Create 3 items all with `url="https://same.com/doc"` and one with `ActionWikiLink="https://different.com"`
- **Action**: Call `collect_urls(items)`
- **Expected**: Returns exactly 2 unique URLs
- **Failure message**: "Duplicate URLs not deduplicated"

## TC-4: URL fetch timeout
**Maps to**: AC-5 (reasonable timeout, graceful degradation)
- **Setup**: Mock HTTP server that delays 15 seconds
- **Action**: Call `fetch_url_content(url, timeout=10)`
- **Expected**: Returns error/empty result within ~10s, does not hang
- **Failure message**: "URL fetch did not respect timeout"

## TC-5: URL fetch failure graceful degradation
**Maps to**: AC-5
- **Setup**: URL that returns HTTP 403
- **Action**: Call `fetch_url_content(url)`
- **Expected**: Returns a failure marker (e.g., `{"url": ..., "error": "403 Forbidden", "content": ""}`) — does not raise
- **Failure message**: "URL fetch failure raised exception instead of degrading gracefully"

## TC-6: HTML to text extraction
**Maps to**: AC-3
- **Setup**: HTML string `"<html><body><h1>Title</h1><p>Content here</p><script>var x=1;</script></body></html>"`
- **Action**: Call `extract_text(html)`
- **Expected**: Returns text containing "Title" and "Content here", does NOT contain "var x=1"
- **Failure message**: "HTML extraction included script content or missed body text"

## TC-7: Text truncation
**Maps to**: NFR (4,000 chars per URL)
- **Setup**: Text string of 10,000 characters
- **Action**: Call `truncate_content(text, max_len=4000)`
- **Expected**: Result is ≤4,000 chars, ends with truncation marker
- **Failure message**: "Truncated text exceeds max length"

## TC-8: Item count cap
**Maps to**: NFR (cap at 30 items)
- **Setup**: 50 mock items for same KPI
- **Action**: Call `build_analysis_prompt(items, fetched_docs={})`
- **Expected**: Prompt includes at most 30 items, includes a note like "Showing 30 of 50 items"
- **Failure message**: "Prompt did not cap items or note truncation"

## TC-9: Four-question structure in prompt
**Maps to**: AC-4
- **Setup**: Any valid items
- **Action**: Call `build_analysis_prompt(items, fetched_docs={})`
- **Expected**: Prompt contains all four questions: "What is being asked?", "Why?", "On what resources", "How?"
- **Failure message**: "Prompt missing one or more of the four analysis questions"

## TC-10: Empty URL fields skipped
**Maps to**: AC-3
- **Setup**: Item with `url=""`, `ActionWikiLink=None`, `Remediation=""`
- **Action**: Call `collect_urls([item])`
- **Expected**: Returns empty set
- **Failure message**: "Empty/None URL fields not filtered out"

## TC-11: send_analysis_prompt handles disconnected state
**Maps to**: AC-1, AC-6 (Review Comment #3)
- **Setup**: CopilotPanel with no active session
- **Action**: Call `send_analysis_prompt(prompt)`
- **Expected**: Panel connects first, then sends. Prompt is not lost.
- **Failure message**: "Analysis prompt lost when panel was disconnected"

## TC-12: KPI ID resolution from right-click
**Maps to**: AC-1, AC-2 (Review Comment #6)
- **Setup**: Mock action tree with a KPI row containing items
- **Action**: Simulate right-click → resolve kpi_id
- **Expected**: `_kpi_id` field is correctly extracted from the selected item
- **Failure message**: "KPI ID not resolved from right-clicked item"

## TC-13: Integration — right-click triggers analysis in Copilot Chat
**Maps to**: AC-1
- **Setup**: App with loaded data, Copilot panel available
- **Action**: Trigger `_launch_llm_analysis(parent, item)` with a real item dict
- **Expected**: Copilot panel opens/activates, prompt is sent, response streams
- **Failure message**: "End-to-end analysis flow did not produce response in Copilot Chat"
