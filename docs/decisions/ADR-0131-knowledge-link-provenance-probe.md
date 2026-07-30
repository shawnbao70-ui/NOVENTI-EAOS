# ADR-0131 — Knowledge Link / Provenance Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G112  
**归属：** Smart Terminal / Knowledge

## 背景

G110–G111 已覆盖 Knowledge 状态、entity 与 archive/share/search。运维仍缺 Terminal 内对 link create 与 provenance get 的薄调用面。

## 决策

1. Terminal Admin 增加 Create knowledge link、Get knowledge provenance。  
2. 仅调用既有 `POST /v1/knowledge/links` 与 `GET /v1/knowledge/provenance/{kind}/{id}`。  
3. path/body id 经独立输入；禁止上下文提升。  
4. 包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / WebAuthn 产品页  
- Twin / Brain Terminal 薄探针（另域）  

## 关联

- [ADR-0130-knowledge-archive-share-search-probe.md](ADR-0130-knowledge-archive-share-search-probe.md)
- [../project/PHX-G112_ARCHITECTURE_GATE.md](../project/PHX-G112_ARCHITECTURE_GATE.md)
