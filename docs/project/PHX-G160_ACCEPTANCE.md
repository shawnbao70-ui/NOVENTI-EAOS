# PHX-G160 WebAuthn Env-Gated Live Mint Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Identity / Smart Terminal  
**退出门禁：** env-gated challenge-bound mint；默认 503；`attestation_crypto_verified=false`；包 `0.2.1`；Alembic `0029`  
**授权：** **DAL-G008** + DAL-G003 + DAL-G004；Usage **DAL-U037**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0183 + Architecture Gate |
| B | `webauthn_ceremony.py` env gate + options/verify mint → `Identity.BindCredential`；`routers/webauthn.py` |
| C | `webauthn_product.py` G160；auth OpenAPI **1.3.6**；inventory fence attestation-crypto；Terminal thin |
| D | PROJECT_STATUS / CHANGELOG / TASKS / ENG tip / Runbook / Checklist / Compat / Manifest G160 / DAL-G008 / DAL-U037 |
| E | `test_api_gateway_g160_*` + soften G145/G151/G154 |

## 2. 核心不变量

- Default：`POST /auth/webauthn/register/options|verify` → 503 `GATEWAY_WEBAUTHN_REGISTRATION_DISABLED`  
- Enabled + missing RP → 503 `GATEWAY_WEBAUTHN_RP_CONFIG_REQUIRED`  
- Enabled + RP：challenge-bound options mint；verify → webauthn credential bind  
- 响应恒 `attestation_crypto_verified=false` / `attestation_mode=challenge_bound`  
- `/auth/webauthn/register` ABSENT  
- 不打开 Brain execute / Twin authorize / Cap→grant / payment regress  
- 不回归 PHX-G161 Role→grant（DAL-G006/U032）或 G163 T2/T3 intake  
- 无新 Alembic；包仍 `0.2.1`；head 仍 `0029_eaos_declared_roles_g90`

## 3. 自动化证据

- 契约：`tests/contracts/test_api_gateway_g160_webauthn_live_mint.py`  
- 回归：`test_api_gateway_g154_*` · `test_api_gateway_g151_*` · `test_api_gateway_g145_*` · `test_delegated_authority_ledger.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0183 |
| Constitution Review | 通过；无 BOOK 编辑；attestation crypto 仍 Out |
| Cross-reference Review | 通过；G145/G151/G154 软化；DAL-G008/U037；不回归 G161/G163 |
| Documentation Review | 通过；OpenAPI 1.3.6 + tip/runbook fences |
| Consistency Review | 通过；包 `0.2.1`；head `0029` |
| Gap Analysis | packed attestation crypto / single-path register / Brain / Twin / Cap→grant 仍 Explicit Out |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer / Out

- Full packed/TPM attestation-statement crypto verify  
- Single-path `/auth/webauthn/register`  
- Brain execute / Twin authorize  
- Cap→grant invent  
- Const/BP rewrite  
- 新 Alembic  
- Always-on mint without env + RP  

## 6. 证据索引

- [PHX-G160 Architecture Gate](PHX-G160_ARCHITECTURE_GATE.md)  
- [ADR-0183](../decisions/ADR-0183-webauthn-live-mint.md)  
- [auth.openapi.yaml](../api/auth.openapi.yaml)  
- [test_api_gateway_g160_webauthn_live_mint.py](../../tests/contracts/test_api_gateway_g160_webauthn_live_mint.py)  
