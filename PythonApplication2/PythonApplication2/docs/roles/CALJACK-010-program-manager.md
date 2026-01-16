# Role Decision Document: Program Manager

**Work Item**: CALJACK-010 - Settings Menu with Language Selection  
**Role**: Program Manager  
**Date**: 2025-01-XX

---

## First Action Verification

- [x] User Story exists at `docs/workitems/CALJACK-010-user-story.md`

---

## Scope Verification

| Item | In Scope | Notes |
|------|----------|-------|
| Settings button on menu | ? | AC #1 |
| Settings screen | ? | AC #2 |
| Language selection | ? | AC #3, #4 |
| Immediate text update | ? | AC #5 |
| Back navigation | ? | AC #6 |
| Session persistence | ? | AC #7 |
| Save to disk | ? | Explicitly out of scope |
| Sound settings | ? | Out of scope |

---

## Acceptance Criteria Review

| AC | Testable | Clear | Achievable |
|----|----------|-------|------------|
| Settings button appears | ? | ? | ? |
| Clicking opens settings | ? | ? | ? |
| Language selector shown | ? | ? | ? |
| 3 language options | ? | ? | ? |
| Text updates immediately | ? | ? | ? |
| Back returns to menu | ? | ? | ? |
| Language persists in session | ? | ? | ? |

**All 7 AC are testable and achievable.**

---

## Dependencies

| Dependency | Status |
|------------|--------|
| Main menu (CALJACK-001) | ? Implemented |
| No other dependencies | ? Independent |

---

## Risks Identified

1. **Font support**: Need font that renders Chinese and Russian
2. **Text overflow**: Translated strings may be longer/shorter
3. **Scope creep**: Keep to 3 languages only

---

## Decisions Made

1. Use button-based language selector (not dropdown) for simplicity
2. Language buttons show native names: English, ??, ???????
3. Store current language in singleton, not file

---

## Ready for Reviewer

- [x] User Story complete
- [x] Design Doc created
- [x] Scope verified
- [x] AC are testable
