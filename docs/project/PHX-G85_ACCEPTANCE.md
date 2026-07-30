# PHX-G85 OIDC Per-Provider Refresh Gate Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**退出门禁：** JWT `eaos_oidc_login_provider` 驱动 refresh/logout overlay；无 Alembic；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0104 + Architecture Gate |
| B | callback mint provider claim |
| C | refresh/logout resolve overlay |
| D | 契约 `test_api_gateway_g85_*` |

## 2. 核心不变量

- 无 claim = 主 OIDC（G61）  
- 未知 provider fail-closed  
- 不扩 refresh SQL  

## 3. 自动化证据

- 本地完整回归：`645 passed`（`tests/contracts`）  
- Alembic head：仍为 `0028_tenant_idp_binding_priority_g78`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0104 |
| Constitution Review | 通过；Gateway OIDC 边界 |
| Cross-reference Review | 通过；G61/G84 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0028` |
| Gap Analysis | provider end_session 目录、MFA 注册、Role 目录、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Provider 级独立 end_session 目录字段  
- MFA 注册 / WebAuthn UX  
- Role 目录 / 自动写 grant  

## 6. 证据索引

- [PHX-G85 Architecture Gate](PHX-G85_ARCHITECTURE_GATE.md)
- [ADR-0104](../decisions/ADR-0104-oidc-provider-refresh.md)
