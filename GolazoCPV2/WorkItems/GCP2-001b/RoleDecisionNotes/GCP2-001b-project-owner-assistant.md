# GCP2-001b: Project Owner Assistant Decision Notes

**Work Item**: GCP2-001b - Consent-Based Enforcement  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **Pattern matching over LLM inference**: Chose simple keyword/phrase matching because:
   - Deterministic and predictable
   - No external API dependencies
   - Faster response times
   - Can be enhanced with LLM later if needed

2. **Acceptance criteria reduced to 7**: Original 15 criteria consolidated to comply with PO Assistant rules.

3. **Audit log append-only**: Deviations cannot be deleted to maintain audit integrity.

4. **User's exact words in audit**: Captures the user's original message as the "reason" for traceability.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| LLM-based intent detection | Adds latency, cost, and non-determinism |
| Binary skip/no-skip only | Ambiguous requests need clarification flow |
| No audit trail | Loses traceability for process compliance |

---

## Tradeoffs Accepted

- **Pattern matching limitations**: May miss creative ways users express skip intent. Can add patterns over time.
- **No confidence scoring**: Removed `confidence` field from `RequestAnalysis` to simplify; requests are either explicit, ambiguous, or normal.

---

## Known Limitations

- Pattern matching is English-only
- New skip phrases require code changes to add
- Ambiguous detection may have false positives

---

## Must-Ask Checklist Responses

- **Interface type**: Python library (class API)
- **Target platform**: Cross-platform (Python 3.10+)
- **Data persistence**: Uses GCP2-003 state file for deviations array
- **User type**: Technical (consumed by agent)
