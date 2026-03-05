# GCP-0048 — Project Owner Assistant Decision Notes

## Decision Summary
User story was pre-authored as part of GCP-0048–0052 subagent initiative batch. Reviewed and validated.

## Key Decisions
1. **Scope validated**: 10 role files get YAML front-matter; TechBestPractices.md is excluded per user story assumption
2. **6 ACs confirmed testable**: AC1 (front-matter exists), AC2 (no implicit refs), AC3 (explicit paths), AC4 (output_validator backward compat), AC5 (new test file), AC6 (outputs consistency)
3. **Backward compatibility constraint**: `output_validator.py` uses `re.search(r'##\s*Required\s*Outputs\s*\n(.*?)(?=\n##|\Z)')` to parse outputs — YAML front-matter at top of file will NOT affect this parser
4. **Cross-cutting issues identified during analysis**: TechBestPractices path is wrong (`.github/roles/` vs actual deploy location), QA has casing inconsistency (`Design-Doc.md` vs `design-doc.md`), refactor output filename mismatch (`{id}-refactor.md` vs `{id}-refactor-expert.md`). These are pre-existing issues — fix opportunistically within scope.

## Assumptions Validated
- GCP-0047 role improvements are already shipped (v2.102.0+ headers confirm this)
- Deployed copies (`.github/roles/`) are updated via bootstrap — out of scope for this work item per user story
