# PHX-G147 OIDC Login Product Surface Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Auth / Smart Terminal  
**规范源：** ADR-0166  
**授权：** DAL-G003（DAL-U008）；关闭 T-0189

## 1. 门禁目标

以 **只读产品姿态面 + Terminal 产品面板** 关闭 T-0189「OIDC 登录页延后」：命名 Foundation OIDC Login Product；`authorization_code_enabled` 来自配置；`live_routes` 组合既有 Auth Code CTA；未配置 fail-closed；**不**交付新协议 / WebAuthn ceremony / Role→grant mint；包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Read-only product posture + Terminal panel（thin） |
| Helper | `api/gateway/oidc_login_product.py` → posture dict |
| Wire | `oidc_status()` / `GET /v1/auth/oidc/status` → `oidc_login_product` |
| Protocol | Existing OAuth2 Authorization Code only（G40/G61/G132） |
| Enabled | `authorization_code_enabled` from OIDC config |
| Live routes | status / login / callback / providers / refresh / logout |
| Fail-closed | Unconfigured → 503；`fail_closed_when_unconfigured=true` |
| Terminal | Named 「OIDC Login Product」 panel composing existing CTAs |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | New auth protocol；WebAuthn ceremony；Role→grant mint；支付清算；Brain execute；Twin authorize；新 Alembic |

## 3. Exit Criteria

1. ADR-0166 Accepted。  
2. Gate / Acceptance + helper + OpenAPI + Terminal + DAL-U008 + status sync 齐；T-0189 完成。  
3. `test_api_gateway_g147_oidc_login_product.py` 与相关 G145/auth/DAL 合约绿。  

见 [PHX-G147_ACCEPTANCE.md](PHX-G147_ACCEPTANCE.md)。
