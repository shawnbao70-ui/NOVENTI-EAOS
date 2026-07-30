# PHX-G48 OIDC Discovery → JWKS Wire Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**规范源：** ADR-0067  
**人工确认：** 支付清算另批  

## 1. 门禁目标

可选将 Discovery `jwks_uri` 注入 JWT 校验 allowlist，且不破坏 G40 EAOS HS256。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Opt-in | `EAOS_OIDC_JWKS_WIRE` + Discovery |
| Precedence | 显式 JWT JWKS / issuers 优先 |
| Dual trust | OIDC JWKS + 可选 EAOS HS256 issuer |
| Timing | 仅 Bearer 校验路径解析 |

## 3. Exit Criteria

1. ADR-0067 Accepted。  
2. Wire 后 IdP RS256 Bearer 可校验；显式 JWKS 仍优先；wire off 行为不变。  
3. G40/G45/G47 仍绿；无 Alembic 变更。  

## 4. 验收

见 [PHX-G48_ACCEPTANCE.md](PHX-G48_ACCEPTANCE.md)；契约 `461 passed`。
