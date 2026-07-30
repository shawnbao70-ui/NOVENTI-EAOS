# PHX-G131 Auth OpenAPI Status Catalog Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Auth  
**退出门禁：** `auth.openapi.yaml` status 目录；Manifest 12 份；包 `0.2.0`；Alembic `0029`  
**人工确认：** login/callback OpenAPI 另批；支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0150 + Architecture Gate |
| B | `auth.openapi.yaml` + Manifest/README |
| C | `test_auth_openapi.py` + `test_api_gateway_g131_*`；release inventory 12 |

## 2. 核心不变量

- 仅契约目录；无 Gateway 行为变更  
- status 永不暴露 secret / jti 列表  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`753 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0150 |
| Constitution Review | 通过；契约 additive-only |
| Cross-reference Review | 通过；release inventory 12 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | login OpenAPI 见 G132；支付清算、WebAuthn、Role→grant、`0.2.1` 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- OIDC login / callback / providers OpenAPI（见 G132）；refresh / logout / MFA 另批  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Role→grant 自动写入  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 6. 证据索引

- [PHX-G131 Architecture Gate](PHX-G131_ARCHITECTURE_GATE.md)
- [ADR-0150](../decisions/ADR-0150-auth-openapi-status-catalog.md)
- [auth.openapi.yaml](../api/auth.openapi.yaml)
- [test_auth_openapi.py](../../tests/contracts/test_auth_openapi.py)
- [test_api_gateway_g131_auth_openapi_status_catalog.py](../../tests/contracts/test_api_gateway_g131_auth_openapi_status_catalog.py)
