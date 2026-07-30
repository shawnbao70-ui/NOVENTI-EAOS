# PHX-G40 OIDC Authorization Code Login Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**退出门禁：** PKCE login；callback 签发 EAOS JWT；未配置 503

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0058 + Architecture Gate |
| B | `/v1/auth/oidc/status|login|callback` |
| C | PKCE S256 + injectable token exchange |
| D | Terminal Bearer 应用（fragment / sessionStorage） |
| E | 契约测试 + 七步自审 |

## 2. 核心不变量

- Kernel 不解析 IdP 协议  
- Body 仍不可提升  
- 未配置 OIDC → 503  
- 伪造/过期 state 拒绝  

## 3. 自动化证据

- 本地完整回归：`424 passed`（`tests/contracts`）  
- 无 schema 变更；Alembic head 仍为 `0023`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0058 |
| Constitution Review | 通过；Gateway 认证边界 |
| Cross-reference Review | 通过；G37/G38 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | Refresh/logout、多 IdP Discovery 产品化延后 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Refresh token / RP logout  
- 完整 OIDC Discovery 与多 IdP  
- Extension iframe runtime / SQL  

## 6. 证据索引

- [PHX-G40 Architecture Gate](PHX-G40_ARCHITECTURE_GATE.md)
- [ADR-0058](../decisions/ADR-0058-oidc-authorization-code-login.md)
