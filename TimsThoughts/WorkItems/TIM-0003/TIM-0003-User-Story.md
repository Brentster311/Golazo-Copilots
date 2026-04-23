# TIM-0003 User Story

**Status**: IMPLEMENTED

## User Story

- **Title**: Build 30-Minute Slide Deck Covering Tim's Five Delivery Documents
- **As a**: Reviewer preparing to engage with Tim Mallalieu's delivery corpus
- **I want**: A structured PowerPoint presentation covering all five documents with corpus-level summary, per-document problem/solution, and detailed per-document slides on expectations, rationale, gaps, and proposed solutions — plus synthesizing slides
- **So that**: I can present, study, or share Tim's delivery model as a coherent 30-minute narrative

## Scope

**In scope:**
- 1 title slide
- 1 corpus abstract slide (serves as executive summary of all 5 docs)
- 1 document map slide (how the 5 docs connect)
- 1 overview slide (problem/solution for each doc at a glance)
- 5 section divider slides (one per document)
- 4 content slides per document: What Tim Wants, Why He Wants It, Observed Gaps, Proposed Solution (20 slides)
- 5 synthesizing slides: Recurring Themes, Accountability Architecture, What This Means by Role, Tensions/Open Questions, Call to Action
- Total: 33 slides, designed for ~30 minutes

**Documents covered:**
1. Delivery is Existential (Delivery is existential - 2.docx)
2. The Delivery Manifesto (The Delivery Manifesto.docx)
3. Delivery as an Infinite Game (Delivery is an infinite game.docx)
4. Harambee and Mission Teams (Harambee and Mission teams - working together for performance.docx)
5. The Role of the Senior IC Leader (The Role of the Senior IC Leader.docx)

**Out of scope:**
- Design/branding with custom theme files
- Speaker notes (content is in slide body)
- Animations or transitions
- Brent's response or critique of Tim's model

## Assumptions

- **Assumption (explicit)**: Microsoft PowerPoint COM automation is available on this machine (confirmed: .pptm files exist in workspace)
- **Assumption (explicit)**: Output saved to `WorkItems/TIM-0003/Tims-Delivery-Vision.pptx`
- **Assumption (explicit)**: Default Office theme; no custom corporate template required

## Acceptance Criteria

- [ ] `Tims-Delivery-Vision.pptx` exists in `WorkItems/TIM-0003/`
- [ ] File contains 33 slides covering all 5 documents
- [ ] Each document has exactly: 1 section divider + 4 content slides (wants, why, gaps, solution)
- [ ] Corpus abstract slide summarizes the entire 5-document model
- [ ] File opens in PowerPoint without errors

## Non-Functional Requirements

- Slide text must be concise enough to read in ~1 minute per slide
- Bullet points, not paragraphs, for content slides
