# PHX-G60 OIDC Discovery → Registry Writeback Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**退出门禁：** opt-in Discovery upsert 注册表；不写 env；env/wire 优先；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0079 + Architecture Gate |
| B | `EAOS_OIDC_DISCOVERY_REGISTRY_WRITE` + upsert |
| C | status + `POST /v1/platform/idp/discovery/sync` |
| D | 契约 `test_api_gateway_g60_*` |

## 2. 核心不变量

- 默认关闭；需 Discovery  
- 写注册表，不写 env  
- 同 issuer：env / JWKS wire 胜出  
- 无新 Alembic  

## 3. 自动化证据

- 本地完整回归：`520 passed`（`tests/contracts`）  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0079 |
| Constitution Review | 通过；Gateway 薄适配 |
| Cross-reference Review | 通过；G48/G56/G57 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0` |
| Gap Analysis | 联邦 UI、支付清算、多区域另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Discovery 写回 env  
- 联邦策略 UI / Refresh / RP-Logout  
- 多区域 / 网格 CRD  

## 6. 证据索引

- [PHX-G60 Architecture Gate](PHX-G60_ARCHITECTURE_GATE.md)
- [ADR-0079](../decisions/ADR-0079-oidc-discovery-registry-write.md)
