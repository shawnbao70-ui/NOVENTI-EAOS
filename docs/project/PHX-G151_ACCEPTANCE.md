# PHX-G151 WebAuthn Ceremony Stub Deepen Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Auth / Smart Terminal  
**退出门禁：** named stub 503；registration 仍关闭；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004 Eng `2` deepen；Usage **DAL-U023**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0170 + Architecture Gate |
| B | `webauthn_ceremony.py` + `routers/webauthn.py` + `app.py` wire |
| C | `webauthn_product.py` G151 posture；`auth.openapi.yaml` v1.3.3 + Terminal thin update |
| D | PROJECT_STATUS / CHANGELOG / ROADMAP / DUAL_TRACK / TASKS / ENG tip / DAL-U023 |
| E | `test_api_gateway_g151_webauthn_ceremony_stub.py` + soften G145/G134/auth empty-routes fences |

## 2. 核心不变量

- Stub routes only：`POST /auth/webauthn/register/options` 与 `…/verify` → 503 `GATEWAY_WEBAUTHN_REGISTRATION_DISABLED`  
- **不** mint PublicKeyCredential options / attestation；即使 `EAOS_WEBAUTHN_REGISTRATION_ENABLED=true`  
- `/auth/webauthn/register` 仍 ABSENT（G134 fence 保持）  
- IdP MFA enrollment redirect（G89/G134）仍是唯一 live enroll 路径  
- 不打开 Role→grant mint / 支付清算 / Brain execute / Twin authorize  
- 无新 Alembic；包仍 `0.2.1`；head 仍 `0029_eaos_declared_roles_g90`

## 3. 自动化证据

- 契约：`tests/contracts/test_api_gateway_g151_webauthn_ceremony_stub.py`  
- 回归：`test_api_gateway_g145_*` · `test_auth_openapi.py` · `test_api_gateway_g134_*` · `test_delegated_authority_ledger.py` · `test_release_g144.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0170 |
| Constitution Review | 通过；fail-closed 持有；无 BOOK 编辑 |
| Cross-reference Review | 通过；G145/G134/auth 仍绿（routes fence 已软化）；DAL-U023 记录 |
| Documentation Review | 通过；OpenAPI + README / tip fences 同步 |
| Consistency Review | 通过；包 `0.2.1`；head `0029` |
| Gap Analysis | Live create/get mint 另批；Role→grant mint 需 explicit PO；支付清算（`4`）暂缓 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Live WebAuthn credential create/get / attestation mint  
- Honoring `EAOS_WEBAUTHN_REGISTRATION_ENABLED` as a mint switch  
- Role→grant auto-write / mint from role（explicit PO）  
- Marketplace 支付清算 / 外部仲裁（Eng `4` 暂缓）  
- Brain execute / Twin authorize  
- 新 Alembic（除非后续编号切片）  

## 6. 证据索引

- [PHX-G151 Architecture Gate](PHX-G151_ARCHITECTURE_GATE.md)  
- [ADR-0170](../decisions/ADR-0170-webauthn-ceremony-stub-deepen.md)  
- [auth.openapi.yaml](../api/auth.openapi.yaml)  
- [test_api_gateway_g151_webauthn_ceremony_stub.py](../../tests/contracts/test_api_gateway_g151_webauthn_ceremony_stub.py)  
