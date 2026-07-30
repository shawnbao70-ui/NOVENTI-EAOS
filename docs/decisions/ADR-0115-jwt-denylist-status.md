# ADR-0115 — JWT Denylist Status Observability

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G96  
**归属：** Platform API Gateway / Auth

## 背景

G46 denylist 与 G61 runtime jti revoke 已落地；`/v1/auth/idp/status` 仅有 `denylist_enabled` 布尔。运维需要更细的只读摘要（配置来源、条目数、进程内 revoke 计数），且不得下发 jti 列表。

## 决策

1. 新增 `GET /v1/auth/jwt/status`（只读、无需租户上下文）。  
2. 返回脱敏摘要：JWT 基础标志 + `denylist.{enabled,has_json,has_url,url?,cache_seconds,configured_entry_count,load_error,runtime_revoked_count}`。  
3. 不下发 denylist JSON 原文或 jti 明细。  
4. Terminal Admin 增加「JWT status」薄按钮。  
5. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0065-jwt-denylist.md](ADR-0065-jwt-denylist.md)
- [../project/PHX-G96_ARCHITECTURE_GATE.md](../project/PHX-G96_ARCHITECTURE_GATE.md)
