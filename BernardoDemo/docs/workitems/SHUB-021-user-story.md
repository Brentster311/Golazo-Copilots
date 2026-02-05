# SHUB-021: Similar Case Search

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: Find semantically similar cases using natural language
- **As a**: Support engineer working on a case
- **I want**: To find similar past cases based on symptoms and context, not just keywords
- **So that**: I can learn from previous resolutions and reduce time-to-resolve

## Scope

- **In scope**:
  - Semantic search across case symptoms and descriptions
  - Similarity scoring and ranking
  - Filter by resolution status (resolved only)
  - Filter by time range and scope
  - Show resolution summary for similar cases
  - "Cases like this" button from case view
  
- **Out of scope**:
  - Image/attachment similarity
  - Cross-tenant case search
  - Real-time case embedding (batch is acceptable)

## Assumptions

- **Assumption (explicit)**: Case embeddings will be pre-computed in batch (nightly)
- **Assumption (explicit)**: Only resolved cases are searchable (privacy protection)
- **Assumption (explicit)**: Similarity threshold will be tuned post-launch

## Acceptance Criteria (bulleted, testable)

- [ ] User can describe problem in natural language and get top 5 similar cases
- [ ] User can click "Find similar" from any case to get related cases
- [ ] Results show: Case ID, similarity score, symptom excerpt, resolution excerpt
- [ ] Results are filtered to user's accessible scope by default
- [ ] User can expand search to broader scope if permitted
- [ ] No results message when no similar cases found (with suggestion to broaden scope)

## Example Interaction

```
User: Find cases similar to: "Customer's VM is running but they 
      can't connect via RDP. NSG looks correct."