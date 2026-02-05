# SHUB-012: Context Awareness

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: Maintain user context across AI assistant conversations
- **As a**: Support engineer using the AI assistant
- **I want**: The assistant to remember my selected scope (product, team, service) and role
- **So that**: I don't have to repeat context in every question and get personalized responses

## Scope

- **In scope**:
  - Inject current Supportability Hub scope into LLM context
  - Remember conversation history within session
  - Personalize responses based on user's team/product
  - "You are currently viewing [Product X]" awareness
  - Role-aware responses (author vs. reviewer vs. PM)
  
- **Out of scope**:
  - Cross-session memory (learning user preferences over time)
  - Multi-user context sharing
  - Modifying user's scope from chat

## Assumptions

- **Assumption (explicit)**: Scope selector state is available via existing Supportability Hub APIs
- **Assumption (explicit)**: User role/permissions are available from auth context
- **Assumption (explicit)**: Context window is sufficient for conversation + scope (8K+ tokens)

## Acceptance Criteria (bulleted, testable)

- [ ] If user has "Azure Compute" selected, queries about "my cases" return Compute cases
- [ ] Assistant acknowledges scope in first response: "I see you're working with [Product]"
- [ ] Follow-up questions reference previous conversation without re-stating context
- [ ] User can ask "What scope am I in?" and get accurate answer
- [ ] Context resets when user changes scope in Supportability Hub
- [ ] Role-appropriate responses (authors see authoring tips, reviewers see review guidance)

## Example Conversations

**Scenario 1: Scope-aware case query**
```
User: How many cases were closed last week?
Assistant: For Azure Compute (your current scope), 
           142 cases were closed last week. 
           Would you like a breakdown by support topic?
```

**Scenario 2: Follow-up without re-stating context**
```
User: What are the common themes in recent cases?
Assistant: Based on Azure Compute cases from the last 30 days,
           the top themes are: 1) VM connectivity (34%), 
           2) Performance issues (28%), 3) Deployment failures (19%)

User: What about the connectivity issues specifically?
Assistant: For the VM connectivity cases (48 total), 
           the breakdown is: NSG rules (45%), 
           RDP/SSH port blocks (30%), DNS resolution (25%)
```

## Non-functional Requirements

- Context injection latency: < 100ms
- Context size: Scope + last 10 conversation turns
- Token budget: Reserve 2K tokens for context

## Telemetry / Metrics Expected

- Context utilization rate (% of queries using scope)
- Conversation depth (turns before new topic)
- Scope change frequency during sessions

## Rollout / Rollback Notes

- Depends on SHUB-010 (Core Prompt Interface)
- Graceful degradation: If scope unavailable, ask user to specify
- Rollback: Disable context injection, require explicit scope in queries

## Privacy Considerations

- Scope/role info is not PII
- Conversation context stays in session (not persisted)
- No cross-user context leakage
