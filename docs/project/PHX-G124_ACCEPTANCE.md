# PHX-G124 Organization Lifecycle Thin Probe Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Organization  
**退出门禁：** Terminal Organization lifecycle 薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0143 + Architecture Gate |
| B | Terminal Set unit status / Suspend·Reactivate membership |
| C | 契约 `test_api_gateway_g124_*` |

## 2. 核心不变量

- 禁止 body 上下文提升  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`736 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0143 |
| Constitution Review | 通过；Gateway 薄适配 |
| Cross-reference Review | 通过；G32/G123 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | membership transfer/end 见 G125；支付清算、WebAuthn、Role→grant 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Membership transfer / end Terminal 探针（见 G125）  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G124 Architecture Gate](PHX-G124_ARCHITECTURE_GATE.md)
- [ADR-0143](../decisions/ADR-0143-organization-lifecycle-probe.md)
- [test_api_gateway_g124_organization_lifecycle.py](../../tests/contracts/test_api_gateway_g124_organization_lifecycle.py)
