# LLM-0006 — Project Owner Assistant Notes

## Decision: Single story, not decomposed
One user-observable outcome: "give the client a URL and a question, get an answer about that URL's content." Single vertical slice.

## Scope Justification
- URL fetch + text extraction + prompt injection is a cohesive feature
- Kept to static HTML only — JS rendering (Playwright/Selenium) would be a separate story
- HTML-to-text uses stdlib to avoid new dependencies
- Content truncation avoids token-limit surprises

## Must-Ask Checklist
- [x] Interface type: Python library (established)
- [x] Target platform: Cross-platform (established)
- [x] Data persistence: In-memory only (no caching)
- [x] User type: Developers (established)

All items already established by prior work items.
