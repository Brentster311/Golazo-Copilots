# GCP-0021: Developer Notes

## Implementation Summary
Updated `golazo-instructions/roles/refactor-expert.md` with:

1. **Design Principles Checklist** - All 10 OOP principles with "Look For" guidance
2. **Required Rationale Format** - 3 valid categories documented
3. **Acceptable Rationales Table** - Clear examples of valid justifications
4. **Unacceptable Rationales Table** - Explicit list including "efficiency excuse" and "time pressure"
5. **Example Template** - Sample refactor notes showing expected format
6. **Updated Success Criteria** - Added "All 10 design principles evaluated and documented"

## Test Case Verification (Manual)

| Test Case | Result |
|-----------|--------|
| TC-01: Principles Section Exists | ✅ "Design Principles Checklist" section added |
| TC-02: All 10 Principles Listed | ✅ All 10 numbered and present |
| TC-03: Each Principle Has Guidance | ✅ "Look For" column populated |
| TC-04: Required Rationale Format Documented | ✅ 3 valid categories listed |
| TC-05: Unacceptable Rationales Listed | ✅ Including "slows me down" |
| TC-06: Existing Responsibilities Preserved | ✅ Original 5 responsibilities intact |
| TC-07: Example Template Included | ✅ Markdown table template provided |

## Key Design Decisions
- Added horizontal rules to visually separate new checklist section
- Numbered principles for easy reference in notes
- Bolded "NEVER valid" heading per QA recommendation
- Added "Evaluate all 10 OOP Design Principles" to Responsibilities list
