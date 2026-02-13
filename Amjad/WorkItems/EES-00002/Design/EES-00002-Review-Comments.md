# EES-00002 — Design Review Comments

## Review Summary

The design doc is clear, well-structured, and feasible. The phased approach (model → detection → refinement → integration → UX) is logical. Several findings below, mostly minor.

## Findings

### Major Findings

| ID | Finding | Severity | Recommendation |
|----|---------|----------|----------------|
| MJ-1 | **"Orphaned facts" definition is vague.** FR-1 says "confirmed facts that are NOT connected to the root cause through existing or newly-confirmed rules." How is "connected" determined? If a fact appears in a rule's conditions, is it connected? What about the rule's `then` — is that connected to the root cause? Single-hop vs multi-hop is acknowledged (OQ-1) but the exact algorithm needs to be specified by the architect. | High | Architect must define the exact graph traversal algorithm for "connected to root cause." |
| MJ-2 | **No root cause = no GAP detection.** The design states GAP detection checks if confirmed facts "lead to a root cause." What happens when the LLM proposes no root cause? The user story doesn't limit GAP detection to root-cause-present scenarios. | Medium | Clarify: if no root cause is confirmed, skip GAP detection entirely (simplest) or detect GAPs between disconnected fact clusters (complex, defer). |
| MJ-3 | **GAP refinement matching is underspecified.** FR-4 says "new rule's conditions match GAP's requires facts." Is this exact match or subset match? If a GAP requires facts {A, B} and a new rule's conditions are {A}, is that a partial match? | Medium | Architect must specify exact matching semantics. |

### Minor Findings

| ID | Finding | Severity | Recommendation |
|----|---------|----------|----------------|
| MN-1 | **`requires`/`produces` on Rule model vs separate GapRule class.** Adding optional fields to Rule keeps it simple but may confuse callers who expect all rules to have the same shape. | Low | Accept this tradeoff — document that `requires`/`produces`/`note` are only present when `status == "GAP"`. |
| MN-2 | **RESOLVED status not in acceptance criteria.** The design proposes `RESOLVED` status but the user story only mentions GAP and CONFIRMED. | Low | Acceptable — RESOLVED is an implementation detail of GAP lifecycle, not a user-visible requirement. |
| MN-3 | **No mention of the LLM system prompt update.** If GAP detection is deterministic and post-LLM, the LLM prompt doesn't need to change. But if GAP rules are added to the knowledge base, they'll appear in `list_rules()`. Should `filter_rules()` exclude GAP rules from dedup comparison? | Medium | Architect should decide: should `RuleGenerator.filter_rules()` skip GAP rules, or compare against them? |

## Questions for Architect

1. What is the exact algorithm for determining if a confirmed fact is "connected" to the root cause? (MJ-1)
2. When no root cause is confirmed, should GAP detection be skipped? (MJ-2)
3. What are the matching semantics for GAP refinement — exact, subset, or superset? (MJ-3)
4. Should `RuleGenerator.filter_rules()` exclude GAP rules from dedup comparison? (MN-3)

---

## Architect Notes

### MJ-1 Resolution: Orphaned Fact Detection Algorithm

**Decision: Single-hop, match_key-based connection check.**

A confirmed fact is "connected to the root cause" if and only if:
1. There exists a CONFIRMED rule (existing OR newly-confirmed from this incident) whose `conditions.items` include a fact matching via `Fact.match_key()`
2. AND that same rule's `then` clause represents the confirmed root cause: `rule.then.noun.lower() == "rootcause"` AND `rule.then.value.lower() == root_cause.lower()`

All confirmed facts NOT consumed by any such rule are "orphaned" and become the GAP's `requires` list.

Multi-hop chain analysis (fact → rule → intermediate → rule → root cause) is explicitly deferred to a future work item.

### MJ-2 Resolution: No Root Cause Behavior

**Decision: Skip GAP detection entirely when no root cause is confirmed.**

Rationale: GAPs bridge orphaned facts toward a known endpoint. Without a root cause, there is no endpoint to bridge toward. Detecting "disconnected fact clusters" is a separate, more complex feature (defer).

Implementation: `GapDetector.detect_gaps()` returns `[]` immediately if `root_cause is None`.

### MJ-3 Resolution: GAP Refinement Matching Semantics

**Decision: Subset matching using `Fact.match_key()`, scoped to single-hop.**

Refinement checks each existing GAP rule against newly-confirmed rules:
1. For each GAP rule, collect its `requires` facts as `set[match_key]`
2. For each new CONFIRMED rule whose `then` connects toward the GAP's `produces`, collect its conditions as `set[match_key]`
3. Compute `remaining = gap_requires_keys - new_rule_condition_keys`
4. If `remaining` is empty AND new rules bridge to produces: **RESOLVED** (status → `"RESOLVED"`, add incident to sources)
5. If `remaining` is smaller than original: **NARROWED** (update requires to remaining facts, add incident to sources)
6. If no overlap: no change

### MN-3 Resolution: filter_rules and GAP Exclusion

**Decision: `RuleGenerator.is_duplicate()` skips rules where `existing.status == "GAP"`.**

Rationale: A confirmed rule with the same conditions/then as a GAP is NOT a duplicate — it's the missing knowledge that the GAP represents. Treating it as a duplicate would prevent GAP resolution.

Implementation: Add `if existing.status == "GAP": continue` in `is_duplicate()`.

### Additional Architectural Decisions

**A-1: GAP Model Contract**
- `Rule.status` extends to `Literal["CONFIRMED", "GAP", "RESOLVED"]`
- New fields: `requires: list[Fact] = []`, `produces: list[Fact] = []`, `note: str = ""`
- `to_dict()`: only emit `requires`/`produces`/`note` when non-default (keeps CONFIRMED rule YAML clean)
- `from_dict()`: use `.get()` with defaults for backward compat
- GAP rules do NOT use `conditions`/`then` (kept at defaults) — use `requires`/`produces` instead

**A-2: requires/produces YAML Format**
Serialized as condition-item dicts (no `status` field), matching `RuleConditions.items` format:
```yaml
requires:
  - noun: Server
    instance: "*"
    property: CPUUsage
    operator: ">"
    value: "90"
produces:
  - noun: RootCause
    instance: "*"
    property: Name
    operator: "=="
    value: "Connection Pool Exhaustion"
```

**A-3: GapDetector Module Design**
- New `src/ees/gap_detector.py` with class `GapDetector`
- Pure logic: takes facts, rules, root cause → returns GAP rules and refinements
- No I/O — all YamlStore interaction remains in `main.py`
- Interface:
  - `detect_gaps(confirmed_facts, new_rules, root_cause, incident_id) → list[Rule]`
  - `check_refinements(new_rules, incident_id) → list[GapRefinement]`

**A-4: GapRefinement Result Type**
New dataclass in `models.py`:
```python
@dataclass
class GapRefinement:
    gap_rule_id: str
    action: Literal["narrowed", "resolved"]
    updated_rule: Rule
```

**A-5: R-007a/b/c Decomposition Pattern Deferred**
The `expert-system-decisions.md` shows a 3-rule decomposition with synthetic intermediate facts (`GAP-007 = TRUE`). EES-00002 uses a simpler single-GAP-rule approach (requires/produces on one rule). The decomposition pattern is an optimization for multi-hop analysis in a future work item.

**A-6: One GAP Rule Per Incident Maximum**
For single-hop detection, at most one GAP rule is created per incident (all orphaned facts are grouped into one GAP). Future work could split into multiple targeted GAPs.

**A-7: Integration Point in main.py**
GAP detection inserts between step 6 (rule confirmation) and step 7 (ontology update):
1. Create `GapDetector(existing_rules)`
2. Call `detect_gaps(confirmed_facts, confirmed_rules, root_cause, incident_id)`
3. Call `check_refinements(confirmed_rules, incident_id)`
4. Present GAP rules for user confirmation (c/e[note]/r)
5. Persist confirmed GAP rules via YamlStore
6. Report: "GAPs: X created, Y narrowed, Z resolved"
