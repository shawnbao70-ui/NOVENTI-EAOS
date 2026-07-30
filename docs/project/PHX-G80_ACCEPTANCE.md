# PHX-G80 OIDC amr/acr Auth Context Gate Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**退出门禁：** `EAOS_OIDC_REQUIRED_AMR` / `REQUIRED_ACR`；mint fail-closed；status 可观测；无 Alembic；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0099 + Architecture Gate |
| B | amr/acr helper + `map_oidc_claims_to_eaos` 门禁 |
| C | oidc status 字段 |
| D | 契约 `test_api_gateway_g80_*` |

## 2. 核心不变量

- 空配置 = 关闭  
- amr 任一命中；acr 精确命中  
- 无 MFA 注册 UI / social login / claim→role  

## 3. 自动化证据

- 本地完整回归：`614 passed`（`tests/contracts`）  
- Alembic head：仍为 `0028_tenant_idp_binding_priority_g78`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0099 |
| Constitution Review | 通过；Gateway OIDC 边界 |
| Cross-reference Review | 通过；G79 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0028` |
| Gap Analysis | MFA 注册、social login、claim→role、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- MFA 注册 / step-up UX / WebAuthn  
- Social login / claim→role  
- 多 issuer 登录重定向  

## 6. 证据索引

- [PHX-G80 Architecture Gate](PHX-G80_ARCHITECTURE_GATE.md)
- [ADR-0099](../decisions/ADR-0099-oidc-amr-acr-gate.md)
