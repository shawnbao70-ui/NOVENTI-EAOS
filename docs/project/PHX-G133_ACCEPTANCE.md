# PHX-G133 OIDC Refresh / Logout OpenAPI Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Auth  
**退出门禁：** auth OpenAPI refresh/logout；包 `0.2.0`；Alembic `0029`  
**人工确认：** MFA enrollment OpenAPI 见 G134；支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0152 + Architecture Gate |
| B | `auth.openapi.yaml` 增补 refresh/logout + bearerAuth |
| C | 更新 `test_auth_openapi.py` + `test_api_gateway_g133_*` |

## 2. 核心不变量

- 仅契约目录；无 Gateway 行为变更  
- 响应不下发 IdP refresh_token / client_secret  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`757 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0152 |
| Constitution Review | 通过；契约 additive-only |
| Cross-reference Review | 通过；G61/G132 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | MFA enrollment OpenAPI 见 G134；支付清算、WebAuthn 产品页、Role→grant、`0.2.1` 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- OIDC MFA enrollment OpenAPI（见 G134；≠ WebAuthn 产品页）  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Role→grant 自动写入  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 6. 证据索引

- [PHX-G133 Architecture Gate](PHX-G133_ARCHITECTURE_GATE.md)
- [ADR-0152](../decisions/ADR-0152-oidc-refresh-logout-openapi.md)
- [auth.openapi.yaml](../api/auth.openapi.yaml)
- [test_api_gateway_g133_oidc_refresh_logout_openapi.py](../../tests/contracts/test_api_gateway_g133_oidc_refresh_logout_openapi.py)
