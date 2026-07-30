# PHX-G45 JWT Multi-Issuer JWKS Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**退出门禁：** 多发行方 allowlist；未知 iss fail-closed；kid miss 刷新；无 schema 变更  
**人工确认：** Marketplace 支付清算 / 外部仲裁另批

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0064 + Architecture Gate |
| B | `JwtIssuerBinding` + `EAOS_JWT_ISSUERS_JSON` |
| C | RS256 按 iss 选 JWKS；kid miss URL 刷新 |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 多发行方模式下未知/缺失 `iss` → 401  
- 单 issuer 旧 env 兼容  
- Body 仍不可提升  
- 支付清算不在本切片  

## 3. 自动化证据

- 本地完整回归：`442 passed`（`tests/contracts`）  
- Alembic head 仍为 `0024`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0064 |
| Constitution Review | 通过；Gateway 认证边界 |
| Cross-reference Review | 通过；G37/G38 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | 吊销列表、IdP UI、支付清算另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- IdP 联邦管理 UI / Discovery 产品化  
- CRL / denylist 产品化  
- ES256 / EdDSA  

## 6. 证据索引

- [PHX-G45 Architecture Gate](PHX-G45_ARCHITECTURE_GATE.md)
- [ADR-0064](../decisions/ADR-0064-jwt-multi-issuer-jwks.md)
