# CRM Delivery Order Shell Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0314, ADR-0329

## Invariants

1. Source SO is confirmed and same-tenant.
2. One SO has at most one C9 Delivery Order shell.
3. Same-key retry is idempotent; another key conflicts.
4. Upstream trace, currency and total are frozen.
5. Permission is default-deny and creation is audited.
6. `draft` does not mean allocated, shipped or completed.

## Decision

Accepted through Product Owner conversation authorization.
