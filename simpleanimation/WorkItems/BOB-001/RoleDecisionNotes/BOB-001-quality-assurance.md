# BOB-001 — Quality Assurance Decision Notes

## Decisions
1. All test cases are manual/visual since this is a graphical animation app.
2. No automated unit tests — the output is visual and best verified by observation.
3. Seven test cases cover all six acceptance criteria plus clean exit.

## Justification
Automated testing of pygame visual output would require screenshot comparison frameworks, which is overkill for a single-file fun animation. Manual visual verification is appropriate.
