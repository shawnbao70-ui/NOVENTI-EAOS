# PHX-G137 Identity Credential/Session Revoke Thin Probe Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Smart Terminal / Identity  
**退出门禁：** credential validate/revoke + session revoke；包 `0.2.0`；Alembic `0029`  
**人工确认：** ≠ AI employee/governor；支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0156 + Architecture Gate |
| B | Gateway routes + serializer + status surfaces |
| C | Terminal Admin 控件 + `test_api_gateway_g137_*` |

## 2. 核心不变量

- 仅薄接线既有 Kernel / OpenAPI；无新迁移  
- revoke 必填 reason；不回传 secret  
- Gateway 不接受 body 抬升 tenant_id / platform_scope  

## 3. 自动化证据

- 本地完整回归：`768 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0156 |
| Constitution Review | 通过；薄适配；fence AI employee/governor |
| Cross-reference Review | 通过；G121 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | AI employee/governor 见 G138；支付清算、WebAuthn、Role→grant、`0.2.1` 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- AI employee / platform governor Gateway + Terminal（见 G138）  
- Role→grant 自动写入  
- Full WebAuthn / MFA registration product page  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Foundation `0.2.1` 发布列车  

## 6. 证据索引

- [PHX-G137 Architecture Gate](PHX-G137_ARCHITECTURE_GATE.md)
- [ADR-0156](../decisions/ADR-0156-identity-credential-session-revoke-probe.md)
- [identity.py](../../api/gateway/routers/identity.py)
- [test_api_gateway_g137_identity_credential_session_revoke.py](../../tests/contracts/test_api_gateway_g137_identity_credential_session_revoke.py)
