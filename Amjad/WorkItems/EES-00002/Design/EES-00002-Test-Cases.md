# EES-00002 — Test Cases

## Test Matrix

Maps to Acceptance Criteria from the User Story and Functional Requirements from the Design Doc.

---

### GAP Detection (FR-1, AC-1)

| TC | Description | Input | Expected | AC |
|----|-------------|-------|----------|-----|
| TC-01 | GAP created when confirmed fact doesn't connect to root cause | Facts: [A], Root cause: RC, Rules: [A→RC missing] | 1 GAP rule with requires=[A], produces=[RC-related] | AC-1 |
| TC-02 | No GAP when all facts connect to root cause through rules | Facts: [A,B], Rules: [IF A AND B THEN RC] | 0 GAP rules | AC-1 |
| TC-03 | No GAP when no root cause is confirmed | Facts: [A,B], Root cause: None | 0 GAP rules (detection skipped) | AC-1 |
| TC-04 | Multiple orphaned facts produce a single GAP | Facts: [A,B,C], Rules cover only [A], root cause present | 1 GAP rule with requires containing orphaned facts | AC-1 |
| TC-05 | No confirmed facts → no GAP detection | Facts: [], Root cause: RC | 0 GAP rules | AC-1 |
| TC-06 | All facts rejected → no GAP detection | Confirmed facts: [] | 0 GAP rules | AC-1 |

### GAP Rule Model (FR-2, AC-5)

| TC | Description | Input | Expected | AC |
|----|-------------|-------|----------|-----|
| TC-07 | GAP rule has required fields: requires, produces, note | Create GAP rule | rule.requires is list, rule.produces is list, rule.note is str | AC-5 |
| TC-08 | GAP rule status is "GAP" | Create GAP rule | rule.status == "GAP" | AC-5 |
| TC-09 | GAP rule roundtrip serialization | GAP rule → to_dict → from_dict | Identical rule restored | AC-5 |
| TC-10 | CONFIRMED rule without GAP fields loads cleanly | Existing CONFIRMED rule YAML (no requires/produces) | Rule loads, requires=[], produces=[], note="" | AC-5 |

### GAP Persistence (FR-3, AC-2)

| TC | Description | Input | Expected | AC |
|----|-------------|-------|----------|-----|
| TC-11 | GAP rule saved to rules/ directory | Save GAP rule via YamlStore | File exists at rules/R-NNN.yaml with status: GAP | AC-2 |
| TC-12 | GAP rule loaded alongside CONFIRMED rules | Save 1 CONFIRMED + 1 GAP, list_rules() | Returns both rules; distinguish by status | AC-2 |
| TC-13 | GAP rule YAML contains source incident IDs | Save GAP rule | YAML contains sources: [INC-NNN] | AC-2 |

### GAP Refinement (FR-4, AC-3, AC-4)

| TC | Description | Input | Expected | AC |
|----|-------------|-------|----------|-----|
| TC-14 | Full GAP resolution: new rules fully bridge requires→produces | GAP requires=[A], produces=[RC]; new rule IF A THEN RC | GAP status → RESOLVED, reported to user | AC-3, AC-4 |
| TC-15 | Partial GAP narrowing: new rules fill part of the gap | GAP requires=[A,B], new rule covers A only | GAP narrowed (requires reduced), sources updated | AC-3, AC-4 |
| TC-16 | No refinement when new rules don't overlap with any GAP | GAP requires=[A], new rule covers [C] | GAP unchanged | AC-3 |
| TC-17 | Multiple GAPs checked during refinement | 2 GAP rules, new rule overlaps with 1 | Only overlapping GAP is refined | AC-3 |
| TC-18 | Resolved GAP preserves source incident provenance | GAP from INC-001, resolved by INC-002 | RESOLVED rule sources: [INC-001, INC-002] | AC-3, NFR |

### GAP Reporting (FR-5, AC-4)

| TC | Description | Input | Expected | AC |
|----|-------------|-------|----------|-----|
| TC-19 | Report shows GAP rules created | 1 GAP detected | Output contains "GAPs: 1 created" | AC-4 |
| TC-20 | Report shows GAP rules narrowed | 1 GAP narrowed | Output contains "narrowed" | AC-4 |
| TC-21 | Report shows GAP rules resolved | 1 GAP resolved | Output contains "resolved" | AC-4 |
| TC-22 | Report shows no GAP activity when none detected | No GAPs | Output contains "GAPs: 0 created" or omitted | AC-4 |

### User Confirmation of GAPs (Design: Phase 5)

| TC | Description | Input | Expected | AC |
|----|-------------|-------|----------|-----|
| TC-23 | User confirms GAP rule | Input: "c" | GAP rule saved | AC-1 |
| TC-24 | User rejects GAP rule | Input: "r" | GAP rule discarded | AC-1 |
| TC-25 | User edits GAP note | Input: "e", new note | GAP saved with updated note | AC-1 |

### Edge Cases

| TC | Description | Input | Expected | AC |
|----|-------------|-------|----------|-----|
| TC-26 | Backward compat: old CONFIRMED rules (no requires/produces) load | Pre-GAP YAML files | Load without error | AC-5 |
| TC-27 | GAP rule is not considered a duplicate of CONFIRMED rule | GAP and CONFIRMED with same conditions | Both exist in knowledge base | AC-2 |
| TC-28 | filter_rules excludes GAP rules from dedup comparison | Pending architect decision (MN-3) | TBD | — |
