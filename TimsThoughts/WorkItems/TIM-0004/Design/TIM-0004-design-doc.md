# TIM-0004 Design Doc — OFP Delivery: Corpus Introduction

## Summary

Produce `OFP_Delivery.md` at the workspace root — a structured Markdown document that introduces Tim Mallalieu's six delivery-transformation writings to readers who have not seen the originals. Each document gets a named section with WHY / HOW / WHAT sub-headers in concise prose. This file acts as the standing introduction to the broader OFP response document (TIM-0005+).

## Problem Statement

The planned response document (`OFP_Delivery.md`) must ground its readers before any rebuttal or agreement can land. Without a neutral, accurate summary of Tim's corpus, readers who missed one or more of the original documents cannot follow the subsequent analysis. The introduction section fills that gap.

## Business Case

| | |
|---|---|
| **Why now** | The April 16 working session is days away. Respondents need a shared corpus reference before that conversation. |
| **Impact** | Sets the frame for all subsequent OFP response sections (TIM-0005+) and serves as a standalone reference artifact. |
| **KPI** | File exists, is readable, passes peer review for accuracy and neutrality. |

## Stakeholders

- **Author / Respondent**: The person preparing the OFP response (primary consumer)
- **Working session participants**: Secondary audience who may use this as a pre-read

## Functional Requirements

1. `OFP_Delivery.md` exists at workspace root with a framing preamble.
2. Six named sections — one per document — appear in the order listed in the User Story.
3. Each section has WHY, HOW, and WHAT sub-headers containing 2–4 sentences of prose (no bullet dumps).
4. Language is executive-accessible: concrete nouns, active voice, no unexplained jargon.
5. File is committed to git.

## Non-Functional Requirements

- Each document section reads in under 90 seconds (~200–300 words per section).
- Tone is neutral and descriptive — no editorial stance.
- Markdown renders cleanly in VS Code preview and on GitHub.

## Proposed Approach

Single-pass authoring of the full introduction in one Markdown file. Content derived directly from reading the six source `.docx` files already extracted to `q:\tmp_*.txt`. No external sources or assumptions beyond the documents themselves.

**Section order:**
1. Delivery Is Existential - 2
2. The Delivery Manifesto
3. Harambee and Mission Teams
4. HBR's AWARE Framework and Mission Teams
5. Delivery as an Infinite Game
6. The Role of the Senior IC Leader

## Alternatives Considered

| Alternative | Reason rejected |
|---|---|
| Separate summary files per document | Adds navigation overhead; single file serves the working session use case better |
| Bullet-point summaries | User Story explicitly requires prose under WHY/HOW/WHAT sub-headers |

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Misrepresenting Tim's intent | Summaries derived word-for-word from source; no interpolation |
| Over-length sections | Hard cap at ~300 words per section; enforced during authoring |

## Dependencies

- Six `.docx` files already extracted to `q:\tmp_*.txt` — dependency resolved.

## Migration / Rollout / Rollback

- No deployment. File is a static Markdown artifact.
- Rollback: `git revert` on the commit.
- Expansion: subsequent work items (TIM-0005+) append response sections to this file.

## Observability Plan

N/A — document artifact.

## Test Strategy Summary

Manual review against each acceptance criterion:
1. File existence check.
2. Section count (6 sections).
3. Sub-header presence (WHY/HOW/WHAT in each).
4. Prose format (no bullet dumps).
5. Git log confirms commit.
