# TIM-0003 — Retrospective

## What Went Well

- **Document extraction via ZIP/XML** worked reliably for all 5 `.docx` files — no COM dependency needed for reading
- **COM automation for PowerPoint** succeeded on first run — 34 slides generated cleanly
- **Content quality**: Full text of all 5 documents was read before authoring any slide content; no hallucinated claims
- **Workflow artifacts were lightweight** for this doc-gen work item — roles completed efficiently without bureaucratic overhead
- **Refactor found a real bug**: reading `$deck.Slides.Count` after `$deck.Close()` was caught and fixed

## What Didn't Go Well

- **Early terminal output routing**: The docx ZIP extraction ran but wrote to a COM session's temp file, not a workspace file — required a second approach
- **File write to q:\tmp_**: PowerShell wrote successfully but read_file couldn't open non-workspace paths — this pattern will fail again; should always write to workspace path from the start
- **"Done. 0 slides saved." message**: Script ran successfully but printed misleading output because slide count was read after deck was closed

## Action Items

| # | Action | Impact |
|---|---|---|
| 1 | Always write intermediate extraction files to `WorkItems/<id>/` not `q:\tmp_*` | File access via tools will work first try |
| 2 | When using COM to close/quit before reading a property, capture the property value first | Avoids misleading output |

## Metrics

- Script ran without error on first attempt: ✅
- Slides verified via ZIP inspection: 34/34 ✅
- All 5 source documents read before authoring: ✅
- Refactor bug caught: 1 (slide count read after close)

## Lessons Learned

For PowerPoint COM scripts: always capture values from the live COM object (`$deck.Slides.Count`, `$deck.Name`, etc.) **before** calling `.Close()` or `.Quit()` — the COM object is no longer accessible after close.
