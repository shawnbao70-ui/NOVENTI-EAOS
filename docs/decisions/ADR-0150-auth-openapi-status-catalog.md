# ADR-0150 — Auth OpenAPI Status Catalog

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G131  
**归属：** API Contracts / Auth boundary

## 背景

G130 已将域 Foundation `GET */status` 纳入既有 OpenAPI。Auth 三件套（`/auth/oidc|idp|jwt/status`）仍无契约文件，且 Release Manifest 清单为 11 份。

## 决策

1. 新增 `docs/api/auth.openapi.yaml`，仅收录三条脱敏 status GET。  
2. 响应信封 `AuthStatusEnvelope`（`data` 允许附加属性；禁止暗示 secret/jti 列表）。  
3. 路径级 `security: []`（与运行时无强制 Bearer 一致）；CorrelationId 可选。  
4. Manifest / SDK inventory → 12 份；不收录 login/callback/refresh/logout（另批）。  
5. 无运行时变更；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- OIDC login / callback / refresh / logout / MFA OpenAPI  
- WebAuthn 注册产品页  
- Marketplace 支付清算 / 外部仲裁  
- Role→grant 自动写入  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0149-openapi-foundation-status-catalog.md](ADR-0149-openapi-foundation-status-catalog.md)
- [../project/PHX-G131_ARCHITECTURE_GATE.md](../project/PHX-G131_ARCHITECTURE_GATE.md)
