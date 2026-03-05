# EES Grammar — Keyword Reference

*Source: EES-00019 — Structured Expert System Language*

The EES rule language uses exactly **10 keywords**. No others are permitted. Rules are serialized as YAML that mirrors the AST tree, and the forward-chaining evaluator processes them until working memory stabilizes (fixed-point) or a goal is resolved.

---

## 1. `RULE`

**Category:** Structure  
**AST node:** `RuleBlock`

The top-level container for an expert system rule. Every rule has a unique `rule_id` (e.g. `R-001`) and a single `Block` of statements that form its body.

```yaml
rule_id: R-001
block:
  - ...statements...
```

**Semantics:** During forward-chaining evaluation, rules are sorted by `rule_id` and executed sequentially in each iteration. A rule is the unit of organization — each rule encapsulates a single piece of diagnostic reasoning.

---

## 2. `BEGIN` / 3. `END`

**Category:** Structure  
**AST representation:** Implicit — `Block` boundaries

`BEGIN` and `END` are the conceptual delimiters of a block of statements. In the YAML serialization they are implicit (a YAML list represents a block), but they are part of the canonical grammar specification to make the language's block structure explicit.

- A `Block` contains an ordered list of statements (`list[Stmt]`)
- Blocks appear as the body of a `RULE`, and as the `then` / `else` branches of a `DECIDE`
- Blocks are recursive — a `DECIDE` inside a block creates nested blocks

**Semantics:** Statements within a block execute sequentially, top to bottom.

---

## 4. `CHECK`

**Category:** Query (read-only)  
**AST node:** `CheckExpr`

Tests whether a fact exists in working memory. A `CHECK` expression specifies a full fact pattern: `Noun(instance).Property operator value`.

```yaml
check:
  noun: User
  instance: $u
  property: adminRole
  operator: "=="
  value: unknown
```

**Semantics:**
- For `==`: returns `True` if a fact with matching `(noun, instance, property, operator, value)` exists in working memory.
- For `!=`: returns `True` if no exact-match fact exists.
- For `>`, `>=`, `<`, `<=`: finds a fact matching `(noun, instance, property)` and compares the numeric values.
- For `contains` / `!contains`: finds a fact matching `(noun, instance, property)` and tests substring containment.

**Constraint:** `CHECK` cannot appear as a standalone statement — it must always be paired with a `DECIDE`. A bare `CHECK` without `DECIDE` is a parse error.

---

## 5. `DECIDE`

**Category:** Control flow  
**AST node:** `DecideStmt`

Branches execution based on a `CHECK` result. Contains exactly one `CHECK` expression and exactly two blocks: `then` (condition met) and `else` (condition not met).

```yaml
- check:
    noun: User
    instance: $u
    property: adminRole
    operator: "=="
    value: unknown
  decide:
    then:
      - assert:
          noun: User
          instance: $u
          property: adminRole
          operator: "=="
          value: confirmed
    else:
      - noop: true
```

**Semantics:**
1. Evaluate the `CHECK` expression against working memory → boolean result
2. If `True`: execute the `then` block
3. If `False`: execute the `else` block
4. Both branches are required — use `NOOP` for an intentionally empty branch
5. The CHECK result and branch taken are recorded in the reasoning trace

**Nesting:** `DECIDE` blocks can contain other `DECIDE` statements, enabling arbitrarily deep decision trees within a single rule.

---

## 6. `ASSERT`

**Category:** Memory mutation (write)  
**AST node:** `AssertStmt`

Adds or overwrites a fact in working memory. This is one of only two keywords that modify working memory (the other is `RETRACT`).

```yaml
- assert:
    noun: User
    instance: $u
    property: adminRole
    operator: "=="
    value: confirmed
```

**Semantics:**
- Creates a `Fact` from the specified fields and inserts it into working memory using its `match_key()` — the tuple `(noun, instance, property)`.
- If a fact with the same match key already exists, it is **overwritten** (upsert behavior).
- The ASSERT is recorded in the reasoning trace with the full fact string.
- Forward chaining continues until no new ASSERTs (or RETRACTs) change working memory across a full iteration (fixed-point convergence).

---

## 7. `RETRACT`

**Category:** Memory mutation (delete)  
**AST node:** `RetractStmt`

Removes facts from working memory. This is one of only two keywords that modify working memory (the other is `ASSERT`).

```yaml
- retract:
    noun: User
    instance: $u
    property: adminRole
```

**Semantics:**
- Matches on `(noun, instance, property)` only — removes **all** facts matching those three fields, regardless of operator or value.
- Matching is case-insensitive on `noun` and `property`.
- If no matching fact exists, it is a silent no-op (no error).
- Each removed fact is individually recorded in the reasoning trace.

---

## 8. `ACT`

**Category:** Side-effect (external action)  
**AST node:** `ActStmt`

Represents an external side-effect or recommended action — something the system should do outside of its own reasoning (e.g., "Escalate to Exchange team", "Send notification to admin").

```yaml
- act: "Escalate to Exchange team for manual verification"
```

**Semantics:**
- **Does not modify working memory.** ACT is trace-only.
- The description string is recorded in the reasoning trace so that the diagnostic output includes actionable recommendations.
- At evaluation time, ACT serves as documentation of what a human or external system should do when this branch of reasoning is reached.

---

## 9. `NOOP`

**Category:** Placeholder  
**AST node:** `NoopStmt`

Explicit no-operation. Does nothing and modifies nothing.

```yaml
- noop: true
```

**Semantics:**
- Recorded in the reasoning trace (so you can see that this branch was entered and deliberately chose to do nothing).
- Primary use case: the `else` (or `then`) branch of a `DECIDE` when one branch requires action but the other does not. Both branches are required, so `NOOP` fills the intentionally-empty branch.

---

## 10. `GAP`

**Category:** Terminal signal  
**AST node:** `GapStmt`

Marks unknown or missing reasoning — "we don't know this, and it needs investigation." GAP is a terminal signal indicating the rule's reasoning has reached a point of uncertainty.

```yaml
- gap: "Admin role could not be confirmed — manual investigation needed"
```

**Semantics:**
- **Does not modify working memory.** GAP is trace-only.
- Recorded in the reasoning trace with its description.
- When a `Goal` is active, a GAP firing in any iteration causes the evaluator to immediately return with `goal_status="escalated"` — meaning the system cannot resolve the diagnosis and must hand off.
- GAPs are the system's way of saying "I've hit the boundary of what I can reason about."

---

## Summary Table

| Keyword | Category | Modifies WM? | AST Node | Purpose |
|---------|----------|:---:|----------|---------|
| `RULE` | Structure | No | `RuleBlock` | Top-level named container |
| `BEGIN` | Structure | No | `Block` (implicit) | Start of statement block |
| `END` | Structure | No | `Block` (implicit) | End of statement block |
| `CHECK` | Query | No | `CheckExpr` | Test a fact in working memory |
| `DECIDE` | Control flow | No | `DecideStmt` | Branch on CHECK result |
| `ASSERT` | Mutation | **Yes** | `AssertStmt` | Add/update a fact |
| `RETRACT` | Mutation | **Yes** | `RetractStmt` | Remove facts |
| `ACT` | Side-effect | No | `ActStmt` | Record external action |
| `NOOP` | Placeholder | No | `NoopStmt` | Intentional no-op |
| `GAP` | Terminal | No | `GapStmt` | Flag missing reasoning |

## Evaluation Model

The forward-chaining evaluator repeats this cycle:

1. Execute all rules (sorted by `rule_id`) against working memory
2. Each rule's block is executed top-to-bottom
3. `DECIDE` evaluates its `CHECK` and enters the appropriate branch
4. `ASSERT` / `RETRACT` mutate working memory
5. `ACT`, `NOOP`, `GAP` are recorded in the trace only
6. After all rules execute, compare working memory to the pre-iteration snapshot
7. If unchanged → **fixed-point reached**, stop
8. If a `Goal` is declared and resolved → stop with `goal_status="resolved"`
9. If a `GAP` fired and a `Goal` is active → stop with `goal_status="escalated"`
10. Otherwise → repeat (up to `max_iterations`, default 100)
