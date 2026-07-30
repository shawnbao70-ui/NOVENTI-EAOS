# ADR-0129 — Knowledge Status / Entity Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G110  
**归属：** Smart Terminal / Knowledge

## 背景

G24 已交付 Knowledge HTTP 面；Package Terminal 运维面（G108–G109）已齐。下一薄切片切入 Knowledge：状态 + entity upsert/get/list；archive/share/link/search/provenance 另批。

## 决策

1. 新增只读 `GET /v1/knowledge/status`（脱敏能力清单；`writable=false`）。  
2. Terminal Admin 增加：Knowledge status、Upsert/Get entity、List entities。  
3. 仅调用既有 `/entities`；禁止 body 上下文提升。  
4. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Terminal archive / share / link / search / provenance  
- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / WebAuthn 产品页  

## 关联

- [../project/PHX-G24_ACCEPTANCE.md](../project/PHX-G24_ACCEPTANCE.md)
- [../project/PHX-G110_ARCHITECTURE_GATE.md](../project/PHX-G110_ARCHITECTURE_GATE.md)
