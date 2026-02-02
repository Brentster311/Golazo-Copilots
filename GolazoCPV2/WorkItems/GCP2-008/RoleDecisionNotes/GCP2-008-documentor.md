# GCP2-008: Documentor Decision Notes

**Work Item**: GCP2-008 - Configuration System  
**Role**: Documentor  
**Date**: 2026-02-01

---

## API Summary

```python
from golazo.config import GolazoConfig

# Load config (from golazo.yaml or defaults)
config = GolazoConfig.load(base_path=Path("."))

# Access configuration
config.roles          # ('project-owner', 'program-manager', ...)
config.transitions    # {'project-owner': ('program-manager',), ...}
config.dor_items      # ('userStory', 'designDoc', ...)
config.dod_items      # ('branchCreated', 'testsWrittenFirst', ...)
config.quality_gates  # ('tester', 'architect')
config.role_to_phase  # {'project-owner': 'design', ...}

# Machine uses config automatically
machine = GolazoStateMachine("WORK-001", base_path=path)
# machine._config is loaded from golazo.yaml
```

## Config File Schema

```yaml
# golazo.yaml
version: "1.0"

roles:
  - project-owner
  - program-manager
  - tester
  - architect
  - developer
  - refactor-expert
  - builder
  - documentor

transitions:
  project-owner: [program-manager]
  program-manager: [tester]
  # ...

dor:
  items: [userStory, designDoc, reviewComments, testCases]

dod:
  items: [branchCreated, testsWrittenFirst, testsPass, ...]

quality_gates:
  - tester
  - architect
```
