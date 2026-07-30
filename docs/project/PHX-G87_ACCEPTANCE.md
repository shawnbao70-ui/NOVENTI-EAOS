# PHX-G87 OIDC Authorize ACR/Prompt Step-Up Gate Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**退出门禁：** 可选 authorize `acr_values`/`prompt`；无 Alembic；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0106 + Architecture Gate |
| B | `oidc_authorize_stepup` + login 接线 |
| C | oidc status 字段 |
| D | 契约 `test_api_gateway_g87_*` |

## 2. 核心不变量

- 空配置 = 关闭  
- 不实现 MFA 注册 UI  
- 与 G80 token amr/acr 互补  

## 3. 自动化证据

- 本地完整回归：`653 passed`（`tests/contracts`）  
- Alembic head：仍为 `0028_tenant_idp_binding_priority_g78`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0106 |
| Constitution Review | 通过；Gateway OIDC 边界 |
| Cross-reference Review | 通过；G80 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0028` |
| Gap Analysis | MFA 注册 UX、Role 目录、query 覆盖、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- MFA 注册 / WebAuthn UX  
- Role 目录 / 自动写 grant  
- 登录 query 覆盖 acr_values/prompt  

## 6. 证据索引

- [PHX-G87 Architecture Gate](PHX-G87_ARCHITECTURE_GATE.md)
- [ADR-0106](../decisions/ADR-0106-oidc-authorize-stepup.md)
