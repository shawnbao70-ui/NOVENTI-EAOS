# CRM Confirm Approval Hook Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0332

## Invariants

1. Hook attaches only to Sales Order confirm.
2. Policy default is false; existing confirms remain green.
3. Required + unavailable/denied/missing port fails closed.
4. human_confirm and commercial_hold remain mandatory predecessors.
5. Permission default-deny on policy read/update.
6. No Approval Center product surface or invoice issue path.

## Decision

Accepted through Product Owner conversation authorization.
