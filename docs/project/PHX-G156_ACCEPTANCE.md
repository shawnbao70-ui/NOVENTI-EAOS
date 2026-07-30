# PHX-G156 Role→grant Auto-Write Stub Deepen Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Permission / Smart Terminal  
**退出门禁：** named stub 503；仍不 mint；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004 Eng `3` deepen；Usage **DAL-U028**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0175 + Architecture Gate |
| B | `role_grant_auto_write.py` + `routers/role_grants.py` + `app.py` wire |
| C | `role_grant_product.py` G156；permission OpenAPI **1.1.2**；Terminal thin |
| D | PROJECT_STATUS / CHANGELOG / TASKS / ENG tip / Manifest G156 / DAL-U028 |
| E | `test_api_gateway_g156_*` + soften G146/G136 |

## 2. 核心不变量

- Stub only：`POST /permission/role-grants` → 503 `GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED`  
- Detail 含 `auto_write_step` + `grant_minted=false` + Cap≠grant / title≠permission  
- **不**从角色插入 grant；live mint 仍需 **explicit PO**  
- `auto_grant_from_role_enabled` 恒 `false`  
- 不打开支付清算 / Brain execute / Twin authorize / WebAuthn live mint  
- 无新 Alembic；包仍 `0.2.1`；head 仍 `0029_eaos_declared_roles_g90`

## 3. 自动化证据

- 契约：`tests/contracts/test_api_gateway_g156_role_grant_auto_write_stub.py`  
- 回归：`test_api_gateway_g146_*` · `test_api_gateway_g136_*` · `test_delegated_authority_ledger.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0175 |
| Constitution Review | 通过；Cap≠grant；fail-closed；无 BOOK 编辑 |
| Cross-reference Review | 通过；G146 软化；DAL-U028 |
| Documentation Review | 通过；OpenAPI + tip fences |
| Consistency Review | 通过；包 `0.2.1`；head `0029` |
| Gap Analysis | Live mint 另批且需 explicit PO；支付（`4`）暂缓 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Role→grant live auto-write / mint（**explicit PO**）  
- Live WebAuthn credential mint  
- Marketplace 支付清算（Eng `4` 暂缓）  
- Brain execute / Twin authorize  
- 新 Alembic  

## 6. 证据索引

- [PHX-G156 Architecture Gate](PHX-G156_ARCHITECTURE_GATE.md)  
- [ADR-0175](../decisions/ADR-0175-role-grant-auto-write-stub-deepen.md)  
- [permission.openapi.yaml](../api/permission.openapi.yaml)  
- [test_api_gateway_g156_role_grant_auto_write_stub.py](../../tests/contracts/test_api_gateway_g156_role_grant_auto_write_stub.py)  
