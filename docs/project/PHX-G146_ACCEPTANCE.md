# PHX-G146 Role→grant Product Posture Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Permission / Smart Terminal  
**退出门禁：** 只读姿态面；auto-write 仍关闭；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 Eng `3`；Usage **DAL-U007**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0165 + Architecture Gate |
| B | `role_grant_product.py` helper + `build_role_catalog_status()` wire |
| C | `permission.openapi.yaml` posture fields（v1.1.1）+ Terminal thin row |
| D | PROJECT_STATUS / CHANGELOG / ROADMAP / DUAL_TRACK / TASKS / DAL-U007 |
| E | `test_api_gateway_g146_role_grant_product_posture.py` |

## 2. 核心不变量

- 不实现从角色插入 / mint grant  
- `/permission/role-grants` 仍 ABSENT  
- 手工 G128/G129 与 evaluate-only G83 仍是非 auto-write 相对面  
- Cap≠grant；title≠permission  
- 不打开支付清算 / Brain execute / Twin authorize / WebAuthn ceremony  
- 无新 Alembic；包仍 `0.2.1`；head 仍 `0029_eaos_declared_roles_g90`

## 3. 自动化证据

- 契约：`tests/contracts/test_api_gateway_g146_role_grant_product_posture.py`  
- 回归：`test_api_gateway_g136_*` · `test_delegated_authority_ledger.py` · `test_api_gateway_g145_*`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0165 |
| Constitution Review | 通过；Cap≠grant / title≠permission；无 BOOK 编辑 |
| Cross-reference Review | 通过；G83/G128/G129 仍绿；DAL-U007 记录 |
| Documentation Review | 通过；OpenAPI + README fences 同步 |
| Consistency Review | 通过；包 `0.2.1`；head `0029` |
| Gap Analysis | Eng 下一可选加深或支付清算（`4`）暂缓；WebAuthn ceremony 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Role→grant auto-write / mint from role（later slice if needed）  
- Full WebAuthn credential create/get ceremony  
- Marketplace 支付清算 / 外部仲裁（Eng `4` 暂缓）  
- Brain execute / Twin authorize  
- 新 Alembic（除非后续编号切片）  

## 6. 证据索引

- [PHX-G146 Architecture Gate](PHX-G146_ARCHITECTURE_GATE.md)  
- [ADR-0165](../decisions/ADR-0165-role-grant-product-posture.md)  
- [permission.openapi.yaml](../api/permission.openapi.yaml)  
- [test_api_gateway_g146_role_grant_product_posture.py](../../tests/contracts/test_api_gateway_g146_role_grant_product_posture.py)  
