# SHUB-032: Content Quality Checker

**Status**: BACKLOG

**Epic**: SHUB-LLM (Supportability Hub AI Assistant)

## User Story

- **Title**: AI-powered content quality validation for Apollo articles
- **As a**: Apollo author or editor
- **I want**: The AI to review my article against all authoring guidelines before submission
- **So that**: I can fix issues proactively and reduce editorial round-trips

## Scope

- **In scope**:
  - Validate against all rules in Rules.md and AuthoringGuidelines.md
  - Check: title format, verb tense, contractions, accessibility, branding
  - Identify unclear or ambiguous instructions
  - Suggest improvements with specific line references
  - Severity classification: blocking vs. suggested
  - Integration with Supportability Hub authoring flow
  
- **Out of scope**:
  - Technical accuracy validation (requires SME)
  - Auto-fixing issues (suggest only)
  - Style preferences beyond documented guidelines

## Acceptance Criteria (bulleted, testable)

- [ ] User can paste article content and get quality report
- [ ] Report identifies all rule violations with line numbers
- [ ] Report categorizes issues: Must Fix, Should Fix, Consider
- [ ] Each issue includes suggested fix
- [ ] Accessibility issues always flagged as Must Fix
- [ ] Clean articles receive "Ready for review" confirmation

## Example Output

```
## Quality Check Results: "Resolve VM RDP connectivity issues"

? Title: Correct format (starts with verb, sentence case)
? Accessibility: Alt text present for all images
?? Line 23: Passive voice detected - "The NSG should be checked" 
   ? Suggest: "Check the NSG rules"
?? Line 45: Missing contraction - "do not" 
   ? Suggest: "don't"
? Line 67: Product name incorrect - "Azure AD" 
   ? Suggest: "Microsoft Entra ID"

**Summary**: 1 blocking issue, 2 suggestions
```

## Non-functional Requirements

- Validation time: < 10s for typical article
- Rule coverage: 100% of documented rules
- False positive rate: < 5%

## Telemetry / Metrics Expected

- Issues found per article (by category)
- Time from first draft to editorial approval (with vs. without)
- Most common issues (for training prioritization)
