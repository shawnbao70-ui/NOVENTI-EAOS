# PHX-G161 Role→grant Env-Gated Live Mint Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Permission / Smart Terminal  
**退出门禁：** env-gated mint；默认 503；Cap≠grant；包 `0.2.1`；Alembic `0029`  
**授权：** **DAL-G006** + DAL-G003 + DAL-G004；Usage **DAL-U032**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0179 + Architecture Gate |
| B | `role_grant_auto_write.py` env gate + `mint_grants_from_roles`；`routers/role_grants.py` |
| C | `role_grant_product.py` G161；permission OpenAPI **1.1.3**；Terminal thin |
| D | PROJECT_STATUS / CHANGELOG / TASKS / ENG tip / Runbook / Checklist / Compat / Manifest G161 / DAL-G006 / DAL-U032 |
| E | `test_api_gateway_g161_*` + soften G146/G156/G136 |

## 2. 核心不变量

- Default：`POST /permission/role-grants` → 503 `GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED`  
- Enabled + empty map → 503 `GATEWAY_ROLE_GRANT_MAP_REQUIRED`  
- Enabled + map：按 roles 展开 G83 map → `Permission.grant`（非 Cap→grant）  
- `cap_is_grant=false` / `title_is_permission=false`  
- 不打开支付清算 / Brain execute / Twin authorize  
- 无新 Alembic；包仍 `0.2.1`；head 仍 `0029_eaos_declared_roles_g90`

## 3. 自动化证据

- 契约：`tests/contracts/test_api_gateway_g161_role_grant_live_mint.py`  
- 回归：`test_api_gateway_g156_*` · `test_api_gateway_g146_*` · `test_api_gateway_g136_*` · `test_delegated_authority_ledger.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0179 |
| Constitution Review | 通过；Cap≠grant；title≠permission；无 BOOK 编辑 |
| Cross-reference Review | 通过；G146/G156 软化；DAL-G006/U032 |
| Documentation Review | 通过；OpenAPI 1.1.3 + tip/runbook fences |
| Consistency Review | 通过；包 `0.2.1`；head `0029` |
| Gap Analysis | payment / Brain / Twin / full OpenAPI / Cap→grant 仍 Explicit Out |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer / Out

- Marketplace 支付清算（Eng `4` 暂缓）  
- Brain execute / Twin authorize  
- Cap→grant invent  
- 全量 OpenAPI HTTP parity  
- Const/BP rewrite  
- WebAuthn attestation crypto verify（G160 remainder；独立）  
- 新 Alembic  

## 6. 证据索引

- [PHX-G161 Architecture Gate](PHX-G161_ARCHITECTURE_GATE.md)  
- [ADR-0179](../decisions/ADR-0179-role-grant-live-mint.md)  
- [permission.openapi.yaml](../api/permission.openapi.yaml)  
- [test_api_gateway_g161_role_grant_live_mint.py](../../tests/contracts/test_api_gateway_g161_role_grant_live_mint.py)  
