# ADR-0132 — Twin Status / Snapshot Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G113  
**归属：** Smart Terminal / Twin

## 背景

G28 已交付 Twin HTTP（snapshot upsert/get；authorize fail-closed）。运维仍缺 Terminal 内对 Twin 状态与 snapshot 的薄调用面。

## 决策

1. 新增只读 `GET /v1/twin/status`（`writable=false`；声明 `authorize_execution=fail_closed` 与支持面）。  
2. Terminal Admin 增加 Twin status、Upsert twin snapshot、Get twin snapshot。  
3. 仅调用既有 `POST /v1/twin/snapshots` 与 `GET /v1/twin/snapshots/{id}`；禁止上下文提升。  
4. Authorize 与 Brain Terminal 另批；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Twin authorize Terminal 薄探针（见 G114；仍 fail-closed API）  
- Brain insights / execute Terminal 薄探针  
- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  

## 关联

- [ADR-0131-knowledge-link-provenance-probe.md](ADR-0131-knowledge-link-provenance-probe.md)
- [../project/PHX-G113_ARCHITECTURE_GATE.md](../project/PHX-G113_ARCHITECTURE_GATE.md)
