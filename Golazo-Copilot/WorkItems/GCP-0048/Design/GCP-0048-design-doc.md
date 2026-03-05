# GCP-0048 Design Document

## Summary
Add YAML front-matter metadata blocks to all 10 role markdown files in `golazo-copilot/src/golazo_copilot/roles/defaults/` and eliminate implicit cross-role references. This makes each role file self-contained so it can be handed to an isolated subagent without prior conversation context.

## Problem Statement
Current role files contain:
1. **No machine-readable metadata** — a subagent receiving a role file cannot programmatically determine what inputs it needs, what outputs it must produce, or which MCP tools to call
2. **Implicit cross-role references** — phrases like "return to **Developer**" or "Quality Assurance Review Comments exist" assume the reader knows the workflow context
3. **Missing/inconsistent artifact paths** — entry conditions in architect, developer, refactor-expert, documenter, builder, and retrospective list requirements like "User Story exists" without explicit `WorkItems/{id}/` paths
4. **Wrong TechBestPractices path** — 4 files reference `.github/roles/TechBestPractices.md` but the source-of-truth is `roles/defaults/TechBestPractices.md`
5. **Casing inconsistency** — QA references `Design-Doc.md` (capital D) while PM creates `design-doc.md` (lowercase)

## Business Case
- **Why now:** This is the foundation for GCP-0049 (Role Context Bundler) and GCP-0050 (Subagent Orchestration). Without self-contained roles, subagents cannot operate independently.
- **Impact:** Enables the full subagent architecture — roles executed in isolation with minimal context transfer.
- **KPIs:** Zero implicit references remaining; 100% role files with valid front-matter.

## Stakeholders
- Golazo Copilot developers (direct)
- LLM orchestration layer consumers of role files (GCP-0049, GCP-0050)

## Functional Requirements
1. Add YAML front-matter block to each of the 10 role files
2. Replace all implicit cross-role references with explicit artifact paths
3. Standardize entry condition artifact paths to use `WorkItems/{id}/` patterns
4. Fix TechBestPractices.md path references
5. Fix casing inconsistencies (Design-Doc → design-doc)

## Non-Functional Requirements
- Role files remain human-readable
- `output_validator.py` backward compatibility (no parser changes)
- Existing tests pass without modification

## Proposed Approach

### YAML Front-Matter Format
Each role file will have a front-matter block between `---` delimiters at the top (before the existing `<!-- Last Updated -->` comment):

```yaml
---
inputs:
  - WorkItems/{id}/{id}-User-Story.md
  - WorkItems/{id}/Design/{id}-design-doc.md
outputs:
  - WorkItems/{id}/Design/{id}-Review-Comments.md
  - WorkItems/{id}/Design/{id}-Test-Cases.md
  - WorkItems/{id}/RoleDecisionNotes/{id}-quality-assurance.md
tools:
  - gcp_status
  - gcp_transition
  - gcp_capabilities
---
```

### Front-Matter Per Role

| Role | inputs | outputs | tools |
|------|--------|---------|-------|
| project-owner-assistant | (none — first role) | `{id}-User-Story.md`, `{id}-project-owner-assistant.md` | `gcp_status`, `gcp_transition`, `gcp_capabilities`, `gcp_create_workitem` |
| program-manager | `{id}-User-Story.md` | `{id}-design-doc.md`, `{id}-program-manager.md` | `gcp_status`, `gcp_transition` |
| domain-expert | `{id}-User-Story.md`, `{id}-design-doc.md` | `{id}-domain-expert.md` | `gcp_status`, `gcp_transition` |
| quality-assurance | `{id}-User-Story.md`, `{id}-design-doc.md` | `{id}-Review-Comments.md`, `{id}-Test-Cases.md`, `{id}-quality-assurance.md` | `gcp_status`, `gcp_transition` |
| architect | `{id}-User-Story.md`, `{id}-design-doc.md`, `{id}-Review-Comments.md` | `{id}-Review-Comments.md`, `{id}-Capability-Impact.md`, `{id}-architect.md` | `gcp_status`, `gcp_transition`, `gcp_capabilities` |
| developer | `{id}-User-Story.md`, `{id}-design-doc.md`, `{id}-Review-Comments.md`, `{id}-Test-Cases.md` | `{id}-developer.md` | `gcp_status`, `gcp_transition`, `gcp_capabilities` |
| refactor-expert | `{id}-developer.md` (to see what changed) | `{id}-refactor-expert.md` | `gcp_status`, `gcp_transition`, `gcp_capabilities` |
| documenter | `{id}-User-Story.md`, `{id}-design-doc.md` | `{id}-documenter.md` | `gcp_status`, `gcp_transition` |
| builder | `{id}-User-Story.md` | `{id}-builder.md` | `gcp_status`, `gcp_transition`, `gcp_capabilities` |
| retrospective | all prior `RoleDecisionNotes/{id}-*.md` | `{id}-retrospective.md` | `gcp_status`, `gcp_transition` |

### Implicit Reference Replacement Strategy

| Current implicit text | Replacement |
|----------------------|-------------|
| "return to **Developer**" | "STOP and call `gcp_transition(role='developer')` with rationale" |
| "Quality Assurance Review Comments exist" | "`WorkItems/{id}/Design/{id}-Review-Comments.md` exists" |
| "previous role", "from the last", "earlier phase" | Explicit file path references |
| "based on Test Cases document" | "based on `WorkItems/{id}/Design/{id}-Test-Cases.md`" |
| "DoR complete (see `.github/copilot-instructions.md`)" | Inline the specific file-existence checks |
| ".github/roles/TechBestPractices.md" | "the TechBestPractices reference document (deployed at `.github/roles/TechBestPractices.md`)" |

### Entry Condition Standardization
All entry conditions will list explicit `WorkItems/{id}/` artifact paths instead of prose descriptions like "User Story exists".

## Alternatives Considered

1. **JSON front-matter**: Rejected — YAML is more readable and standard for markdown front-matter (used by Jekyll, Hugo, MDX, etc.)
2. **Separate metadata sidecar files**: Rejected — adds file management overhead; keeping metadata in the same file ensures it stays in sync
3. **Inline HTML data attributes**: Rejected — not standard, hard to parse, poor readability
4. **Only fix references, skip front-matter**: Rejected — front-matter is the key enabler for GCP-0049's context bundler

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Front-matter breaks `output_validator.py` parsing | Parser uses regex to find `## Required Outputs` section — front-matter at top won't match. Validated by reading the parser code. |
| Role file loader doesn't handle front-matter | `loader.py` reads raw file content and returns it as-is — front-matter is just part of the markdown string. The LLM consumer handles interpretation. |
| Existing tests fail | Run full test suite before committing. No test mods expected since tests mock/load role content and parse it. |
| Casing fix breaks existing work items | Historical `Review-Comments.md` files already use this casing. Only fixing the QA file's reference from `Design-Doc.md` to `design-doc.md`. |

## Dependencies
- GCP-0047 (role improvements) — already shipped (v2.102.0+)
- No runtime code changes required
- No new Python dependencies

## Migration / Rollout / Rollback

- **Rollout:** Bump version in `pyproject.toml`, rebuild package. `gcp_bootstrap` deploys updated role files to `.github/roles/`.
- **Rollback:** Revert role file changes, rebuild with previous version. Front-matter is additive — removing it doesn't break anything.
- **Existing workspaces:** Run `gcp_bootstrap` to pull updated roles.

## Observability Plan
- No runtime telemetry — role files are static markdown consumed by LLM
- Validation is via the new `test_role_self_contained.py` test

## Test Strategy Summary
1. **New test file `test_role_self_contained.py`** validates:
   - Every role file has valid YAML front-matter (AC1)
   - No implicit cross-role references via regex patterns (AC2)
   - All artifact references use `WorkItems/{id}/` paths (AC3)
   - Front-matter `outputs:` matches `## Required Outputs` section (AC6)
2. **Existing `test_output_validator.py`** validates AC4 — backward compat (run without modification)
3. **Full pytest suite** must pass with zero modifications to existing tests
