# EES-00016 Documentor Notes

## Documentation Updates
- **User Story**: Updated to remove all references to `string` type. Assumptions and acceptance criteria now reflect `enum|bool|long` only.
- **Design Doc**: Updated summary, problem statement, FR-1 code sample, FR-2 validation rules, NFRs, risks table, rollout/rollback, and test strategy table.
- **Test Cases**: Updated TC-16-14/15 (string → rejected), TC-16-16 (unknown → False), TC-16-19/20 (from_dict defaults to enum).
- **Review Comments**: Left as-is — historical record of the original review decision. The string removal was a post-implementation Project Owner decision.

## Accuracy Verification
- All code references in docs match the actual implementation.
- `OntologyProperty.VALID_TYPES = frozenset({"enum", "bool", "long"})` exists in code.
- `from_dict()` defaults to `"enum"` — confirmed in code and docs.
- `validate_value()` returns `False` for unknown types — confirmed.

## User Story Status
- Already marked **IMPLEMENTED** — confirmed.
