# EES-00004 — Program Manager Decision Notes

## Design Decisions

### D-1: Forward Chaining Algorithm
Forward chaining is the right fit for flat AND/OR rules. Starting from input facts, iteratively fire rules and add derived facts until convergence. This naturally handles dependency order without explicit sorting.

### D-2: match_key()-Based Matching
Reuses existing `Fact.match_key()` for condition matching — consistent with how dedup and GAP detection work. Operators are compared as strings, not numerically evaluated.

### D-3: Separate Module (`rule_evaluator.py`)
Evaluation is a distinct concern from learning. New module keeps the separation clean and is independently testable.

### D-4: EvaluationResult Model
Structured output with all necessary fields for reporting. Includes trace for auditability.

### D-5: Read-Only Operation
Zero writes to persisted data. Safe to run repeatedly without side effects.

### D-6: Dual Input Modes
`--facts` for quick CLI testing, `--facts-file` for structured input. Both parse through `Fact.parse()`.

## Files Affected
- `src/ees/models.py` — EvaluationResult dataclass
- `src/ees/rule_evaluator.py` — NEW module
- `src/ees/main.py` — `evaluate` subcommand
