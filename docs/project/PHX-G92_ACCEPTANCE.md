# PHX-G92 Terminal Tenant Roles Catalog Read Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Permission  
**退出门禁：** Terminal 租户角色目录只读；包版本仍 `0.2.0`；Alembic 仍 `0029`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0111 + Architecture Gate |
| B | Terminal Admin「List tenant roles catalog」 |
| C | 契约 `test_api_gateway_g92_*` |

## 2. 核心不变量

- 仅租户上下文调用既有 `/v1/permission/roles`  
- 不写 grants；不替代 G91 平台 CRUD  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`670 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0111 |
| Constitution Review | 通过；租户读 / 无 body 提升 |
| Cross-reference Review | 通过；G88/G91 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | 自动写 grant、WebAuthn 产品页、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G92 Architecture Gate](PHX-G92_ARCHITECTURE_GATE.md)
- [ADR-0111](../decisions/ADR-0111-terminal-tenant-roles-catalog-read.md)
- [test_api_gateway_g92_terminal_tenant_roles.py](../../tests/contracts/test_api_gateway_g92_terminal_tenant_roles.py)
