# EES-00005 — Review Comments

## Design Review

### Findings

| ID | Severity | Area | Finding | Recommendation |
|----|----------|------|---------|----------------|
| MJ-1 | Major | FR-2 | Fact editing inline in a Tkinter Treeview is non-trivial. ttk.Treeview doesn't natively support inline editing — requires custom Entry widget overlay. | Architect to confirm approach: either (a) double-click opens edit dialog, or (b) implement inline Entry overlay. Dialog is simpler and recommended for V1. |
| MJ-2 | Major | Test Strategy | Design doc says "GUI tests are inherently harder to automate" and suggests manual testing. This diverges from TDD-first requirement. Need to clarify what automated tests ARE expected. | Focus automated tests on: (1) GUI data adapter functions (model → display), (2) worker thread logic, (3) engine integration via `evaluate_facts` / `process_incident`. GUI widget tests deferred to manual verification. |
| MN-1 | Minor | FR-7 | Evaluate panel fact input format not fully specified — "one per line, or semicolon-delimited". Should pick one default. | Use one-per-line in the text area (more natural in GUI), convert to semicolons internally for `_parse_input_facts()`. |
| MN-2 | Minor | Architecture | `workers.py` module handles threading but error propagation pattern not specified. How does a worker report LLM errors back to the UI? | Worker should catch exceptions and post error result via `queue.Queue` or callback. UI displays error dialog. |
| MN-3 | Minor | FR-6 | Rule browser filtering by "source incident" may require parsing all rule YAML files to extract `sources` field. Performance concern with large rule sets. | For V1, load all rules at tab activation. Filter client-side. This is adequate for expected scale. |

### Overall Assessment
**Conditionally Approved** — Design is well-structured. MJ-1 and MJ-2 need architect resolution. Minor findings are clarification-level.

---

## Architect Notes

### MJ-1 Resolution: Fact Editing — EDIT DIALOG
Use a modal dialog for fact editing (not inline Treeview editing). Rationale:
- Tkinter `ttk.Treeview` has no native inline editing support. Custom overlay is fragile and complex.
- A simple dialog with fields (Noun, Instance, Property, Operator, Value) is straightforward and reliable.
- Same approach for specializing (pre-fill dialog with current values, focus on Instance field).
- **Action:** Implement `FactEditDialog` as a `tk.Toplevel` with form fields.

### MJ-2 Resolution: Test Automation Scope — ADAPTER PATTERN CONFIRMED
Automated tests target the adapter layer between engine models and GUI display:
- **Adapter functions:** `facts_to_rows(facts) -> list[tuple]`, `rules_to_rows(rules) -> list[tuple]`, `ontology_to_tree(nouns) -> list[dict]`, `eval_result_to_display(result) -> dict`
- **Worker functions:** `run_extraction(text, ontology, callback)`, `run_evaluation(facts, rules, callback)`
- These are pure Python functions, testable without Tk event loop.
- Widget interaction (click, dialog) is manually verified.
- **Action:** No design change. Developer creates `src/ees/gui/adapters.py` for adapter functions.

### MN-1 Resolution: Evaluation Fact Input — ONE PER LINE
GUI eval panel uses a multiline `tk.Text` widget. Each line is one fact string. Internally converted to `Fact.parse()` calls.

### MN-2 Resolution: Worker Error Propagation — CALLBACK PATTERN
Workers accept a `on_complete(result)` and `on_error(exception)` callback pair. Worker catches all exceptions and calls `on_error`. UI thread schedules dialog via `root.after()`.

### MN-3 Resolution: Rule Browser Performance — CLIENT-SIDE FILTER
Load all rules at tab activation via `YamlStore.list_rules()`. Filter in memory. Adequate for expected scale.

### Additional Architectural Notes

**AN-1: Module Boundary**
GUI package (`src/ees/gui/`) depends on engine modules but engine modules NEVER depend on GUI. This ensures CLI remains fully functional without GUI.

**AN-2: Adapter Module**
New `adapters.py` contains pure functions for converting engine models to display-ready data structures. This is the primary test seam for automated GUI-related tests.

**AN-3: No Engine Changes**
The GUI calls existing engine functions directly: `FactExtractor.extract()`, `RuleEvaluator.evaluate()`, `YamlStore.*`, `RuleGenerator.*`, `GapDetector.*`. No engine modifications needed.

**AN-4: Entry Point**
Add to `pyproject.toml`: `ees-gui = "ees.gui.app:main"`. Also runnable via `python -m ees.gui`.

**AN-5: Tkinter Availability**
Tkinter is included in standard Python on Windows. No additional install step. If running on minimal Python installs (Docker, etc.), Tkinter may be missing — but this is out of scope (Windows desktop target).

**AN-6: Capability Registry Update**
Add `gui` capability to `capabilities.yaml`. Depends on: data-models, yaml-persistence, fact-extraction, rule-generation, rule-evaluation, ontology-management.
