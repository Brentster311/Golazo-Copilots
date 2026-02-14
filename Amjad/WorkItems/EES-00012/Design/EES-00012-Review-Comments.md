# EES-00012 — Review Comments

## C-1: `rules_to_rows()` v1 code will crash on v2 RuleOutput (Critical)

**Location:** `src/ees/gui/adapters.py` lines 44-55  
**Issue:** Accesses `r.then.noun`, `r.then.instance`, `r.then.property`, `r.then.value` which don't exist on `RuleOutput`. Also checks `r.type == "ruleout"` which is a deprecated v1 field.  
**Recommendation:** Use `_then_display()` (already exists at line 81-84) and rewrite `rules_to_rows()` to use `rule.then.kind` / `rule.then.description`. Add `else` key.

## C-2: `_show_rule_detail()` references all v1 attributes (Critical)

**Location:** `src/ees/gui/app.py` lines 800-836  
**Issue:** References `rule.type`, `rule.then.value`, `rule.then.noun`, `rule.then.instance`, `rule.then.property`, `rule.requires`, `rule.produces`, `rule.note`. All are deprecated v1 attrs.  
**Recommendation:** Rewrite to show `rule.then.kind(rule.then.description)` and `rule.else_` if present.

## C-3: `eval_result_to_display()` uses deprecated backward-compat properties (Medium)

**Location:** `src/ees/gui/adapters.py` lines 87-103  
**Issue:** Uses `result.root_causes`, `result.ruled_out`, `result.gap_rules` (deprecated backward-compat properties). Doesn't expose branch info (THEN vs ELSE).  
**Recommendation:** Use `result.outputs` list which has `{rule_id, branch, output}` entries. Group by output kind for display.

## C-4: `_format_eval_display()` missing branch info (Medium)

**Location:** `src/ees/gui/app.py` lines 839-878  
**Issue:** Only shows fired rules and their `then` but doesn't indicate whether THEN or ELSE branch fired.  
**Recommendation:** Include `(THEN)` or `(ELSE)` marker after each fired rule's output.

## C-5: No "else" column in rules treeviews (Low)

**Location:** `src/ees/gui/app.py` lines 189-199, 460-473  
**Issue:** Only 4 columns (proposed) / 6 columns (KB). Neither includes ELSE branch display.  
**Recommendation:** Add "else" column. Display blank for rules without `else_`.

## C-6: No live LLM extraction status (Feature Gap)

**Location:** `src/ees/fact_extractor.py`, `src/ees/gui/app.py` line 280  
**Issue:** `status_var.set("Extracting facts via LLM...")` is static. Multi-turn extraction can take 30+ seconds with no progress indication.  
**Recommendation:** Add `on_status` callback to `FactExtractor.extract()`. Wire in GUI via `root.after(0, ...)`.

---

## Architect Notes

### A-1: Capability Impact Assessment

Files affected: `fact_extractor.py`, `adapters.py`, `app.py`.  
**Directly affected capabilities:** `fact-extraction`, `gui`.  
**Transitively affected:** `cli-orchestration`.  
Contract preservation: `FactExtractor.extract()` signature gains an optional keyword-only `on_status` param — fully backward compatible. `rules_to_rows()` output dict gains an `else` key — callers that destructure specific keys are unaffected. `eval_result_to_display()` output dict structure changes to use `outputs` grouping — `_format_eval_display()` must be updated in lockstep.

### A-2: Thread-Safety of `on_status` Callback

The callback is invoked from the worker thread (inside `do_extract()`). The GUI wires it via `root.after(0, self.status_var.set, msg)` which is the standard Tkinter thread-safe pattern. No additional synchronization needed.

### A-3: `on_status` Error Isolation

If the `on_status` callback raises an exception, it should not crash the extraction loop. Wrap each `on_status(msg)` call in a try/except to isolate status reporting failures from extraction logic.

### A-4: `_then_display()` Promotion

Moving `_then_display()` from a nested function inside `eval_result_to_display()` to a module-level helper is architecturally correct — it eliminates duplication and makes it testable in isolation.

### A-5: `eval_result_to_display()` Contract Change

Current return dict keys: `input_facts`, `fired_rules`, `root_causes`, `ruled_out`, `gap_rules`, `trace`.  
Proposed new structure should use `outputs` list with `{rule_id, branch, kind, description}` entries. The deprecated `root_causes`, `ruled_out`, `gap_rules` keys should be preserved for backward compatibility until the `_format_eval_display()` is updated — then they can be removed in one pass since the only consumer is in `app.py`.

### A-6: No Security/Privacy Concerns

All changes are display-layer and callback-plumbing. No new external calls, no new data flows, no credential handling changes.
