# EES-00001 — Architect Decision Notes

## Architectural Review Summary

Reviewed the design doc and QA review comments for EES-00001 (Core Learning Loop). All 3 critical and 5 major findings have been resolved with design doc updates. Architectural decisions below.

---

## Key Architectural Decisions

### AD-1: LLM Proposes Complete Rules (not just facts)
**Decision:** The LLM generates both extracted facts AND proposed IF/THEN rules with BECAUSE clauses. The user confirms in two phases: facts first, then rules.

**Rationale:** Building a rule composition algorithm would be the hardest part of the system and would likely produce worse results than an LLM that understands the incident narrative. The human-in-the-loop confirmation ensures quality while leveraging LLM reasoning for the complex step.

**Trade-off:** More dependence on LLM quality for rule coherence, but avoids inventing a combinatorial rule generation algorithm for v1.

### AD-2: Azure OpenAI as LLM Provider
**Decision:** Use Azure OpenAI Service via the `openai` Python package (Azure mode) with `azure-identity` for auth.

**Auth:** `ChainedTokenCredential(AzureCliCredential(), ManagedIdentityCredential())` per TechBestPractices.md. `DefaultAzureCredential` is explicitly forbidden.

**Models:** GPT-4o, GPT-4-turbo, GPT-5 series — model is determined by Azure deployment name, not hardcoded.

**Configuration:** Environment variables for `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_DEPLOYMENT`.

**Rationale:** Native Azure Identity integration. Model flexibility via deployment config. Enterprise-grade content filtering and data residency. Same `openai` SDK.

**Alternative considered:** GitHub Copilot API (viable, uses GitHub token auth). Rejected for v1 in favor of Azure OpenAI's deployment control and model selection flexibility.

**Risk:** Azure subscription dependency. Mitigated by keeping the LLM call isolated in `fact_extractor.py` — swapping providers requires changing only that module.

### AD-3: ruamel.yaml over PyYAML
**Decision:** Use `ruamel.yaml` for all YAML operations.

**Rationale:** ruamel.yaml preserves comments and formatting on round-trip. Since these YAML files will be human-readable records, preserving structure matters. PyYAML strips comments.

### AD-4: Five-Component Architecture
**Decision:** Split into 5 clearly bounded components:
1. **Incident Loader** — file I/O and validation
2. **Fact Extractor** — LLM prompt construction, API call, response parsing, user confirmation of facts
3. **Rule Generator** — user confirmation of rules, deduplication
4. **Ontology Manager** — ontology CRUD, matching existing entries, suggesting reuse
5. **YAML Persistence** — atomic write of all YAML files at end of workflow

**Rationale:** Each component has a single responsibility. Testable in isolation with clear interfaces. The separation of extraction (LLM-dependent) from persistence (pure I/O) enables thorough unit testing without LLM calls.

### AD-5: Atomic Persistence at End of Workflow
**Decision:** No YAML files are written until all user confirmations are complete and all data is validated.

**Rationale:** Prevents partial/corrupt state from interrupted sessions. All-or-nothing write ensures data integrity.

**Risk:** If the process crashes after confirmation but before write, work is lost. Acceptable for v1 CLI tool; could add write-ahead logging in future.

### AD-6: Sequential ID Generation
**Decision:** `INC-<NNN>` for incidents, `R-<NNN>` for rules. Auto-increment by scanning existing files.

**Rationale:** Simple, human-readable, no external dependencies. File-scanning approach works for single-user local tool.

**Risk:** Concurrent users could generate duplicates. Not a concern for v1 (single-user, local files).

### AD-7: Root Causes Are Not Parameterized
**Decision:** Root causes are type-level concepts (e.g., "Resource Exhaustion"), not instance-specific. No specialize (s) action for root cause confirmation.

**Rationale:** The root cause describes *what happened*, not *where it happened*. Instance-specific context lives in the rule conditions. This keeps the root cause model simple and avoids explosion of near-identical root cause entries.

---

## QA Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| CR-1 | Critical | FR-2 format corrected |
| CR-2 | Critical | Summary format corrected |
| CR-3 | Critical | Incident YAML schema completed |
| MJ-1 | Major | Error handling section added (file validation) |
| MJ-2 | Major | LLM failure recovery strategy added |
| MJ-3 | Major | Rule Generation Strategy section added |
| MJ-4 | Major | Root cause non-parameterized, clarified |
| MJ-5 | Major | Input validation for edited facts added |
| MN-1 | Minor | Deferred — instance tracking not needed for v1 |
| MN-2 | Minor | Deferred — fact-level provenance not needed for v1 |
| MN-3 | Minor | Exact duplicate check accepted; fuzzy deferred |

---

## Open Questions (Resolved)

| Question | Answer |
|----------|--------|
| LLM proposes rules or just facts? | Complete rules (AD-1) |
| LLM output format? | JSON structured output (AD-2) |
| ID generation? | Sequential file-scan (AD-6) |
| LLM provider? | OpenAI GPT-4o (AD-2) |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM returns poor quality rules | Medium | Medium | Human confirms all rules; can edit or reject |
| OpenAI API changes/outage | Low | High | LLM isolated in single module; swap possible |
| Azure subscription unavailable | Low | High | ChainedTokenCredential fails fast with clear error |
| YAML corruption from crash | Low | Medium | Atomic writes; no partial state |
| Large incidents exceed token limits | Medium | Low | 500KB file warning; future chunking |

---

## No New User Stories Required

All QA findings were resolvable within existing scope. No behavioral or scope changes needed.
