# PHX-G93 Permission Roles Status Observability Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Permission / Smart Terminal  
**退出门禁：** `/v1/permission/roles/status` + Terminal 探针；包版本仍 `0.2.0`；Alembic 仍 `0029`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0112 + Architecture Gate |
| B | `GET /v1/permission/roles/status` 脱敏摘要 |
| C | Terminal Admin「Roles status」 |
| D | 契约 `test_api_gateway_g93_*` |

## 2. 核心不变量

- 只读；不写 grants  
- 不下发原始 grant map env 串或 grants 明细  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`673 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0112 |
| Constitution Review | 通过；租户读 / 无 body 提升 |
| Cross-reference Review | 通过；G83/G88/G92 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | 自动写 grant、WebAuthn 产品页、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G93 Architecture Gate](PHX-G93_ARCHITECTURE_GATE.md)
- [ADR-0112](../decisions/ADR-0112-permission-roles-status.md)
- [test_api_gateway_g93_roles_status.py](../../tests/contracts/test_api_gateway_g93_roles_status.py)
