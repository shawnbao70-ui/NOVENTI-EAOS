# PHX-G48 OIDC Discovery → JWKS Wire Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**退出门禁：** Discovery `jwks_uri` 可注入 JWT allowlist；显式 JWKS 优先；G40 HS256 仍可用；无 schema 变更  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0067 + Architecture Gate |
| B | `EAOS_OIDC_JWKS_WIRE` + `maybe_wire_discovery_jwks` |
| C | Bearer 路径接线；status 暴露 `jwks_wire` |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- Wire 默认关闭；需 Discovery  
- 显式 `EAOS_JWT_ISSUERS_JSON` / `EAOS_JWT_JWKS_*` 优先  
- OIDC JWKS + 可选 EAOS HS256 issuer 双信任  
- 支付清算不在本切片  

## 3. 自动化证据

- 本地完整回归：`461 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0067 |
| Constitution Review | 通过；Gateway 认证边界 |
| Cross-reference Review | 通过；G40/G45/G47 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | 多 IdP UI、写回 env、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 多 IdP 联邦管理 UI  
- Discovery 结果写回环境变量  
- Refresh / RP-Logout  

## 6. 证据索引

- [PHX-G48 Architecture Gate](PHX-G48_ARCHITECTURE_GATE.md)
- [ADR-0067](../decisions/ADR-0067-oidc-discovery-jwks-wire.md)
