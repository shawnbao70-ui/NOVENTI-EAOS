# PHX-G134 OIDC MFA Enrollment OpenAPI Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Auth  
**退出门禁：** auth OpenAPI mfa-enrollment；包 `0.2.0`；Alembic `0029`  
**人工确认：** ≠ WebAuthn 产品页；支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0153 + Architecture Gate |
| B | `auth.openapi.yaml` 增补 mfa-enrollment |
| C | 更新 `test_auth_openapi.py` + `test_api_gateway_g134_*` |

## 2. 核心不变量

- 仅契约目录；无 Gateway 行为变更  
- 文档明确为 IdP enrollment redirect，非 WebAuthn 产品面  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`759 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0153 |
| Constitution Review | 通过；契约 additive-only；fence WebAuthn |
| Cross-reference Review | 通过；G89/G133 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | Platform OpenAPI 见 G135；WebAuthn、支付清算、Role→grant、`0.2.1` 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Full WebAuthn / MFA registration product page  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Role→grant 自动写入  
- Foundation `0.2.1` 发布列车  

## 6. 证据索引

- [PHX-G134 Architecture Gate](PHX-G134_ARCHITECTURE_GATE.md)
- [ADR-0153](../decisions/ADR-0153-oidc-mfa-enrollment-openapi.md)
- [auth.openapi.yaml](../api/auth.openapi.yaml)
- [test_api_gateway_g134_oidc_mfa_enrollment_openapi.py](../../tests/contracts/test_api_gateway_g134_oidc_mfa_enrollment_openapi.py)
