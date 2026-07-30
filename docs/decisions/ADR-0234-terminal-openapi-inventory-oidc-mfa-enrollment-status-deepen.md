# ADR-0234 — Terminal OpenAPI Inventory OIDC MFA Enrollment Status Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G215  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U088**；PO cue「充分授权…自主开发…加快」

## 背景

G213 已展示 host-acquire details；G214 闭合 OIDC MFA enrollment details（`mfa_enrollment_url`）。
Admin 仍需一瞥看到 OIDC MFA enrollment details honest 标记。

## 决策

1. 加深 `loadOpenapiInventoryProductPosture({ quiet })`：当 t0188 含
   `oidc_mfa_enrollment` 时追加 `OIDC MFA enrollment details honest (G214/G215)`。  
2. Admin CTA **OpenAPI inventory status (G215)**。  
3. Inventory **不** bump。  
4. 包 `0.2.1`；Alembic `0029`；`full_openapi_http_complete` 仍 false。

## Explicit Out

- MFA runtime behavior change  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G215_ARCHITECTURE_GATE.md](../project/PHX-G215_ARCHITECTURE_GATE.md)  
