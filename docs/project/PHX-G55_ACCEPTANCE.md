# PHX-G55 Multi-IdP Status UI Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Smart Terminal  
**退出门禁：** 只读聚合脱敏；Admin 探针；无写 API；无 schema / 版本 bump  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0074 + Architecture Gate |
| B | `GET /v1/auth/idp/status` + `idp_status.py` |
| C | Terminal Admin「IdP / JWT status」探针 |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- `writable: false`；配置源仍为 environment  
- 不泄露 secret / client_secret / 完整 JWKS  
- BOOK23：交互层只读探针  
- 支付清算不在本切片  

## 3. 自动化证据

- 本地完整回归：`496 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0074 |
| Constitution Review | 通过；BOOK23 |
| Cross-reference Review | 通过；G40/G45/G36 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；版本仍 `0.2.0` |
| Gap Analysis | SQL 适配器、联邦策略 UI、支付清算另批；写注册表见 G56 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Discovery 写回 env（写注册表 Foundation 见 PHX-G56）  
- Refresh / RP-Logout / 组织级联邦策略 UI  
- Service Mesh / KEDA / 多区域  

## 6. 证据索引

- [PHX-G55 Architecture Gate](PHX-G55_ARCHITECTURE_GATE.md)
- [ADR-0074](../decisions/ADR-0074-multi-idp-status-ui.md)
