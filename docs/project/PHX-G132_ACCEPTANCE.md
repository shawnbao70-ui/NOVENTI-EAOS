# PHX-G132 OIDC Login / Callback OpenAPI Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Auth  
**退出门禁：** auth OpenAPI login/callback/providers；包 `0.2.0`；Alembic `0029`  
**人工确认：** refresh/logout/MFA OpenAPI 另批；支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0151 + Architecture Gate |
| B | `auth.openapi.yaml` 增补 login/callback/providers |
| C | 更新 `test_auth_openapi.py` + `test_api_gateway_g132_*` |

## 2. 核心不变量

- 仅契约目录；无 Gateway 行为变更  
- callback JSON 不包含 IdP client_secret / refresh_token 明文  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`755 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0151 |
| Constitution Review | 通过；契约 additive-only |
| Cross-reference Review | 通过；G40/G131 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | refresh/logout 见 G133；MFA OpenAPI、支付清算、WebAuthn、Role→grant、`0.2.1` 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- OIDC refresh / logout OpenAPI（见 G133）；MFA enrollment 另批  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Role→grant 自动写入  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 6. 证据索引

- [PHX-G132 Architecture Gate](PHX-G132_ARCHITECTURE_GATE.md)
- [ADR-0151](../decisions/ADR-0151-oidc-login-callback-openapi.md)
- [auth.openapi.yaml](../api/auth.openapi.yaml)
- [test_api_gateway_g132_oidc_login_callback_openapi.py](../../tests/contracts/test_api_gateway_g132_oidc_login_callback_openapi.py)
