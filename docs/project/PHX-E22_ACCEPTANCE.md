# PHX-E22 Event Webhook HMAC Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted  
**归属：** Event Bus  
**退出门禁：** 可选 HMAC；兼容未签名；Alembic 0023

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0056 + Architecture Gate |
| B | `sign_webhook_v1` / `verify_webhook_signature` |
| C | 订阅 `signing_secret` + 投递签名头 |
| D | Alembic `0023` + Gateway/OpenAPI + 契约 |

## 2. 核心不变量

- 投递所有权仍归 Event Bus  
- 无 secret → E21 未签名行为  
- 审计仅记 `hmac=true/false`，不记 secret  
- SSRF 门禁不变  

## 3. 自动化证据

- 本地完整回归：`418 passed`（`tests/contracts`）  
- Alembic head：`0023_event_webhook_hmac_e22`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0056 |
| Constitution Review | 通过 |
| Cross-reference Review | 通过；E21 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；Manifest head 同步 |
| Gap Analysis | 密钥轮换/加密存储/mTLS 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- 密钥轮换编排；密钥加密存储  
- mTLS webhook  
- OIDC 登录页；Terminal Extension Host  

## 6. 证据索引

- [PHX-E22 Architecture Gate](PHX-E22_ARCHITECTURE_GATE.md)
- [ADR-0056](../decisions/ADR-0056-event-webhook-hmac.md)
- [ADR-0051](../decisions/ADR-0051-event-webhook-transport.md)
