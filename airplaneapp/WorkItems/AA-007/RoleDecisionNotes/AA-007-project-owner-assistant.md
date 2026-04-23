# AA-007 — Project Owner Assistant Decision Notes

## Scope Decision
AA-007 is a single vertical slice: forgot password flow from the login page through token generation, password reset, and re-login. This was explicitly out of scope in AA-001 and is now captured as a deferred backlog item.

## Status
BACKLOG — not yet scheduled for implementation. Priority to be determined after core features (AA-002 through AA-006) are evaluated.

## Key Design Note
Since AirplaneApp is local-only for MVP with no email service, the reset token will be output to the server console. The implementation should use the same swappable service pattern as auth so that plugging in an email provider later is straightforward.
