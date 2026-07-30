# PHX-G125 Organization Membership Transfer / End Thin Probe Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Organization  
**退出门禁：** Terminal Organization membership transfer/end 薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0144 + Architecture Gate |
| B | Terminal Transfer membership unit / End membership |
| C | 契约 `test_api_gateway_g125_*` |

## 2. 核心不变量

- 禁止 body 上下文提升  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`738 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0144 |
| Constitution Review | 通过；Gateway 薄适配 |
| Cross-reference Review | 通过；G32/G124 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | enterprise lifecycle 见 G126；支付清算、WebAuthn、Role→grant、`0.2.1` 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 6. 证据索引

- [PHX-G125 Architecture Gate](PHX-G125_ARCHITECTURE_GATE.md)
- [ADR-0144](../decisions/ADR-0144-organization-membership-transfer-end-probe.md)
- [test_api_gateway_g125_organization_membership_transfer_end.py](../../tests/contracts/test_api_gateway_g125_organization_membership_transfer_end.py)
