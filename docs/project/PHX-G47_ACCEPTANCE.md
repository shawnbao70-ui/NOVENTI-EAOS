# PHX-G47 OIDC IdP Discovery Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**退出门禁：** Discovery 填充端点；issuer 不匹配拒绝；G40 默认路径仍绿；无 schema 变更  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0066 + Architecture Gate |
| B | `EAOS_OIDC_DISCOVERY` / `EAOS_OIDC_DISCOVERY_URL` |
| C | issuer 匹配 + HTTPS + 进程内缓存；status 暴露 discovery |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- Discovery 默认关闭；G40 启发式路径不变  
- 显式 authorize/token env 优先于 Discovery  
- Discovery `issuer` 必须匹配 `EAOS_OIDC_ISSUER`  
- 支付清算不在本切片  

## 3. 自动化证据

- 本地完整回归：`453 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0066 |
| Constitution Review | 通过；Gateway 认证边界 |
| Cross-reference Review | 通过；G40/G46 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | 多 IdP UI、支付清算另批；Discovery→JWKS 见 G48 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 多 IdP 联邦管理 UI  
- Refresh / RP-Logout（Discovery→JWKS Foundation 见 PHX-G48）  

## 6. 证据索引

- [PHX-G47 Architecture Gate](PHX-G47_ARCHITECTURE_GATE.md)
- [ADR-0066](../decisions/ADR-0066-oidc-discovery.md)
