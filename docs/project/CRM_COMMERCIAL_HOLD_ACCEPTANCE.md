# Acceptance — CRM Commercial Hold Gate (C11 / PHX-G304)

## Must pass

1. Customer exposes `commercial_hold` (default false) in model/API.
2. Set/clear hold requires `pkg.crm.customer:update` and is audited.
3. SO confirm fails closed when lineage customer has `commercial_hold=true`.
4. DO create fails closed under the same condition.
5. Incomplete customer lineage fails closed on those paths.
6. Alembic head is `0040_crm_commercial_hold_g304`.
7. No credit_limit, aging, override, Approval, PSP, or GL surfaces opened.

## Evidence

- Contract + gateway tests under `tests/contracts/test_crm_c11_*` /
  `test_api_gateway_g304_*`
- PG integration coverage in `tests/integration/test_crm_c1_postgresql.py`
