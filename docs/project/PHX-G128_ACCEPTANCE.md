# PHX-G128 Permission Policy / Grant Manual Write Thin Probe Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Permission  
**退出门禁：** Terminal permission policy/grant 手工写入薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** 非 Role→grant 自动写入；Marketplace 支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0147 + Architecture Gate |
| B | Terminal Create·Activate policy；Create·Revoke grant |
| C | 契约 `test_api_gateway_g128_*` |

## 2. 核心不变量

- 禁止 body 上下文提升  
- 不启用 Role→grant 自动写入  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`744 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0147 |
| Constitution Review | 通过；Gateway 薄适配；手工写入 ≠ 自动 Role→grant |
| Cross-reference Review | 通过；G22/G94/G95 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | deprecate/delegate 见 G129；支付清算、WebAuthn、Role→grant、`0.2.1` 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Policy deprecation / grant delegation Terminal 探针（见 G129）  
- Role→grant 自动写入 / Role→Policy 绑定  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 6. 证据索引

- [PHX-G128 Architecture Gate](PHX-G128_ARCHITECTURE_GATE.md)
- [ADR-0147](../decisions/ADR-0147-permission-policy-grant-write-probe.md)
- [test_api_gateway_g128_permission_policy_grant_write.py](../../tests/contracts/test_api_gateway_g128_permission_policy_grant_write.py)
