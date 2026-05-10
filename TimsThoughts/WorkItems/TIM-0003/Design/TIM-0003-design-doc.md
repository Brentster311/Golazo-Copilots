# TIM-0003 Design Document

## Summary

Build a 34-slide PowerPoint presentation covering Tim Mallalieu's five delivery documents as a coherent 30-minute narrative deck. The slide deck is generated via a reproducible PowerShell script using COM automation.

## Problem Statement

Tim has produced five related documents that form a coherent delivery operating model. No consolidated visual summary exists that a reader can use to rapidly internalize the full model, present it to others, or use as a study reference.

## Business Case

- **Why now**: Tim is actively presenting this model to leadership. A structured deck enables faster comprehension, discussion, and response.
- **Impact**: Reduces the time to understand the full corpus from ~2 hours (reading all 5 docs) to ~30 minutes.
- **KPI**: Deck opens and renders correctly in PowerPoint; covers all 5 documents with 4 content slides each.

## Stakeholders

- Brent Jensen (primary consumer and presenter)
- Any reviewer engaging with Tim's delivery model

## Functional Requirements

| # | Requirement |
|---|---|
| F1 | One `.pptx` file covering all 5 documents |
| F2 | Corpus abstract slide serving as executive summary |
| F3 | Problem/solution overview slide for all 5 docs |
| F4 | Section divider + 4 content slides per document (wants, why, gaps, solution) |
| F5 | 5 synthesizing slides: themes, architecture, by-role, tensions, call to action |
| F6 | Total deck: ~34 slides, ~30 minutes |

## Non-Functional Requirements

- File must open in Microsoft PowerPoint without errors
- Content must be bullet-point format (not prose paragraphs)
- Script must be re-runnable (idempotent: overwrites prior output)

## Proposed Approach

Generate via `Build-SlideDeck.ps1` using PowerShell COM automation against `PowerPoint.Application`. Two layout types used: ppLayoutTitle (1) for section dividers and title; ppLayoutContent (2) for all content slides.

## Alternatives Considered

| Alternative | Reason Not Chosen |
|---|---|
| Manual authoring in PowerPoint | Not reproducible; slower to maintain |
| Open XML from scratch | No COM needed but significantly more complex XML to author |
| Markdown → reveal.js | Not a native .pptx output |

## Risks

| Risk | Mitigation |
|---|---|
| PowerPoint COM not available | Confirmed: `.pptm` files exist in workspace, COM succeeded |
| Text overflow on slides | Bullets kept concise; user can reformat in PowerPoint |

## Dependencies

- Source documents in `TimsDocs/` (all 5 `.docx` files)
- `Microsoft.Office.Interop.PowerPoint` (via COM, requires PowerPoint installation)

## Rollback

Delete `Tims-Delivery-Vision.pptx` and re-run `Build-SlideDeck.ps1`.

## Test Strategy

- Verify file exists at output path
- Verify ZIP contains 34 `ppt/slides/slide*.xml` entries
- Open file in PowerPoint and verify slides render

## Status

Implemented. File verified at `WorkItems/TIM-0003/Tims-Delivery-Vision.pptx`, 34 slides, 89,098 bytes.
