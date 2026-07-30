# PHX-G22 Gateway Permission HTTP Surface Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 薄适配；Evaluate 不可 body 冒充 principal

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0037 + Architecture Gate |
| B | 七条 Permission 路由薄适配 |
| C | PERMISSION_* 错误映射 + DI |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 路径对齐 `permission.openapi.yaml`
- Evaluate principal = 受信头 subject（禁止 body 冒充）
- Body 禁止 `tenant_id` / `platform_scope`；`principal_id` 为资源字段
- 默认 `PermissionService()`；测试注入 grant administrators

## 3. 自动化证据

- 本地完整回归：`339 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0037 |
| Constitution Review | 通过；默认拒绝与审计边界保留在 Kernel |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18–G21 仍绿 |
| Gap Analysis | deprecate/delegate HTTP 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- Policy deprecation / Grant delegation HTTP
- JWT/OIDC；平台面；商业 Marketplace

## 6. 证据索引

- [PHX-G22 Architecture Gate](PHX-G22_ARCHITECTURE_GATE.md)
- [ADR-0037](../decisions/ADR-0037-gateway-permission-http-surface.md)
- [permission.openapi.yaml](../api/permission.openapi.yaml)
- [Gateway Permission router](../../api/gateway/routers/permission.py)
