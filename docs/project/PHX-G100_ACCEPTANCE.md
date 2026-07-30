# PHX-G100 Terminal Event Subscribe/Replay Thin Probe Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Event Bus  
**退出门禁：** Terminal Event subscribe / replay 薄探针；包版本仍 `0.2.0`；Alembic 仍 `0029`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0119 + Architecture Gate |
| B | Terminal Admin Subscribe + Replay event |
| C | 契约 `test_api_gateway_g100_*` |

## 2. 核心不变量

- 仅调用既有 subscriptions / event replay  
- Terminal 不采集 signing_secret  
- 禁止 body 上下文提升；不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`688 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0119 |
| Constitution Review | 通过；Gateway 薄；secret 不下发 |
| Cross-reference Review | 通过；G26/G97–G99 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | 自动写 grant、WebAuthn 产品页、支付清算、Webhook secret 管理台另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  
- Webhook signing_secret 管理台  

## 6. 证据索引

- [PHX-G100 Architecture Gate](PHX-G100_ARCHITECTURE_GATE.md)
- [ADR-0119](../decisions/ADR-0119-terminal-event-subscribe-replay.md)
- [test_api_gateway_g100_terminal_event_subscribe.py](../../tests/contracts/test_api_gateway_g100_terminal_event_subscribe.py)
