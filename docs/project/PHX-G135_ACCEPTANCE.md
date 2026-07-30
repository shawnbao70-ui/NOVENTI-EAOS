# PHX-G135 Platform OpenAPI Catalog Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Platform  
**退出门禁：** `platform.openapi.yaml`；Manifest 13 份；包 `0.2.0`；Alembic `0029`  
**人工确认：** ≠ Role→grant；支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0154 + Architecture Gate |
| B | `platform.openapi.yaml` + Manifest/README 12→13 |
| C | `test_platform_openapi.py` + `test_api_gateway_g135_*`；inventory 计数更新 |

## 2. 核心不变量

- 仅契约目录；无 Gateway 行为变更  
- JWKS plaintext 永不出现在响应 schema  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`764 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0154 |
| Constitution Review | 通过；契约 additive-only；fence Role→grant |
| Cross-reference Review | 通过；release inventory 13 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | `/permission/roles` OpenAPI 见 G136；支付清算、WebAuthn、Role→grant、`0.2.1` 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- `GET /permission/roles` OpenAPI（见 G136）  
- Role→grant 自动写入  
- Full WebAuthn / MFA registration product page  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Foundation `0.2.1` 发布列车  

## 6. 证据索引

- [PHX-G135 Architecture Gate](PHX-G135_ARCHITECTURE_GATE.md)
- [ADR-0154](../decisions/ADR-0154-platform-openapi-catalog.md)
- [platform.openapi.yaml](../api/platform.openapi.yaml)
- [test_platform_openapi.py](../../tests/contracts/test_platform_openapi.py)
- [test_api_gateway_g135_platform_openapi_catalog.py](../../tests/contracts/test_api_gateway_g135_platform_openapi_catalog.py)
