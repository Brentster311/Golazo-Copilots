# SHUB-051: Training Mode (AI Onboarding Assistant)

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: Interactive AI assistant for onboarding new support team members
- **As a**: New support engineer or author joining a team
- **I want**: An AI tutor that teaches me about my product's support landscape
- **So that**: I can become productive faster without overwhelming my teammates with questions

## Scope

- **In scope**:
  - Interactive Q&A about product support (common issues, resolutions, tools)
  - Guided tours of Supportability Hub features
  - Practice scenarios with simulated cases
  - Progress tracking and knowledge gaps identification
  - Team-specific customization (focus areas, tribal knowledge)
  
- **Out of scope**:
  - Replacing formal training programs
  - Certification/testing
  - Performance evaluation

## Acceptance Criteria (bulleted, testable)

- [ ] New user can start "Training Mode" from assistant
- [ ] AI presents: "Let's learn about [Product]. What would you like to start with?"
- [ ] AI can quiz: "Given this case symptom, what would you check first?"
- [ ] AI tracks: topics covered, questions asked, knowledge gaps
- [ ] Manager can see onboarding progress dashboard
- [ ] Training content is product/team-scoped

## Example Interaction

```
AI: Welcome to Azure Compute support training! I'll help you get up 
    to speed. Based on your role, I recommend starting with:
    
    1. ?? Top 5 case types (30 min)
    2. ??? Essential diagnostics (20 min)  
    3. ?? Key documentation (15 min)
    4. ?? Escalation procedures (10 min)
    
    Which would you like to explore first?

User: Let's start with top case types

AI: Great! The top 5 case types for Azure Compute are:
    
    1. **VM Connectivity (28%)** - RDP/SSH access issues
       - Key diagnostic: VM Console Serial Log
       - Common causes: NSG rules, Windows Firewall, NIC issues
       
    Let me show you a practice scenario...
    
    ?? **Practice Case**: "Customer reports VM is running but RDP 
    times out. NSG allows port 3389. What's your next step?"
    
    A) Check Windows Firewall settings
    B) Restart the VM
    C) Check if RDP service is running
    D) Escalate to Tier 2
```

## Non-functional Requirements

- Training session state persisted across sessions
- Content freshness: Updated weekly with new case patterns
- Mobile-friendly for on-the-go learning

## Telemetry / Metrics Expected

- Time to first case (with vs. without training mode)
- Knowledge assessment scores over time
- Topics most frequently revisited (indicates confusion)
- Manager engagement with progress dashboards
