# PHX-G145 WebAuthn / MFA Product Posture Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Auth / Smart Terminal  
**退出门禁：** 只读姿态面；注册仪式仍关闭；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 Eng `2`；Usage **DAL-U006**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0164 + Architecture Gate |
| B | `webauthn_product.py` helper + `oidc_status()` wire |
| C | `auth.openapi.yaml` posture fields（v1.3.1）+ Terminal thin row |
| D | PROJECT_STATUS / CHANGELOG / ROADMAP / DUAL_TRACK / TASKS / DAL-U006 |
| E | `test_api_gateway_g145_webauthn_product_posture.py` |

## 2. 核心不变量

- 不实现 WebAuthn credential create/get  
- `/auth/webauthn/register` 仍 ABSENT（G134 fence 保持）  
- IdP MFA enrollment redirect（G89/G134）仍是唯一 live enroll 路径  
- 不打开 Role→grant / 支付清算 / Brain execute / Twin authorize  
- 无新 Alembic；包仍 `0.2.1`；head 仍 `0029_eaos_declared_roles_g90`

## 3. 自动化证据

- 契约：`tests/contracts/test_api_gateway_g145_webauthn_product_posture.py`  
- 回归：`test_api_gateway_g134_*` · `test_auth_openapi.py` · `test_delegated_authority_ledger.py` · `test_release_g144.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0164 |
| Constitution Review | 通过；fail-closed 持有；无 BOOK 编辑 |
| Cross-reference Review | 通过；G89/G134 仍绿；DAL-U006 记录 |
| Documentation Review | 通过；OpenAPI + README fences 同步 |
| Consistency Review | 通过；包 `0.2.1`；head `0029` |
| Gap Analysis | Eng 下一可选加深或支付清算（`4`）暂缓；完整 WebAuthn ceremony 另批；Role→grant thin posture via G146 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Full WebAuthn credential create/get ceremony（later slice if needed）  
- Role→grant 自动写入（Eng `3` thin posture via G146；auto-write still deferred）  
- Marketplace 支付清算 / 外部仲裁（Eng `4` 暂缓）  
- Brain execute / Twin authorize  
- 新 Alembic（除非后续编号切片）  

## 6. 证据索引

- [PHX-G145 Architecture Gate](PHX-G145_ARCHITECTURE_GATE.md)  
- [ADR-0164](../decisions/ADR-0164-webauthn-mfa-product-posture.md)  
- [auth.openapi.yaml](../api/auth.openapi.yaml)  
- [test_api_gateway_g145_webauthn_product_posture.py](../../tests/contracts/test_api_gateway_g145_webauthn_product_posture.py)  
