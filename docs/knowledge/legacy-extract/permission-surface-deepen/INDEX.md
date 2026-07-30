# Permission Surface Deepen — INDEX

**Verified:** 2026-07-23  
**Legacy root:** `H:\Workspace\EZAM_CRM - 9.0\`

## Module Index

| Module | Evidence | Primary locus | Main conclusion |
|--------|----------|---------------|-----------------|
| [ui_vs_server_rbac.md](ui_vs_server_rbac.md) | Strong | templates + domain routers | UI visibility and server authorization frequently diverge |
| [convert_do_route_gaps.md](convert_do_route_gaps.md) | Strong | sales/inventory/platform routes | two GET creation paths enforce different permissions; one has no server gate |
| [admin_bypass_matrix.md](admin_bypass_matrix.md) | Strong | checker + permission center | Admin/Super Admin bypass all invoked checker actions |
| [opt_in_checks.md](opt_in_checks.md) | Strong | security middleware + routers | CSRF is centralized, resource authorization is route-by-route opt-in |

## Cross-pack Map

| This pack | Authority referenced | Relationship |
|-----------|----------------------|--------------|
| all modules | `../risk-catalog/permission_holes.md` | deepens PH-001/002/003/006/007/008 without duplicating catalog |
| UI/server + admin | `../platform-obs/identity_obs.md` | applies observed role/session/checker authority to business routes |
| opt-in | `../platform-obs/platform.md` | relates route registration/canonical-residual structure |
| convert DO | `../order-chain/so_to_do.md` | permission surface around SO→DO process |
| convert DO | `../numbering-collision-deepen/generators_matrix.md` | distinct DO numbering implementations |
| UI/server | `../governance/approval.md` | Human Approved is not approver authorization |

## Enforcement Summary

| Concern | Observed authority | Coverage |
|---------|--------------------|----------|
| Authentication state | session/user helpers | route opt-in; global requirement not proven |
| Module/action RBAC | `core/permission/checker.py` | route/template/service opt-in |
| Privileged bypass | Admin/Super Admin role strings | unconditional whenever checker invoked |
| CSRF | global middleware | mutating methods only; GET excluded |
| Owner scope | per-query filters | inconsistent |
| Tenant scope | optional/default-compatible helpers | inconsistent |
| Human intent | Type A form confirmation | selected commands only |
| Route authority | registration order + duplicate filter | standard bootstrap known; alternatives UNKNOWN |

## Critical Permission Conclusions

1. “Default deny”只描述 checker 函数行为，不能描述整个应用；endpoint 必须先显式调用 checker。
2. 按钮隐藏不具 server authority；直链、脚本和 residual alias 必须独立授权。
3. `/create_do` 的 UI gate 为 Delivery Orders add，而 server 无 gate；`/convert_do` 则检查 Sales Orders edit，资源/action contract 漂移。
4. Admin/Super Admin bypass 是 checker short-circuit；它不改变业务校验，也不修复 GET、CSRF、对象范围或审计。
5. CSRF middleware 将 GET 视作 safe，Legacy GET writes 因而构成结构性盲区。
6. 模块级 `can_*` matrix 没有表达 tenant、owner、specified approver、source-state、idempotency。

## Coverage Check

| File | Rules | Validations | Data semantics | Evidence rows | UNKNOWN rows | Result |
|------|-------|-------------|----------------|---------------|--------------|--------|
| `ui_vs_server_rbac.md` | 24 | 12 | 17 | 18 | 10 | PASS |
| `convert_do_route_gaps.md` | 22 | 12 | 16 | 17 | 9 | PASS |
| `admin_bypass_matrix.md` | 22 | 13 | 18 | 17 | 9 | PASS |
| `opt_in_checks.md` | 25 | 12 | 21 | 22 | 10 | PASS |

Required threshold (“同 A”): rules ≥8, validations ≥6, data semantics ≥8, evidence rows ≥6, UNKNOWN+searched paths ≥5.

## Read-only Source Families

- `core/permission/**`
- `core/auth/**`
- `core/security/**`
- `core/database/tenant_scope.py`
- `apps/quotation/**`
- `apps/sales/**`
- `apps/inventory/**`
- `apps/finance/**`
- `apps/approval/**`
- `apps/permission_center/**`
- `apps/platform/**`
- `apps/brand_center/**`
- `templates/**`
- `bootstrap/**`
- `database/**`
- `docs/reports/**`

## Write Boundary

Only `docs/knowledge/legacy-extract/permission-surface-deepen/**` was created or modified for this phase.
