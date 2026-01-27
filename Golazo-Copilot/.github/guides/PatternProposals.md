<!-- Golazo Version: 1.1.5 -->
# Pattern Research Guide

## When to Use

Consult this guide when:
- Modifying deployment pipelines or CI/CD configs
- Adding infrastructure settings or resources
- Changing configuration files (YAML, JSON, environment settings)
- Proposing new architectural patterns
- Adding new dependencies or libraries

---

## Mandatory Pattern Research Process

Before proposing ANY new infrastructure, pipeline, or config pattern, follow these steps:

### Step 1: SEARCH FIRST

Before proposing any new pattern:
- Search the codebase for similar implementations
- Look for files with similar names, extensions, or purposes
- Check common locations: `pipelines/`, `infra/`, `config/`, `.github/workflows/`, `deploy/`
- Search for similar configuration keys or parameter names

**Example searches:**
```
# Find similar pipeline files
*.yml, *.yaml in pipeline directories

# Find similar config patterns
appsettings*.json, *.config, environment variables

# Find infrastructure definitions
*.tf, *.bicep, ARM templates
```

### Step 2: COUNT USAGE

Report your findings clearly:
- How many components use each pattern found
- Which pattern is most common (the "standard")
- Any outliers or exceptions and why they exist

**Example report:**
```
Found 3 patterns for database connection strings:
- Pattern A (Key Vault reference): 12 services use this ? STANDARD
- Pattern B (Environment variable): 2 services use this (legacy)
- Pattern C (Inline in config): 1 service uses this (deprecated)
```

### Step 3: PRESENT OPTIONS

Show the user:
- Existing patterns with usage counts
- Pros/cons of each approach
- Your recommendation based on existing conventions

**Always recommend the most common pattern unless there's a strong reason not to.**

### Step 4: GET EXPLICIT APPROVAL

If proposing something different from existing patterns:
1. Clearly state: "This differs from existing pattern X used by Y services"
2. Explain why the different approach might be needed
3. Ask user to explicitly confirm before proceeding
4. Document the reason for divergence in commit message

---

## Fail-Fast Rule

If pattern research reveals the proposed approach is non-standard:

1. **STOP** implementation immediately
2. **REPORT** findings to user with pattern comparison
3. **ASK**: "Should I align with the existing pattern (used by N services) or continue with the new approach?"
4. **WAIT** for explicit user confirmation
5. **DO NOT** proceed until user confirms direction

---

## Common Pattern Categories

### Deployment Pipelines
- Build stages and steps
- Environment promotion flow
- Approval gates
- Variable/secret handling

### Configuration
- Connection strings
- Feature flags
- Environment-specific settings
- Secret references

### Infrastructure
- Resource naming conventions
- Tagging standards
- Network configurations
- Identity/access patterns

---

## Red Flags (Always Stop and Ask)

Stop and ask the user if you notice:
- Creating a new pattern when 5+ services use an existing one
- Environment names that don't match existing conventions
- New secret/config storage approach different from standard
- Different CI/CD tool or approach than rest of repo
- New dependency when similar functionality exists

---

## Example Workflow

**User request:** "Add database connection to ServiceX"

**Correct approach:**
1. Search: Find how other services connect to databases
2. Count: "Found 8 services using Key Vault references, 1 using env vars"
3. Present: "The standard pattern is Key Vault reference. Shall I use that?"
4. Approve: Wait for user confirmation
5. Implement: Follow the standard pattern

**Wrong approach:**
- Immediately propose a new connection string pattern without checking existing services
