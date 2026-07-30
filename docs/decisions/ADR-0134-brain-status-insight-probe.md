# ADR-0134 — Brain Status / Insight Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G115  
**归属：** Smart Terminal / Brain

## 背景

G28 已交付 Brain HTTP（insight publish/get；execute fail-closed）。运维仍缺 Terminal 内对 Brain 状态与 insight 的薄调用面。

## 决策

1. 新增只读 `GET /v1/brain/status`（`writable=false`；声明 `execute_execution=fail_closed`、`advisory_required=true` 与支持面）。  
2. Terminal Admin 增加 Brain status、Publish brain insight、Get brain insight。  
3. 仅调用既有 `POST /v1/brain/insights` 与 `GET /v1/brain/insights/{id}`；禁止上下文提升；`advisory` 固定 true。  
4. Execute Terminal 探针另批；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Brain execute Terminal 薄探针（见 G116；仍 fail-closed API）  
- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  
- 打开 Brain execute 执行权  

## 关联

- [ADR-0133-twin-authorize-fail-closed-probe.md](ADR-0133-twin-authorize-fail-closed-probe.md)
- [../project/PHX-G115_ARCHITECTURE_GATE.md](../project/PHX-G115_ARCHITECTURE_GATE.md)
