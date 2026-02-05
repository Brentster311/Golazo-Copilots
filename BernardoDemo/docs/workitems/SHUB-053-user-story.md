# SHUB-053: Cross-Team Insights

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: Surface learnings from similar products/teams
- **As a**: Supportability PM
- **I want**: To learn from how other teams solved similar problems
- **So that**: I don't reinvent the wheel and can adopt proven practices

## Scope

- **In scope**:
  - Identify similar products/services based on case patterns
  - Surface successful interventions from similar teams
  - Share anonymized/aggregated insights (not raw case data)
  - "Teams like you also tried..." recommendations
  - Opt-in sharing model (teams choose to contribute)
  
- **Out of scope**:
  - Sharing identifiable case data across teams
  - Comparing team performance
  - Forcing best practice adoption

## Acceptance Criteria (bulleted, testable)

- [ ] User can ask: "What have similar teams done about deployment failures?"
- [ ] AI identifies similar teams based on: technology stack, case patterns, size
- [ ] Results show: intervention, outcome, team (if opted-in to share)
- [ ] Privacy-safe: No customer data crosses team boundaries
- [ ] Teams can opt out of cross-team insights entirely

## Example Interaction

```
User: What have other compute-related teams done to reduce 
      their connectivity case volume?

AI: I found 3 relevant interventions from similar teams:

    1. **Azure VMware Solution** (similar: IaaS compute)
       - Created interactive connectivity diagnostic
       - Result: 23% case reduction in 2 months
       - Contact: @vmware-support-pm (opted-in to connect)
    
    2. **Azure Stack HCI** (similar: hybrid compute)
       - Added "Check connectivity" to portal deploy flow
       - Result: 18% reduction in post-deploy cases
       
    3. **Azure Batch** (similar: compute orchestration)
       - GT for "job won't start" (top issue overlap with your VMs)
       - Result: 4.1 CSAT on the GT
       
    Would you like me to connect you with any of these teams?
```

## Non-functional Requirements

- Cross-team search latency: < 10s
- Privacy: Zero customer data leakage
- Similarity matching accuracy: Teams find suggestions relevant 80%+

## Telemetry / Metrics Expected

- Cross-team queries per month
- Connections facilitated
- Interventions adopted from cross-team insights
- Teams opted-in to sharing

## Privacy & Governance

- Opt-in only (teams explicitly share)
- No raw case data crosses boundaries
- Aggregated patterns only (e.g., "23% reduction")
- Contact sharing requires explicit PM opt-in
