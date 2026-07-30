# PHX-G121 Identity Credential / Session Thin Probe Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Identity  
**退出门禁：** Terminal Identity credential/session 薄探针；Identity Terminal 运维面齐；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0140 + Architecture Gate |
| B | Terminal Bind credential / Create session / Validate session |
| C | 契约 `test_api_gateway_g121_*` |

## 2. 核心不变量

- 禁止 body 上下文提升  
- session 路径 subject 经 trusted header 覆盖（非 body）  
- secret 仅 handle；不下发  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`730 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0140 |
| Constitution Review | 通过；Gateway 薄适配；secret 不下发 |
| Cross-reference Review | 通过；G20/G120 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | Organization、支付清算、WebAuthn、Role→grant 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Organization Terminal 薄探针（status/tenant/enterprise 见 G122；unit/membership 另批）  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G121 Architecture Gate](PHX-G121_ARCHITECTURE_GATE.md)
- [ADR-0140](../decisions/ADR-0140-identity-credential-session-probe.md)
- [test_api_gateway_g121_identity_credential_session.py](../../tests/contracts/test_api_gateway_g121_identity_credential_session.py)
