# TIM-0004 — Test Cases

## AC1: OFP_Delivery.md exists with title and framing paragraph

**TC-01**: Verify `OFP_Delivery.md` exists at workspace root (`q:\src\Golazo-Copilots\TimsThoughts\OFP_Delivery.md`).
- **Pass**: File exists.
- **Fail**: File missing or at incorrect path.

**TC-02**: Verify the file begins with a top-level heading (H1) and contains a framing paragraph before any document-specific section.
- **Pass**: First H1 heading present; at least one prose paragraph follows before the first document section.
- **Fail**: File opens directly into a document section with no preamble.

## AC2: Each of the six Tim documents has its own named section

**TC-03**: Verify six named sections exist, one per document, in this order:
1. Delivery Is Existential - 2
2. Harambee and Mission Teams
3. The Delivery Manifesto
4. HBR's AWARE Framework and Mission Teams
5. Delivery as an Infinite Game
6. The Role of the Senior IC Leader

- **Pass**: All six sections present in the correct order.
- **Fail**: Any section missing, out of order, or named inaccurately.

## AC3: Each section contains WHY, HOW, WHAT sub-headers with concise prose

**TC-04**: For each of the six sections, verify sub-headers WHY, HOW, and WHAT are present (18 sub-headers total).
- **Pass**: All 18 sub-headers present.
- **Fail**: Any sub-header missing in any section.

**TC-05**: Verify that the content under each sub-header is prose, not a bullet list.
- **Pass**: No list items (`-`, `*`, `1.`) appear under WHY/HOW/WHAT sub-headers.
- **Fail**: Any sub-header uses bullet points or numbered lists as its primary content.

**TC-06**: Verify each section is approximately 200–300 words (auditable, not automated).
- **Pass**: No section exceeds ~300 words.
- **Fail**: Any section is clearly a wall-of-text bulk dump or too short to convey core ideas.

## AC4: Executive-accessible language

**TC-07**: Verify domain-specific terms (e.g., "Harambee," "steel threads," "AWARE") are briefly explained on first use within each section.
- **Pass**: Each specialized term carries a contextual gloss on first use in its section.
- **Fail**: Terms used without explanation that would confuse a reader unfamiliar with the corpus.

## AC5: File committed to git

**TC-08**: Run `git log --oneline -- OFP_Delivery.md` from workspace root; verify at least one commit exists.
- **Pass**: Commit entry visible.
- **Fail**: File is untracked or unstaged.
