# PHX-G88 Opt-in EAOS Roles Catalog Gate Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Permission  
**退出门禁：** 只读角色目录聚合；无 Alembic；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0107 + Architecture Gate |
| B | `role_catalog` 聚合 |
| C | `GET /v1/permission/roles` |
| D | 契约 `test_api_gateway_g88_*` |

## 2. 核心不变量

- 空源 = 空目录  
- 永不写 grants  
- 需租户受信上下文  

## 3. 自动化证据

- 本地完整回归：`656 passed`（`tests/contracts`）  
- Alembic head：仍为 `0028_tenant_idp_binding_priority_g78`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0107 |
| Constitution Review | 通过；Gateway 只读；无 body 提升 |
| Cross-reference Review | 通过；G81/G83 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0028` |
| Gap Analysis | Role SQL/自动写 grant、MFA 注册、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Role SQL 表 / 自动写 grant  
- MFA 注册 / WebAuthn UX  

## 6. 证据索引

- [PHX-G88 Architecture Gate](PHX-G88_ARCHITECTURE_GATE.md)
- [ADR-0107](../decisions/ADR-0107-eaos-roles-catalog.md)
