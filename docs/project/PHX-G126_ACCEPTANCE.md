# PHX-G126 Organization Enterprise Lifecycle Thin Probe Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Organization  
**退出门禁：** Terminal Organization enterprise lifecycle 薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0145 + Architecture Gate |
| B | Terminal Suspend / Reactivate / Close enterprise |
| C | 契约 `test_api_gateway_g126_*` |

## 2. 核心不变量

- 禁止 body 上下文提升  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`740 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0145 |
| Constitution Review | 通过；Gateway 薄适配 |
| Cross-reference Review | 通过；G32/G125 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | platform tenant lifecycle 见 G127；permission write、支付清算、WebAuthn、Role→grant、`0.2.1` 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Platform tenant lifecycle Terminal 探针（见 G127）  
- Permission policy/grant 手工写入 Terminal 探针（≠ Role→grant 自动写入）  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 6. 证据索引

- [PHX-G126 Architecture Gate](PHX-G126_ARCHITECTURE_GATE.md)
- [ADR-0145](../decisions/ADR-0145-organization-enterprise-lifecycle-probe.md)
- [test_api_gateway_g126_organization_enterprise_lifecycle.py](../../tests/contracts/test_api_gateway_g126_organization_enterprise_lifecycle.py)
