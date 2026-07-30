# ADR-0130 — Knowledge Archive / Share / Search Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G111  
**归属：** Smart Terminal / Knowledge

## 背景

G110 已覆盖 Knowledge 状态与 entity upsert/get/list。运维仍缺 Terminal 内对 archive / share / search 的薄调用面；link / provenance 另批。

## 决策

1. Terminal Admin 增加 Archive / Share entity、Search knowledge。  
2. 仅调用既有 `.../archive`、`.../share`、`GET /search`。  
3. path id 与 share_with_subject_id 经独立输入；禁止 body 上下文提升。  
4. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Terminal link create / provenance get  
- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / WebAuthn 产品页  

## 关联

- [ADR-0129-knowledge-status-entity-probe.md](ADR-0129-knowledge-status-entity-probe.md)
- [../project/PHX-G111_ARCHITECTURE_GATE.md](../project/PHX-G111_ARCHITECTURE_GATE.md)
