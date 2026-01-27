# GCP-012: Design Document

## Summary
Create a new guide file `.github/guides/PatternProposals.md` that instructs Copilot to research existing patterns before proposing new infrastructure, pipeline, or config changes.

## Problem Statement
Copilot sometimes proposes new patterns for infrastructure/config changes without checking if similar implementations already exist in the codebase. This leads to inconsistent patterns across the repo.

## Business Case

### Why Now
- Observed during infrastructure changes that Copilot invented new patterns when existing ones should have been used
- Guide approach (like powershell-terminal.md) proven effective
- Low implementation cost

### Impact
- **Positive**: Consistent patterns across codebase
- **Positive**: Reduced tech debt from pattern proliferation
- **Positive**: User awareness before diverging from conventions

## Proposed Implementation

### New File: `.github/guides/PatternProposals.md`

```markdown
<!-- Golazo Version: 1.1.5 -->
# Pattern Research Guide

## When to Use
Consult this guide when:
- Modifying deployment pipelines or CI/CD configs
- Adding infrastructure settings or resources
- Changing configuration files (YAML, JSON, etc.)
- Proposing new architectural patterns

## Mandatory Pattern Research Process

### Step 1: SEARCH FIRST
Before proposing any new pattern:
- Search the codebase for similar implementations
- Look for files with similar names, extensions, or purposes
- Check common locations (pipelines/, infra/, config/, etc.)

### Step 2: COUNT USAGE
Report findings:
- How many components use each pattern found
- Which pattern is most common
- Any outliers or exceptions

### Step 3: PRESENT OPTIONS
Show user:
- Existing patterns with usage counts
- Pros/cons of each
- Recommendation based on existing conventions

### Step 4: GET EXPLICIT APPROVAL
If proposing something different from existing patterns:
- Clearly state "This differs from existing pattern X"
- Ask user to confirm before proceeding
- Document reason for divergence

## Fail-Fast Rule
If pattern research reveals the proposed approach is non-standard:
1. STOP implementation immediately
2. Report findings to user
3. Ask: "Should I align with existing pattern or continue with new approach?"
4. Do NOT proceed until user confirms direction
```

### Spine Update
Add to "Context-Specific Guides" section:
```markdown
### Infrastructure & Pattern Changes
**When to use**: Modifying pipelines, CI/CD, infrastructure, or proposing new architectural patterns

**Guide**: `.github/guides/PatternProposals.md`
```

## Test Strategy
1. Verify guide file exists
2. Verify guide has correct sections
3. Verify spine references guide
4. VERSION = 1.1.5, CHANGELOG updated
