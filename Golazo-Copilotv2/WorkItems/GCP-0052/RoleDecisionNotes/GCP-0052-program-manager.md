# GCP-0052 Program Manager Decision Notes

**Work Item:** GCP-0052 — Subagent Handoff Protocol & Integration Testing  
**Role:** Program Manager  
**Date:** 2026-02-22

---

## Key Design Decisions

1. **Two distinct deliverables with clear separation** — The handoff protocol document is a human-readable reference; the integration test file is machine-verifiable. They complement each other: the document explains the "why" and "what," the tests enforce the "how."

2. **Tests call real tool functions, not mocks** — `gcp_transition` and `gcp_role_context` are exercised directly. Only the subagent's work (file creation) is simulated. This catches integration bugs at tool boundaries while keeping tests fast and deterministic.

3. **Role files loaded from package defaults** — Tests copy the actual role default files (with their real YAML front-matter) into `tmp_path`. This makes the tests authoritative: if front-matter changes, tests detect drift immediately.

4. **Handoff matrix derived from role front-matter** — Rather than hardcoding the artifact relationships, the protocol document's matrix is built by cross-referencing the `inputs:` and `outputs:` fields in each role's default file. This keeps the documentation in sync with the code.

5. **Three focused test cases** — Full 10-role workflow (TC1), negative/blocking case (TC2), and backward transition re-entry (TC3). Each tests a distinct aspect of the handoff protocol rather than one monolithic test.

## Approach Rationale

- The subagent initiative (GCP-0048/0049/0050) built the machinery but left it unverified as an integrated system. GCP-0052 closes that gap.
- The handoff protocol serves both as onboarding documentation and as the specification that the integration tests verify.
- Using `tmp_path` with no shared state ensures tests are isolated, parallelizable, and run in < 10 seconds.
- No production code changes are needed — this is purely documentation + verification.

## Risks Flagged

1. **Role front-matter changes could break tests** — Mitigated: that's intentional. Tests surface drift immediately, which is the point of integration testing.
2. **Test file may be large (~200-300 lines)** — Acceptable given it covers 10 role transitions. Helper functions keep it manageable.
3. **Handoff matrix may need updating as roles evolve** — The protocol document includes a note about deriving the matrix from front-matter, making updates straightforward.
