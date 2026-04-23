# AA-002 — Project Owner Assistant Decision Notes

## Scope Decision
AA-002 delivers organization creation, role-based membership, and the invitation flow. This is the second vertical slice — users can now form groups and assign roles, which is the prerequisite for shared aircraft management.

## Why This Scope
- Aircraft profiles (AA-003) need an org context — you can't add a plane without an org to own it.
- The invite flow is included because an org with no way to add members isn't useful.
- Aircraft detail fields (make/model/engine) are deferred to AA-003 to keep this story focused on the org + membership model.

## Key Design Decisions
- **Invite-code approach (not email):** Since the app is local-only MVP with no email service, the admin copies an invite link/code and shares it externally. This mirrors how Discord invites work — simple and effective.
- **Multi-org support from day one:** The user specified that a user can belong to multiple orgs. The Membership junction table (user + org + role) supports this cleanly.
- **Org switcher in UI:** Needed immediately because users can have multiple orgs. A dropdown or sidebar selector to switch active org context.

## Must-Ask Checklist
- [x] Interface type: web (established in AA-001)
- [x] Target platform: local Windows (established in AA-001)
- [x] Data persistence: SQLite via Prisma (established in AA-001)
