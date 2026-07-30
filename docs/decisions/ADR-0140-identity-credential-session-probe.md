# ADR-0140 — Identity Credential / Session Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G121  
**归属：** Smart Terminal / Identity

## 背景

G120 已覆盖 Identity 状态与 subject register/resolve。运维仍缺 Terminal 内对 credential bind 与 session create/validate 的薄调用面。

## 决策

1. Terminal Admin 增加 Bind identity credential、Create identity session、Validate identity session。  
2. 仅调用既有 `/v1/identity/credentials`、`/sessions`、`/sessions/{id}/validation`。  
3. Session create/validate 以目标 subject 作为 trusted header（可选 `subjectId` 覆盖）；`secret_handle` 仅为 vault ref，不下发真实 secret。  
4. Identity Terminal 运维面齐；Organization Terminal 另批；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Organization Terminal 薄探针  
- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  

## 关联

- [ADR-0139-identity-status-subject-probe.md](ADR-0139-identity-status-subject-probe.md)
- [../project/PHX-G121_ARCHITECTURE_GATE.md](../project/PHX-G121_ARCHITECTURE_GATE.md)
