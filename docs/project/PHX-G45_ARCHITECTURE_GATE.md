# PHX-G45 JWT Multi-Issuer JWKS Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Identity  
**规范源：** ADR-0064  
**人工批准：** 支付清算另批（用户确认）；本切片仅身份边界  

## 1. 门禁目标

多发行方 JWKS allowlist + 未知 issuer fail-closed + kid 未命中缓存刷新。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Config | `EAOS_JWT_ISSUERS_JSON`；旧单 issuer env 兼容 |
| Fail-closed | 多发行方模式下未知/缺失 `iss` 拒绝 |
| Rotation | URL JWKS kid miss → 刷新一次 |
| Payment | 显式另批 |

## 3. Exit Criteria

1. ADR-0064 Accepted。  
2. 双 issuer 契约绿；未知 iss 401。  
3. G37/G38 回归绿；无 Alembic 变更。
