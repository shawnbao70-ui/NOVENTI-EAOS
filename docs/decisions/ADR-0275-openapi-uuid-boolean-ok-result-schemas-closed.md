# ADR-0275 — OpenAPI UuidResult / BooleanResult / OkResponse Closed

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G256  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U129**

## 背景

跨域 `UuidResult` / `BooleanResult` / `OkResponse` live 键已由 G170 统一，
但多数契约仍省略 `additionalProperties`（default open）。identity 已关闭。

## 决策

1. 对已命名 props 的 UuidResult/BooleanResult/OkResponse 设
   `additionalProperties: false`（保留可选 `audit_id` / `ok`）。  
2. 触及契约各 bump patch；ops **1.0.53**；inventory PHX-G256。  
3. 不 invent free-form；不打开 HARD HOLD。
