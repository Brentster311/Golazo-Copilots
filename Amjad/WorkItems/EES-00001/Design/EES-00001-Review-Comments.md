# EES-00001 — Design Review Comments

## Review Summary
The design doc is well-structured and covers the required sections. The YAML schemas are concrete and the CLI flow is clear. Below are findings organized by severity.

---

## Critical — Must Address Before Implementation

### CR-1: FR-2 still references old format
**Location:** Design Doc, Functional Requirements table, FR-2
**Issue:** FR-2 says `Noun.Property = value` but should say `Noun(instance).Property operator value` to match the parameterized noun model.
**Recommendation:** Update FR-2 text.

### CR-2: Summary still references old format
**Location:** Design Doc, Summary paragraph
**Issue:** Summary says `` `Noun.Property = value` `` — should reference the parameterized format.
**Recommendation:** Update to `` `Noun(instance).Property operator value` ``.

### CR-3: Incident YAML schema is truncated
**Location:** Design Doc, YAML Schema Designs, incidents section
**Issue:** The incidents YAML example appears to be cut off — the `App` fact entry is incomplete (missing property, operator, value, status fields) and the closing ``` is missing before the rules schema starts.
**Recommendation:** Complete the incident schema example.

---

## Major — Should Address

### MJ-1: No error handling for invalid incident files
**Location:** Design Doc, Data Flow
**Issue:** What happens if the incident file doesn't exist, is empty, is binary, or is extremely large? No error cases are defined.
**Recommendation:** Add explicit error handling for: file not found, empty file, non-text file, file exceeding a reasonable size limit.

### MJ-2: LLM response parsing failure not covered
**Location:** Design Doc, LLM Integration
**Issue:** The LLM may return malformed output that doesn't parse into facts. No fallback or retry strategy is defined.
**Recommendation:** Define behavior when LLM returns unparseable output: retry, present raw text to user, or abort with clear error message.

### MJ-3: Rule generation logic is underspecified
**Location:** Design Doc, Architecture component 3 (Rule Generator)
**Issue:** How does the system decide which facts to combine into a single rule vs. separate rules? How does it decide AND vs. OR? How does it determine the THEN clause? This is the most complex piece and has the least detail.
**Recommendation:** Either specify the algorithm or explicitly state that the LLM proposes complete rules (not just facts) and the user confirms them.

### MJ-4: Specialize action on root cause not defined
**Location:** Design Doc, CLI Interaction Flow
**Issue:** Root cause confirmation offers `c/e/r` but no `s` (specialize). Is root cause always generalized? This should be explicit.
**Recommendation:** Clarify that root causes are not parameterized (they are type-level concepts, not instance-level), or add specialize if needed.

### MJ-5: Edited facts not re-validated
**Location:** Design Doc, CLI Interaction Flow
**Issue:** When a user edits a fact (option `e`), the edited text is accepted as-is. What if the user enters something unparseable as `Noun(instance).Property operator value`?
**Recommendation:** Add input validation for edited facts. Reject malformed input and re-prompt.

---

## Minor — Nice to Have

### MN-1: Ontology doesn't track instances
**Location:** Design Doc, ontology.yaml schema
**Issue:** The ontology tracks noun types and properties but not known instances. If a user specializes `Server(WebApp01)`, should `WebApp01` be tracked so it can be suggested for future incidents?
**Recommendation:** Consider adding an optional `known_instances` list to ontology nouns. Can be deferred if not needed for v1.

### MN-2: Rule provenance doesn't link to specific facts
**Location:** Design Doc, rules YAML schema
**Issue:** Rules track source incident IDs but not which specific facts from those incidents contributed. This makes it harder to trace rule origins precisely.
**Recommendation:** Consider adding fact references within sources. Deferrable.

### MN-3: No duplicate rule detection
**Location:** Design Doc, Rule Generator
**Issue:** Processing the same incident twice, or two similar incidents, could generate duplicate or near-duplicate rules. No deduplication strategy is mentioned.
**Recommendation:** Add at minimum a check for exact duplicate rules. Fuzzy dedup can be deferred.

---

## Questions for Architect

1. Should the LLM propose complete rules (IF/THEN with BECAUSE), or just facts which the system then composes into rules? (relates to MJ-3)
2. What structured output format should the LLM use? (JSON? YAML? Custom?)
3. How should incident IDs and rule IDs be generated?

---

## Architect Notes

### Resolutions

| Finding | Resolution | Design Doc Section |
|---------|------------|--------------------|
| CR-1 | FR-2 updated to `Noun(instance).Property operator value` | Functional Requirements |
| CR-2 | Summary updated to reference parameterized format | Summary |
| CR-3 | Incident YAML schema completed with App fact entry and proper closure | YAML Schema Designs |
| MJ-1 | Added explicit error handling: file not found, empty, binary, >500KB | Error Handling section |
| MJ-2 | Added LLM retry strategy: retry once, then save raw output and abort | Error Handling section |
| MJ-3 | LLM proposes complete rules (not just facts). Two-phase confirmation: facts then rules. | Rule Generation Strategy section |
| MJ-4 | Root causes are type-level concepts, not parameterized. Confirmation is c/e/r only. | Root Cause is Not Parameterized section |
| MJ-5 | Edited facts validated against `Noun(instance).Property operator value` pattern. Re-prompt up to 3x. | Error Handling section |

### Answers to QA Questions

1. **LLM proposes complete rules** with IF/THEN and BECAUSE clauses. The user reviews and confirms facts first, then rules. This avoids needing a rule composition algorithm — the LLM leverages its understanding of the incident narrative.

2. **JSON mode** via Azure OpenAI's structured output. A defined JSON schema ensures reliable parsing. See the LLM Response Format in the design doc's LLM Provider Decision section.

3. **Sequential IDs:** `INC-<NNN>` for incidents, `R-<NNN>` for rules. Auto-incremented by scanning existing files. Padded to 3 digits minimum. See ID Generation Strategy section.

### Architectural Decisions

- **LLM Provider:** Azure OpenAI Service via `openai` Python package (Azure mode). Models: GPT-4o, GPT-4-turbo, GPT-5 series — deployment-level choice.
- **Authentication:** `ChainedTokenCredential(AzureCliCredential(), ManagedIdentityCredential())` per TechBestPractices.md. `DefaultAzureCredential` is forbidden.
- **YAML Library:** `ruamel.yaml` instead of `PyYAML`. Rationale: preserves comments and formatting on round-trip, important for human-edited files.
- **Atomic Writes:** All YAML persistence deferred to end of workflow. No partial writes on error.
- **5 Components:** Incident Loader, Fact Extractor, Rule Generator, Ontology Manager, YAML Persistence — each with clear single responsibility.
- **Security:** Token-based auth via Azure Identity. No API keys in env vars. Incident data stays within Azure tenant boundary.

### Minor Findings Disposition

| Finding | Disposition |
|---------|-------------|
| MN-1 (Ontology instance tracking) | **Deferred** — not needed for v1. Can be added as enhancement. Tracked for EES-00002+. |
| MN-2 (Rule-to-fact provenance) | **Deferred** — rule provenance tracks incident IDs, sufficient for v1. |
| MN-3 (Duplicate rule detection) | **Accepted for v1 scope** — exact duplicate check added. Rule Generator will skip rules with identical conditions and conclusion. Fuzzy dedup deferred. |

### New Sections Added to Design Doc

1. **Rule Generation Strategy** — how LLM proposes rules, two-phase user confirmation
2. **Error Handling** — file validation, LLM failure recovery, input validation
3. **Root Cause is Not Parameterized** — clarifies type-level nature
4. **ID Generation Strategy** — sequential IDs for incidents and rules
5. **LLM Provider Decision** — OpenAI choice with rationale and JSON schema
6. **Project Structure** — full directory layout with all source modules
7. **Dependency Choices** — package table with version requirements and rationale
8. **Security & Privacy** — API key handling, data transmission awareness
