# ADR-0139 — Identity Status / Subject Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G120  
**归属：** Smart Terminal / Identity

## 背景

G20 已交付 Identity HTTP（subjects/credentials/sessions）。运维仍缺 Terminal 内对状态与 subject register/resolve 的薄调用面。

## 决策

1. 新增只读 `GET /v1/identity/status`（`writable=false` 与支持面声明）。  
2. Terminal Admin 增加 Identity status、Register identity subject、Resolve identity subject。  
3. 仅调用既有 `POST /v1/identity/subjects` 与 `GET /v1/identity/subjects/{id}`；禁止上下文提升。  
4. Credential / session Terminal 探针另批；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Identity credential / session Terminal 薄探针  
- Organization Terminal 薄探针  
- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  

## 关联

- [ADR-0138-ai-approval-commit-probe.md](ADR-0138-ai-approval-commit-probe.md)
- [../project/PHX-G120_ARCHITECTURE_GATE.md](../project/PHX-G120_ARCHITECTURE_GATE.md)
