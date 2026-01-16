# User Story: CALJACK-010

**Status**: BACKLOG

---

## User Story

**Title**: Settings Menu with Language Selection

**As a**: Player

**I want**: To access a settings menu and change the display language

**So that**: I can play the game in my preferred language

---

## Out of Scope

- Sound settings
- Graphics/resolution settings
- Saving settings between sessions (future enhancement)
- Right-to-left language support

---

## Assumptions

- **Assumption (explicit)**: Settings accessible from main menu
- **Assumption (explicit)**: Language options: English, Chinese (Simplified), Russian
- **Assumption (explicit)**: Language change takes effect immediately
- **Assumption (explicit)**: All UI strings are translatable (buttons, labels, messages)

---

## Acceptance Criteria (bulleted, testable)

- [ ] "Settings" button appears on main menu
- [ ] Clicking Settings opens settings screen
- [ ] Settings screen shows Language dropdown/selection
- [ ] Language options: English, Chinese, Russian
- [ ] Selecting language updates all displayed text immediately
- [ ] Back button returns to main menu
- [ ] Selected language persists while app is running

---

## Strings to Translate

| English | Chinese (Simplified) | Russian |
|---------|---------------------|---------|
| New Game | ??? | ????? ???? |
| Settings | ?? | ????????? |
| Help | ?? | ?????? |
| Back | ?? | ????? |
| Player 1 | ??1 | ????? 1 |
| Player 2 | ??2 | ????? 2 |
| Player 1 (You) | ??1 (?) | ????? 1 (??) |
| Trump: | ??: | ??????: |
| Stock: | ??: | ??????: |
| Player X's Turn | ??X??? | ??? ?????? X |
| Game Over! | ????! | ???? ????????! |
| End the game? | ????? | ????????? ????? |
| Yes, Exit | ???? | ??, ????? |
| Cancel | ?? | ?????? |
| Language | ?? | ???? |
| English | English | English |
| Chinese | ?? | ????????? |
| Russian | ??????? | ??????? |

---

## Non-functional Requirements

- Font must support Chinese and Russian characters
- Layout should accommodate varying text lengths

---

## Telemetry / Metrics Expected

- None

---

## Rollout / Rollback Notes

- Independent of other features
- Requires font that supports CJK and Cyrillic characters
