# PHX-G84 OIDC Multi-Provider Login Gate Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**退出门禁：** 可选 login providers 目录 + `?provider=`；无 Alembic；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0103 + Architecture Gate |
| B | `oidc_login_providers` + login/callback overlay |
| C | `/providers` + status + Terminal 薄链接 |
| D | 契约 `test_api_gateway_g84_*` |

## 2. 核心不变量

- 空目录 = 关闭（主 OIDC 不变）  
- 未知 provider fail-closed  
- 不泄露 client_secret  

## 3. 自动化证据

- 本地完整回归：`640 passed`（`tests/contracts`）  
- Alembic head：仍为 `0028_tenant_idp_binding_priority_g78`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0103 |
| Constitution Review | 通过；Gateway OIDC 边界 |
| Cross-reference Review | 通过；G40/G81 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0028` |
| Gap Analysis | per-provider refresh、MFA 注册、完整社交 UX、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 按 provider 的 refresh/logout 路由  
- MFA 注册 / WebAuthn UX  
- 完整社交品牌与账号关联产品流  

## 6. 证据索引

- [PHX-G84 Architecture Gate](PHX-G84_ARCHITECTURE_GATE.md)
- [ADR-0103](../decisions/ADR-0103-oidc-multi-provider-login.md)
