# PHX-G90 Declared EAOS Roles Catalog SQL Store Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Permission  
**退出门禁：** memory|sql 声明角色；Alembic `0029`；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0109 + Architecture Gate |
| B | `eaos_declared_roles` + Alembic 0029 |
| C | platform CRUD + tenant 聚合 |
| D | 契约 `test_api_gateway_g90_*` |

## 2. 核心不变量

- 默认 memory  
- disable 不进租户 catalog  
- 永不写 grants  

## 3. 自动化证据

- 本地完整回归：`666 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0109 |
| Constitution Review | 通过；平台写 / 租户读 |
| Cross-reference Review | 通过；G88 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | 自动写 grant、WebAuthn 产品页、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G90 Architecture Gate](PHX-G90_ARCHITECTURE_GATE.md)
- [ADR-0109](../decisions/ADR-0109-eaos-declared-roles-sql.md)
