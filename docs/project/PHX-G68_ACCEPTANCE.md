# PHX-G68 JWT Tenant IdP Federation Enforcement Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway  
**退出门禁：** 租户面 JWT 与 OIDC 共用联邦强制；平台面/开发头不强制；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0087 + Architecture Gate |
| B | `context_from_tenant_claims` 强制 |
| C | issuer 解析（`eaos_oidc_issuer` / 非 EAOS `iss`） |
| D | 契约 `test_api_gateway_g68_*` |

## 2. 核心不变量

- 复用 `EAOS_TENANT_IDP_FEDERATION`  
- EAOS 签发令牌无 `eaos_oidc_issuer` → deny  
- 平台面与开发受信头不强制  
- `federation.planes` = `["oidc","jwt"]`  

## 3. 自动化证据

- 本地完整回归：`553 passed`（`tests/contracts`）  
- Alembic head：仍为 `0027_tenant_idp_bindings_g67`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0087 |
| Constitution Review | 通过；仅租户面 |
| Cross-reference Review | 通过；G66/G67 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0027` |
| Gap Analysis | 联邦 UI、支付清算、网格 CRD 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 联邦 UI / social login  
- 网格 CRD / 多区域 / KMS  

## 6. 证据索引

- [PHX-G68 Architecture Gate](PHX-G68_ARCHITECTURE_GATE.md)
- [ADR-0087](../decisions/ADR-0087-jwt-tenant-idp-federation.md)
