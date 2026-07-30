# PHX-G147 OIDC Login Product Surface Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Auth / Smart Terminal  
**退出门禁：** 只读姿态面 + Terminal 面板；无新协议；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003；Usage **DAL-U008**；关闭 **T-0189**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0166 + Architecture Gate |
| B | `oidc_login_product.py` helper + `oidc_status()` wire |
| C | `auth.openapi.yaml` posture fields（v1.3.2）+ Terminal 「OIDC Login Product」 panel |
| D | PROJECT_STATUS / CHANGELOG / ROADMAP / DUAL_TRACK / TASKS T-0189 / DAL-U008 |
| E | `test_api_gateway_g147_oidc_login_product.py` |

## 2. 核心不变量

- 不引入新认证协议；仅命名/组合既有 Authorization Code 面（G40/G61/G132）  
- 未配置 OIDC 仍 fail-closed（503）  
- 不实现 WebAuthn credential create/get；`/auth/webauthn/register` 仍 ABSENT  
- 不打开 Role→grant mint / 支付清算 / Brain execute / Twin authorize  
- 无新 Alembic；包仍 `0.2.1`；head 仍 `0029_eaos_declared_roles_g90`

## 3. 自动化证据

- 契约：`tests/contracts/test_api_gateway_g147_oidc_login_product.py`  
- 回归：`test_api_gateway_g145_*` · `test_auth_openapi.py` · `test_delegated_authority_ledger.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0166 |
| Constitution Review | 通过；fail-closed 持有；无 BOOK 编辑 |
| Cross-reference Review | 通过；G40/G61/G132 + G145 仍绿；DAL-U008 记录；T-0189 关闭 |
| Documentation Review | 通过；OpenAPI + README fences 同步 |
| Consistency Review | 通过；包 `0.2.1`；head `0029` |
| Gap Analysis | Eng 下一可选加深仍为 WebAuthn ceremony / Role→grant auto-write；支付清算（`4`）暂缓 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Full WebAuthn credential create/get ceremony  
- Role→grant auto-write / mint from role  
- Marketplace 支付清算 / 外部仲裁（Eng `4` 暂缓）  
- Brain execute / Twin authorize  
- 新 Alembic（除非后续编号切片）  

## 6. 证据索引

- [PHX-G147 Architecture Gate](PHX-G147_ARCHITECTURE_GATE.md)  
- [ADR-0166](../decisions/ADR-0166-oidc-login-product-surface.md)  
- [auth.openapi.yaml](../api/auth.openapi.yaml)  
- [test_api_gateway_g147_oidc_login_product.py](../../tests/contracts/test_api_gateway_g147_oidc_login_product.py)  
