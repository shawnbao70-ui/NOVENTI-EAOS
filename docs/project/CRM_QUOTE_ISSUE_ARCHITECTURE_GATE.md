# CRM Quote Issue Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0333

## Invariants

1. Draft→Issued is explicit, auditable, and human-confirmed.
2. Issued requires ≥1 active quote line.
3. Same issue key replays; different key conflicts.
4. Convert requires issued.
5. Issued quotes reject commercial header/line mutation.
6. No email/PDF/Approval/Workflow side effects.

## Decision

Accepted through Product Owner conversation authorization.
