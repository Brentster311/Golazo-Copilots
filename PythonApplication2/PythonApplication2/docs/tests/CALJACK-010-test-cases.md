# Test Cases: CALJACK-010

**Work Item**: CALJACK-010 - Settings Menu with Language Selection  
**Date**: 2025-01-XX

---

## Test Categories

### 1. LanguageManager Tests

| ID | Test | Expected |
|----|------|----------|
| LM-1 | LanguageManager is singleton | Same instance returned |
| LM-2 | Default language is English | `get_current()` returns 'en' |
| LM-3 | Get translation key | Returns translated string |
| LM-4 | Get missing key | Returns key itself |
| LM-5 | Set language to Chinese | Language changes to 'zh' |
| LM-6 | Set language to Russian | Language changes to 'ru' |
| LM-7 | Set invalid language | Language unchanged |
| LM-8 | All keys exist in all languages | No missing translations |

### 2. Settings State Tests

| ID | Test | Expected |
|----|------|----------|
| SS-1 | SettingsState creates | Instance not None |
| SS-2 | Has back button | back_button exists |
| SS-3 | Has language buttons | 3 language buttons exist |
| SS-4 | Back returns to menu | Returns STATE_MENU |

### 3. Menu Integration Tests

| ID | Test | Expected |
|----|------|----------|
| MI-1 | Menu has settings button | settings_button exists |
| MI-2 | Settings button returns STATE_SETTINGS | Correct state returned |

### 4. Translation Coverage Tests

| ID | Test | Expected |
|----|------|----------|
| TC-1 | All English keys defined | No missing keys |
| TC-2 | All Chinese keys defined | No missing keys |
| TC-3 | All Russian keys defined | No missing keys |

---

## Manual Tests

| ID | Test | Steps | Expected |
|----|------|-------|----------|
| MT-1 | Visual language switch | 1. Open Settings 2. Click ?? 3. Observe | All text changes to Chinese |
| MT-2 | Chinese characters render | Switch to Chinese | Characters visible, not boxes |
| MT-3 | Russian characters render | Switch to Russian | Cyrillic visible, not boxes |
| MT-4 | Text fits in buttons | All 3 languages | No overflow or clipping |
