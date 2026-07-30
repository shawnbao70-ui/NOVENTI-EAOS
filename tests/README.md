# tests/

Test suites for EAOS.

## Purpose

Architecture, unit, integration, security, and platform verification tests.

## Status

PHX-K09 当前结果：本地完整 `215 passed`，专用 PostgreSQL `12 passed`；覆盖 Workflow 审批真相源、Permission Policy/Scope/Delegation、Organization L0–L2 与 Identity L2。

## Suites

- `contracts/`：内存、SQLAlchemy、事务与跨域契约
- `integration/`：受保护的专用 PostgreSQL 迁移及往返验证
