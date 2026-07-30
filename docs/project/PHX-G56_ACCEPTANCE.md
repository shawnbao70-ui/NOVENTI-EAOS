# PHX-G56 Multi-IdP Write Registry Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**退出门禁：** 平台面注册表可写；校验合并 env 优先；Alembic `0025`；包版本仍 `0.2.0`  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0075 + Architecture Gate |
| B | 进程内注册表 + `/v1/platform/idp/issuers` |
| C | JWT 校验合并 + status `registry` 段 |
| D | Alembic `0025_idp_issuer_bindings_g56` + 契约 |

## 2. 核心不变量

- 平台面才可写；status 端点仍只读  
- 同 issuer：env 胜出  
- 不存 HS256 secret；响应不泄露完整 JWKS（`has_jwks_json`）  
- SQL 表契约就绪；Gateway 默认进程内  

## 3. 自动化证据

- 本地完整回归：`500 passed`（`tests/contracts`）  
- Alembic head：`0025_idp_issuer_bindings_g56`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0075 |
| Constitution Review | 通过；Gateway 平台面 |
| Cross-reference Review | 通过；G45/G55 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0` |
| Gap Analysis | SQL 适配器接线、Discovery 写回、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Gateway SQL 仓储接线  
- Discovery 写回 env / 联邦策略 UI  
- Service Mesh / KEDA / 多区域  

## 6. 证据索引

- [PHX-G56 Architecture Gate](PHX-G56_ARCHITECTURE_GATE.md)
- [ADR-0075](../decisions/ADR-0075-multi-idp-write-registry.md)
