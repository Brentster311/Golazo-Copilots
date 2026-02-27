# SFI-020 — Test Cases

## Right-Click KPI Row → Analyze with LLM (Core)

| Author | Date | Mapped To |
|--------|------|-----------|
| QA (Golazo) | 2026-02-06 | SFI-020 Acceptance Criteria |

---

## Test Case Mapping to Acceptance Criteria

| AC# | Acceptance Criterion | Test Cases |
|-----|---------------------|------------|
| AC1 | Right-click shows context menu | TC-01, TC-02, TC-03 |
| AC2 | LLM analysis displayed in modal | TC-04, TC-05, TC-06, TC-07 |
| AC3 | Result saved to disk | TC-08, TC-09, TC-10 |
| AC4 | UI remains responsive | TC-11, TC-12 |
| AC5 | Error handling | TC-13, TC-14, TC-15, TC-16 |

---

## Group 1: Context Menu (AC1)

### TC-01: Right-click KPI row shows context menu
- **Given**: SFIReporterApp is loaded with data; KPI treeview has rows
- **When**: User right-clicks (`<Button-3>`) a KPI row in `tree_kpis`
- **Then**: A context menu appears with "🤖 Analyze with LLM" option
- **And**: The clicked row is selected (highlighted)
- **Verify**: `tree.selection()` returns the right-clicked row's iid

### TC-02: Right-click in DetailModal treeview shows context menu
- **Given**: A `DetailModal` is open with action item rows
- **When**: User right-clicks a row in the DetailModal's treeview
- **Then**: Same context menu appears with "🤖 Analyze with LLM"
- **And**: The clicked row is selected

### TC-03: Right-click on empty space does NOT show context menu
- **Given**: KPI treeview is visible with rows
- **When**: User right-clicks on empty space below the last row
- **Then**: No context menu appears
- **Verify**: `tree.identify_row(event.y)` returns empty string → menu not posted

---

## Group 2: LLM Analysis + Display (AC2)

### TC-04: build_prompt produces structured prompt from item data
- **Given**: A complete action item dict with all expected fields
- **When**: `build_prompt(item)` is called
- **Then**: Returns a string containing the item's title, status, SLA, dates, owner, service name, remediation text
- **And**: The prompt instructs the LLM to return Mission, Steps to Done, Resources Needing Repair, Risk of Delay sections

### TC-05: build_prompt handles missing/None fields gracefully
- **Given**: An action item dict with only `id` and `Title` fields (others missing or None)
- **When**: `build_prompt(item)` is called
- **Then**: Returns a valid prompt string without errors
- **And**: Missing fields show as "N/A" or are omitted

### TC-06: analyze_item returns structured AnalysisResult (mocked)
- **Given**: A mocked Azure OpenAI client that returns a well-formatted response
- **When**: `analyze_item(item, config)` is called
- **Then**: Returns an `AnalysisResult` with `mission`, `steps_to_done`, `resources_needing_repair`, `risk_of_delay` populated
- **And**: `timestamp` is set, `action_item_id` matches input

### TC-07: AnalysisModal displays all four sections
- **Given**: An `AnalysisResult` with all four sections populated
- **When**: `AnalysisModal` is opened with the result
- **Then**: Modal displays labeled sections: Mission, Steps to Done, Resources Needing Repair, Risk of Delay
- **And**: Action item title and timestamp are shown in the header

---

## Group 3: Persistent Storage (AC3)

### TC-08: save_analysis writes valid JSON to correct path
- **Given**: An `AnalysisResult` for action item "AI-12345"
- **When**: `save_analysis(result)` is called
- **Then**: A file exists at `<LOCALAPPDATA>/GUI/analyses/AI-12345.json`
- **And**: File contains valid JSON with `schema_version`, `action_item_id`, `analysis`, `timestamp`

### TC-09: load_analysis reads back saved data
- **Given**: A saved analysis JSON file for "AI-12345"
- **When**: `load_analysis("AI-12345")` is called
- **Then**: Returns a dict matching the saved data
- **And**: `analysis.mission`, `analysis.steps_to_done`, etc. are present

### TC-10: analysis_exists returns correct boolean
- **Given**: Analysis saved for "AI-12345" but NOT for "AI-99999"
- **When**: `analysis_exists("AI-12345")` and `analysis_exists("AI-99999")` are called
- **Then**: Returns `True` and `False` respectively

---

## Group 4: UI Responsiveness (AC4)

### TC-11: Analysis runs on background thread
- **Given**: "Analyze with LLM" is triggered
- **When**: The LLM call is in progress
- **Then**: The call executes on a non-main thread (`threading.current_thread() != threading.main_thread()`)
- **And**: The main thread (UI) is not blocked

### TC-12: Concurrent analysis is blocked
- **Given**: An analysis is already in progress
- **When**: User right-clicks another row and clicks "Analyze with LLM"
- **Then**: The menu option is disabled or shows "Analysis in progress…"
- **And**: Only one LLM call is active at a time

---

## Group 5: Error Handling (AC5)

### TC-13: Missing API key shows configuration error
- **Given**: `AZURE_OPENAI_API_KEY` environment variable is not set
- **When**: User clicks "Analyze with LLM"
- **Then**: A `messagebox.showerror` appears with the missing variable name(s) and setup instructions
- **And**: No LLM call is attempted

### TC-14: LLM API timeout shows error
- **Given**: Azure OpenAI API times out (mocked to raise `openai.APITimeoutError`)
- **When**: `analyze_item` is called
- **Then**: Raises or returns an error
- **And**: The UI shows a user-friendly error message, not a raw traceback

### TC-15: LLM API returns unexpected format
- **Given**: Azure OpenAI returns a response that doesn't follow the section header format
- **When**: `analyze_item` processes the response
- **Then**: Falls back to displaying the raw response text in the modal
- **And**: No crash or unhandled exception

### TC-16: Corrupted saved analysis file
- **Given**: An analysis JSON file exists but contains invalid JSON
- **When**: `load_analysis` is called for that action item
- **Then**: Returns `None` (or raises a handled exception)
- **And**: Does not crash the application

---

## Security Tests

### TC-17: API key not in logs or UI
- **Given**: LLM config is loaded with an API key
- **When**: An analysis completes (success or error)
- **Then**: The API key does not appear in log files, modal text, or error messages
- **Verify**: Search log output and modal text widgets for the key string
