# PHX-G61 OIDC Refresh + RP-Logout Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**退出门禁：** opt-in refresh/logout；runtime jti revoke；Terminal 薄按钮；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0080 + Architecture Gate |
| B | `POST /v1/auth/oidc/refresh` + `/logout` |
| C | status 字段 + Terminal 按钮 |
| D | 契约 `test_api_gateway_g61_*` |

## 2. 核心不变量

- 默认关闭；缺 refresh 绑定 fail-closed  
- 不向浏览器回传 IdP refresh_token  
- Logout 本地 revoke；RP-Logout URL 可选  
- 无新 Alembic  

## 3. 自动化证据

- 本地完整回归：`525 passed`（`tests/contracts`）  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0080 |
| Constitution Review | 通过；Gateway/Terminal 薄面 |
| Cross-reference Review | 通过；G40/G46 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0` |
| Gap Analysis | 联邦 UI、SQL refresh 持久化、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 组织级联邦策略 UI  
- Refresh 绑定 SQL 持久化  
- 多区域 / 网格 CRD  

## 6. 证据索引

- [PHX-G61 Architecture Gate](PHX-G61_ARCHITECTURE_GATE.md)
- [ADR-0080](../decisions/ADR-0080-oidc-refresh-rp-logout.md)
