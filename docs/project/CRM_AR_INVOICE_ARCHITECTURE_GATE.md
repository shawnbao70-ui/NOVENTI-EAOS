# CRM AR Invoice Shell Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0315, ADR-0330

## Invariants

1. Source DO and its confirmed SO are same-tenant and mandatory.
2. One DO/SO has at most one C10 invoice shell.
3. Same-key retry is idempotent; another key conflicts.
4. Customer, currency and total are frozen source trace.
5. Permission is default-deny and creation is audited.
6. `draft` creates no AR, tax, payment or GL fact.

## Decision

Accepted through Product Owner conversation authorization.
