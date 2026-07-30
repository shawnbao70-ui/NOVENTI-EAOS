# PHX-G123 Organization Unit / Membership Thin Probe Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Organization  
**退出门禁：** Terminal Organization unit/membership 薄探针；Organization Terminal 运维面齐；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0142 + Architecture Gate |
| B | Terminal Upsert unit / Get tree / Add·List memberships |
| C | 契约 `test_api_gateway_g123_*` |

## 2. 核心不变量

- 禁止 body 上下文提升  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`734 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0142 |
| Constitution Review | 通过；Gateway 薄适配 |
| Cross-reference Review | 通过；G21/G122 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | unit status/membership suspension、支付清算、WebAuthn、Role→grant 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Organization unit status / membership suspension Terminal 探针（见 G124）  
- Membership transfer / end Terminal 探针（见 G125）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G123 Architecture Gate](PHX-G123_ARCHITECTURE_GATE.md)
- [ADR-0142](../decisions/ADR-0142-organization-unit-membership-probe.md)
- [test_api_gateway_g123_organization_unit_membership.py](../../tests/contracts/test_api_gateway_g123_organization_unit_membership.py)
