# QA Decision Notes — EES-00006

## Review Summary
- 1 major finding (FactExtractor constructor backward compatibility)
- 3 minor findings (default mismatch, source display, validation timing)
- 14 test cases: 10 unit (automatable), 4 manual (dialog interaction)

## Key Concerns
- The FactExtractor kwargs approach needs architect sign-off to ensure CLI path is unaffected
- Settings resolution order (config → env → default) is clear and testable
