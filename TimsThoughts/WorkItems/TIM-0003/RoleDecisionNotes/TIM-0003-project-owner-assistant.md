# TIM-0003 — Role Decision Notes: Project Owner Assistant

## Work Item
TIM-0003: Build a 30-minute slide deck covering Tim's five delivery documents

## Scope Decisions

**Chosen layout**: 34 slides structured as:
- 1 title slide
- 3 corpus-level synthesis slides (abstract, document map, problem/solution overview)
- 5 section dividers (one per document)
- 20 per-document content slides (4 per document: wants, why, gaps, solution)
- 5 synthesizing slides (themes, architecture, by-role, tensions, call to action)

**Rationale for 34 vs 30 slides**: A 30-minute deck at ~1 min per content slide needs approximately 25-30 content slides. Section dividers act as visual resets and run ~15 seconds each, so 34 total fits comfortably in 30 minutes.

## Document Coverage

All five source documents read directly from `.docx` via ZIP/XML extraction:
| Document | Source File |
|---|---|
| Delivery is Existential | `Delivery is existential - 2.docx` |
| The Delivery Manifesto | `The Delivery Manifesto.docx` |
| Delivery as an Infinite Game | `Delivery is an infinite game.docx` |
| Harambee and Mission Teams | `Harambee and Mission teams - working together for performance.docx` |
| Role of the Senior IC Leader | `The Role of the Senior IC Leader.docx` |

Also drew on `TimsDocs-Summary-APA.md` and `Thinking.MD` for cross-document synthesis.

## Technical Decisions

- **COM automation** via `PowerPoint.Application` COM object (PowerShell)
- **Format**: `.pptx` (ppSaveAsOpenXMLPresentation = 24)
- **Layouts used**: ppLayoutTitle (1) for dividers/title; ppLayoutContent (2) for all content slides
- **Output**: `WorkItems/TIM-0003/Tims-Delivery-Vision.pptx`
- **Build script**: `WorkItems/TIM-0003/Build-SlideDeck.ps1` (reproducible)

## Suggested Additional Slides (Noted for User)

Five additional slides were included beyond the mandated structure:
1. **Document Map** (Slide 3) — shows how the 5 docs form a progression (urgency → contract → mindset → team → leadership)
2. **Recurring Themes** (Slide 30) — five signals consistent across all documents
3. **Accountability Architecture** (Slide 31) — how the model layers from individual to culture
4. **What This Means by Role** (Slide 32) — PM, Architect, Tech Lead, EM call-outs
5. **Tensions and Open Questions** (Slide 33) — five friction points in implementation

## Outcome

- File: `WorkItems/TIM-0003/Tims-Delivery-Vision.pptx`
- Verified: 34 slide XML parts in PPTX archive
- Size: 89,098 bytes
