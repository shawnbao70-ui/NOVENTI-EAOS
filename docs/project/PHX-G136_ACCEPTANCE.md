# PHX-G136 Permission Roles List OpenAPI Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Contracts / Permission  
**退出门禁：** `permission.openapi.yaml` GET /roles；包 `0.2.0`；Alembic `0029`  
**人工确认：** ≠ Role→grant；支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0155 + Architecture Gate |
| B | `permission.openapi.yaml` 增补 GET /roles（v1.1.0） |
| C | 更新 `test_permission_openapi.py` + `test_api_gateway_g136_*` |

## 2. 核心不变量

- 仅契约目录；无 Gateway 行为变更  
- 文档明确只读聚合；≠ Role→grant；≠ `/platform/roles`  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`766 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0155 |
| Constitution Review | 通过；契约 additive-only；fence Role→grant |
| Cross-reference Review | 通过；G135 platform roles 仍区分 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | 支付清算、WebAuthn、Role→grant、`0.2.1` 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Role→grant 自动写入  
- Full WebAuthn / MFA registration product page  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Foundation `0.2.1` 发布列车  

## 6. 证据索引

- [PHX-G136 Architecture Gate](PHX-G136_ARCHITECTURE_GATE.md)
- [ADR-0155](../decisions/ADR-0155-permission-roles-list-openapi.md)
- [permission.openapi.yaml](../api/permission.openapi.yaml)
- [test_api_gateway_g136_permission_roles_list_openapi.py](../../tests/contracts/test_api_gateway_g136_permission_roles_list_openapi.py)
