# GCP-0021: Test Cases

## TC-01: Principles Section Exists
**Given**: The updated refactor-expert.md file
**When**: I read the file contents
**Then**: A section titled "Design Principles Checklist" exists

## TC-02: All 10 Principles Listed
**Given**: The Design Principles Checklist section
**When**: I count the principles
**Then**: Exactly 10 principles are listed:
1. DRY
2. Encapsulate What Changes
3. Open/Closed
4. Single Responsibility
5. Dependency Inversion
6. Composition over Inheritance
7. Liskov Substitution
8. Interface Segregation
9. Program to Interface
10. Delegation

## TC-03: Each Principle Has Guidance
**Given**: Each principle in the checklist
**When**: I review the "Look For" column
**Then**: Each principle has actionable guidance text

## TC-04: Required Rationale Format Documented
**Given**: The role file
**When**: I search for rationale requirements
**Then**: The 3 valid categories are listed:
- "Reviewed - no issues found"
- "N/A - [reason]"
- "Violation found - [action taken or work item created]"

## TC-05: Unacceptable Rationales Listed
**Given**: The role file
**When**: I search for unacceptable rationales
**Then**: The following are explicitly listed as invalid:
- Skipped without evaluation
- Vague ("looks fine")
- Deferred without tracking
- Ignored violation
- Efficiency excuse ("slows me down")
- Self-imposed time pressure

## TC-06: Existing Responsibilities Preserved
**Given**: The original refactor-expert.md responsibilities
**When**: I compare with updated file
**Then**: All original responsibilities are still present:
- Identify code smells, duplication, complexity
- Apply refactoring patterns
- Improve naming clarity
- Reduce coupling
- Ensure no behavior changes

## TC-07: Example Template Included
**Given**: The role file
**When**: I search for example format
**Then**: A sample refactor notes structure is provided showing principle-by-principle documentation
