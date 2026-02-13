# EES-00005 — Architect Decision Notes

## QA Finding Resolutions

| Finding | Resolution | Rationale |
|---------|-----------|-----------|
| MJ-1: Fact editing in Treeview | **Edit dialog** | Tkinter Treeview has no native inline editing. Modal dialog with form fields is simpler, reliable, and consistent. |
| MJ-2: Test automation scope | **Adapter pattern** | Adapter functions (model → display) are pure Python, testable without Tk. Workers testable via callback pattern. Widget interaction is manual. |
| MN-1: Eval fact input format | **One per line** | More natural in multiline text widget. Converted internally. |
| MN-2: Worker error propagation | **Callback pattern** | `on_complete(result)` + `on_error(exception)` callbacks. UI schedules error dialog via `root.after()`. |
| MN-3: Rule browser performance | **Client-side filter** | Load all, filter in memory. Adequate for expected scale. |

## Architectural Decisions

### AD-1: Dependency Direction
GUI → Engine (never reverse). CLI remains fully functional without GUI package. Engine modules have zero GUI imports.

### AD-2: Adapter Layer (`adapters.py`)
Pure functions converting engine models to display-ready tuples/dicts. This is the automated test seam. Functions:
- `facts_to_rows(facts) -> list[tuple]`
- `rules_to_rows(rules) -> list[tuple]`
- `ontology_to_tree(nouns) -> list[dict]`
- `eval_result_to_display(result) -> dict`
- `filter_rules(rules, status, rule_type) -> list[Rule]`

### AD-3: Threading Safety
All Tk widget manipulation happens on the main thread via `root.after()`. Worker threads only produce data or errors — never touch widgets.

### AD-4: No Engine Modifications
GUI calls existing engine APIs directly. This is additive-only — no blast radius to existing functionality.

## Security/Privacy
- No new credentials handling — GUI uses same `FactExtractor` which handles Azure auth
- File dialogs respect OS-level permissions
- No network activity beyond existing LLM calls

## Capability Impact
- 7 capabilities transitively affected but NO contract changes needed
- New `gui` capability to be added to capabilities.yaml

## Approval
**Approved** — Design is architecturally sound. Adapter pattern provides clean test seam. No existing contracts affected.
