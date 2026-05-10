# TIM-0005 — Test Cases

## AC1: 12 `.agent.md` files exist in `.github/agents/`

**TC-01**: Verify `.github/agents/` directory exists.
- **Pass**: Directory exists.
- **Fail**: Directory missing.

**TC-02**: Count `.agent.md` files in `.github/agents/`. Verify exactly 12.
- **Pass**: `(Get-ChildItem ".github/agents/*.agent.md").Count -eq 12`
- **Fail**: Count is not 12.

**TC-03**: Verify each of the 12 expected filenames is present:
`al-shalloway`, `christopher-alexander`, `daniel-pink`, `donald-reinertsen`, `eric-ries`, `joseph-grenny`, `kent-beck`, `dean-leffingwell`, `mary-poppendieck`, `simon-sinek`, `starfish-spider`, `stephen-covey`
- **Pass**: All 12 filenames match.
- **Fail**: Any file missing or misnamed.

## AC2: Valid YAML frontmatter with description, name, and tools

**TC-04**: For each of the 12 files, verify the file opens with `---` (YAML frontmatter block).
- **Pass**: All 12 files begin with `---`.
- **Fail**: Any file missing the opening `---`.

**TC-05**: For each file, verify `name:` field is present and is a human-readable author name.
- **Pass**: All 12 files contain `name:` with a recognizable author name.
- **Fail**: Any file uses a slug or filename as the display name.

**TC-06**: For each file, verify `description:` is present, quoted, and contains the author's name plus at least one trigger phrase ("review from", "what would", or "perspective").
- **Pass**: All 12 files have a quoted description with name + trigger phrase.
- **Fail**: Any description is unquoted (colon risk), missing author name, or missing trigger phrase.

**TC-07**: For each file, verify `tools: [read, search]` is present.
- **Pass**: All 12 files specify `tools: [read, search]`.
- **Fail**: Any file has different or missing tools.

## AC3: Body accurately represents the author's lens

**TC-08**: For each agent, verify the body is written in first-person author voice (contains "I would", "My concern", "I ask", or similar).
- **Pass**: All 12 bodies use first-person voice.
- **Fail**: Any body uses third-person ("He would ask…").

**TC-09**: For each agent, verify the body contains at least 3 distinct questions or concerns attributable to that author's known frameworks.
- **Pass**: All 12 bodies contain ≥ 3 distinct questions/concerns.
- **Fail**: Any body is a generic review template without author-specific content.

**TC-10**: For each agent, verify no position is invented — all concerns trace back to the corresponding `Agile/*.md` source file.
- **Pass**: Manual review confirms no fabricated stances.
- **Fail**: Any agent contains positions not documented in the source.

## AC4: Read-only + user-invocable

**TC-11**: Verify `user-invocable: true` is present (or absent, defaulting to true) in each file.
- **Pass**: All 12 have explicit `user-invocable: true` or no `user-invocable: false`.
- **Fail**: Any file has `user-invocable: false`.

## AC5: Committed to git

**TC-12**: Run `git log --oneline -- .github/agents/` — verify at least one commit references the 12 agent files.
- **Pass**: Commit entry visible.
- **Fail**: Files untracked or unstaged.
