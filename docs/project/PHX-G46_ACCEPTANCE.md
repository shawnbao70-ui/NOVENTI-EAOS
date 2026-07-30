# PHX-G46 JWT Denylist Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**退出门禁：** denylist 命中 → `GATEWAY_JWT_REVOKED`；未配置行为不变；无 schema 变更  
**人工确认：** Marketplace 支付清算另批暂缓

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0065 + Architecture Gate |
| B | `EAOS_JWT_DENYLIST_JSON` / `EAOS_JWT_DENYLIST_URL` |
| C | verify_token 后强制检查 |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 签名与 party 校验通过后才查 denylist  
- 命中 → 401 `GATEWAY_JWT_REVOKED`  
- 无 `jti` 无法命中（不强制全量带 jti）  
- 支付清算不在本切片  

## 3. 自动化证据

- 本地完整回归：`446 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0065 |
| Constitution Review | 通过；Gateway 认证边界 |
| Cross-reference Review | 通过；G37/G45 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | 分布式实时吊销、支付清算另批；IdP Discovery 见 G47 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- Redis / 实时吊销总线  
- 全量 CRL 互操作（IdP Discovery Foundation 见 PHX-G47）  

## 6. 证据索引

- [PHX-G46 Architecture Gate](PHX-G46_ARCHITECTURE_GATE.md)
- [ADR-0065](../decisions/ADR-0065-jwt-denylist.md)
