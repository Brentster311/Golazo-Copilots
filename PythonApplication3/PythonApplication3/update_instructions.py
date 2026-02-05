"""Script to update copilot-instructions.md with Must-Ask Gate"""
import os

file_path = r'C:\Users\brentj\source\repos\Brentster311\Golazo-Copilots\.github\copilot-instructions.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the DoR section
old_section = """## Non-negotiable process gates

### Definition of Ready (DoR) - before writing production code

You MUST NOT write or modify production code until **ALL** of the following exist for the work item:

1) A User Story document
2) A Design Document including a business case
3) Review Comments from **Reviewer** and **Architect**
4) A Test Cases document (TDD-first)

Failure to enforce this is a **process violation**."""

new_section = """## Non-negotiable process gates

### Must-Ask Gate (BEFORE any artifacts)

When the **Project Owner Assistant** role begins, you MUST ask the user the following questions and **WAIT for answers** before creating any artifacts:

**Must-Ask Checklist** (display this exactly):

> Before I create the User Story, I need to confirm:
>
> 1. **Interface type**: CLI (terminal), GUI (graphical window), Web app, API, or Library?
> 2. **Target platform**: Windows, Mac, Linux, or cross-platform?
> 3. **Data persistence**: Files, database, cloud storage, or in-memory only?
> 4. **User type**: Technical (developers) or non-technical (general users)?
>
> Please answer these 4 questions so I can proceed.

**STOP and wait for user response.** Do not proceed until all 4 are answered.

Record answers in the User Story under a new section: **Must-Ask Responses**

---

### Definition of Ready (DoR) - before writing production code

You MUST NOT write or modify production code until **ALL** of the following exist for the work item:

1) **Must-Ask responses recorded** (interface, platform, persistence, user type)
2) A User Story document
3) A Design Document including a business case
4) Review Comments from **Reviewer** and **Architect**
5) A Test Cases document (TDD-first)

Failure to enforce this is a **process violation**."""

if old_section in content:
    content = content.replace(old_section, new_section)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: Updated copilot-instructions.md with Must-Ask Gate!')
else:
    print('ERROR: Could not find the exact text to replace')
    print('Searching for partial match...')
    if '### Definition of Ready (DoR)' in content:
        print('Found DoR section - may need manual update')
