# EES-00005 — Design Doc: GUI for Incident Processing and Rule Management

## Summary
Add a desktop GUI application (Windows) that wraps the existing expert system engine, providing visual interfaces for incident loading, fact confirmation, rule browsing, ontology viewing, and rule evaluation. The GUI uses the same YAML persistence layer as the CLI, ensuring interoperability.

## Problem Statement
The expert system currently operates exclusively through CLI. While functional for developers, the CLI workflow (sequential prompts for each fact, rule, and root cause) becomes tedious for larger incidents. A GUI enables parallel review of facts, visual rule chain exploration, and more efficient interaction with the knowledge base.

## Business Case
- **Why now:** All engine functionality is complete (EES-00001 through EES-00004). The GUI is the natural consumer layer.
- **Impact:** Reduces friction in the learning loop (faster fact review) and testing phase (visual evaluation results). Makes the system accessible to engineers who prefer visual tools.
- **KPIs:** Time to process an incident (CLI vs GUI), user adoption, number of incidents processed.

## Stakeholders
- Technical user — primary GUI user
- Future extensions — GUI provides the foundation for richer features

## Functional Requirements

### FR-1: Incident Loading
- File browser dialog to select incident text files
- Display incident text in a read-only text area
- "Process" button triggers LLM extraction

### FR-2: Fact Review Panel
- Display LLM-proposed facts in a table/list with columns: Noun, Instance, Property, Operator, Value, Status
- Per-fact actions: Confirm, Reject, Edit (inline), Specialize (change instance)
- Bulk actions: Confirm All, Reject All
- Visual status indicators (green=confirmed, red=rejected, yellow=pending)

### FR-3: Rule Review Panel
- Display proposed rules after fact confirmation
- Show IF/THEN/BECAUSE in structured format
- Per-rule actions: Confirm, Reject, Edit BECAUSE
- Display both positive and RULEOUT rules with visual distinction

### FR-4: Root Cause Confirmation
- Simple dialog or panel for root cause confirmation/edit/reject

### FR-5: GAP Rule Display
- Show detected GAP rules with REQUIRES/PRODUCES/NOTE
- Per-gap actions: Confirm, Edit NOTE, Reject

### FR-6: Knowledge Base Browser
- **Rules tab:** List all rules with columns: ID, Status, Type, Conditions summary, Then summary
  - Filterable by status (CONFIRMED/GAP/RESOLVED) and type (positive/ruleout)
  - Click to expand full rule details
- **Ontology tab:** Tree or list view of nouns and their properties
- **Root Causes tab:** List of known root causes

### FR-7: Rule Evaluation Panel
- Input area for facts (text input or select from known facts)
- "Evaluate" button runs the evaluation engine
- Results display:
  - Fired rules list
  - Root causes identified (highlighted green)
  - Root causes ruled out (highlighted red)
  - GAP rules encountered (highlighted yellow)
  - Rule chain trace (expandable tree or timeline)

### FR-8: Data Directory Selection
- Settings/preferences for selecting the data directory
- Default: `data/` relative to working directory

## Non-Functional Requirements
- **Responsive UI:** LLM calls run in a background thread; UI remains responsive with progress indicator
- **Interoperable:** Same YAML files as CLI — user can switch between CLI and GUI freely
- **Single-window:** Tabbed or panel-based layout in a single window
- **No installer required:** Run directly with `python -m ees.gui` or `ees-gui` entry point

## Proposed Approach

### GUI Framework: Tkinter
**Rationale:**
- Ships with Python standard library — zero additional dependencies
- Adequate for this use case (forms, tables, tree views, file dialogs)
- Windows-native look with `ttk` themed widgets
- Simple to package and distribute
- Consistent with the project's minimal-dependency philosophy

**Alternatives considered:**

| Alternative | Reason Rejected |
|-------------|----------------|
| PyQt6/PySide6 | Heavy dependency (~150MB), GPL/LGPL licensing complexity, overkill for this UI |
| CustomTkinter | Extra dependency, cosmetic-only benefits |
| Dear PyGui | GPU-based, heavy, not standard |
| Web app (Flask/Streamlit) | Out of scope per user story (desktop app) |

### Architecture

```
src/ees/
├── gui/
│   ├── __init__.py
│   ├── app.py              # Main application window (Tk root)
│   ├── incident_panel.py   # FR-1: Incident loading
│   ├── fact_panel.py       # FR-2: Fact review table
│   ├── rule_panel.py       # FR-3: Rule confirmation
│   ├── eval_panel.py       # FR-7: Evaluation interface
│   ├── browser_panel.py    # FR-6: Knowledge base browser
│   └── workers.py          # Background thread workers for LLM calls
```

### Step 1: Application Shell (`app.py`)
- `Tk()` root window with notebook (tabs) for main sections
- Tabs: "Process Incident", "Knowledge Base", "Evaluate"
- Menu bar: File (Open data dir, Exit), Help (About)
- Status bar at bottom

### Step 2: Process Incident Tab
- Left panel: File browser + incident text display
- Right panel: Fact review table → Rule review → Root cause → GAP review
- Sequential workflow guided by state (load → extract → confirm facts → confirm rules → save)
- LLM extraction runs in `threading.Thread` with progress indicator

### Step 3: Knowledge Base Tab
- Sub-tabs: Rules, Ontology, Root Causes
- Rules: `ttk.Treeview` with sortable columns, filter dropdowns
- Ontology: `ttk.Treeview` in tree mode (noun → properties)
- Root Causes: Simple listbox

### Step 4: Evaluate Tab
- Text entry for facts (one per line, or semicolon-delimited)
- "Evaluate" button triggers `RuleEvaluator.evaluate()`
- Results displayed in structured panels (fired rules, root causes, ruleouts, gaps, trace)

### Step 5: Background Workers (`workers.py`)
- `threading.Thread` wrapper for LLM calls
- Uses `queue.Queue` or `root.after()` for thread-safe UI updates
- Progress indicator (indeterminate progress bar during LLM call)

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Tkinter layout complexity for multi-panel UI | Use `ttk.PanedWindow` and `ttk.Notebook` for clean layout. Keep panels simple. |
| Thread-safety for Tkinter | All UI updates via `root.after()` callback. Worker threads only produce results, never touch widgets. |
| Large rule sets may slow Treeview | Lazy loading / pagination if needed. For V1, load all — scale concern is minimal for expected data sizes. |
| LLM call failures during GUI operation | Show error dialog, don't crash. Same error handling as CLI. |

## Open Questions
None — all major decisions addressed in user story and this design.

## Dependencies
- EES-00001 through EES-00004 (all complete)
- Python `tkinter` (standard library)
- No new external dependencies

## Migration / Rollout / Rollback
- **Additive:** New `src/ees/gui/` package. No changes to existing modules.
- **Entry point:** Add `ees-gui = "ees.gui.app:main"` to `pyproject.toml`
- **Rollback:** Remove the `gui/` package. No data migration needed.

## Observability Plan
- Status bar shows operation counts (facts confirmed, rules saved, evaluations run)
- Error dialogs for LLM failures, file I/O errors

## Test Strategy Summary
- **Unit tests:** GUI worker thread logic (fact parsing, result formatting) — testable without Tk
- **Unit tests:** Data transformation functions (model → table row conversion)
- **Integration tests:** Headless smoke tests using Tkinter's `update()` loop (if feasible)
- **Manual testing:** Visual verification of layout, interaction flow, and responsiveness
- **Note:** GUI tests are inherently harder to automate. Focus on testing the non-UI logic that mediates between GUI and engine.
