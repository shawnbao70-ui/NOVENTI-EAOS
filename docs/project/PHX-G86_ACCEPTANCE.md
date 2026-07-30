# PHX-G86 OIDC Provider End-Session Catalog Gate Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**退出门禁：** provider 可选 end_session；无 Alembic；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0105 + Architecture Gate |
| B | providers 第 7 段 + overlay |
| C | catalog `has_end_session` |
| D | 契约 `test_api_gateway_g86_*` |

## 2. 核心不变量

- 缺省回落主 `end_session_endpoint`  
- 不泄露 client_secret  
- 主登录路径不变  

## 3. 自动化证据

- 本地完整回归：`649 passed`（`tests/contracts`）  
- Alembic head：仍为 `0028_tenant_idp_binding_priority_g78`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0105 |
| Constitution Review | 通过；Gateway OIDC 边界 |
| Cross-reference Review | 通过；G84/G85 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0028` |
| Gap Analysis | MFA 注册、Role 目录、Discovery 填 end_session、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- MFA 注册 / WebAuthn UX  
- Role 目录 / 自动写 grant  
- Provider Discovery 自动填 end_session  

## 6. 证据索引

- [PHX-G86 Architecture Gate](PHX-G86_ARCHITECTURE_GATE.md)
- [ADR-0105](../decisions/ADR-0105-oidc-provider-end-session.md)
