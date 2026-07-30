# ADR-0133 — Twin Authorize Fail-Closed Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G114  
**归属：** Smart Terminal / Twin

## 背景

G113 已覆盖 Twin 状态与 snapshot upsert/get。运维仍需在 Terminal 内显式验证 authorize 恒 fail-closed，而不打开执行路径。

## 决策

1. Terminal Admin 增加 Authorize from twin（expect 403）。  
2. 仅调用既有 `POST /v1/twin/snapshots/{id}/authorize`；期望 HTTP 403 / `TWIN_EXECUTION_FORBIDDEN`。  
3. UI 展示 fail-closed 观测结果；禁止上下文提升；不放宽执行权。  
4. Twin Terminal 运维面齐；Brain Terminal 另批；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Brain insights / execute Terminal 薄探针（status/insight 见 G115；execute 另批）  
- Marketplace 支付清算 / 外部仲裁  
- 自动写 grant / WebAuthn 产品页  
- 打开 Twin authorize 执行权  

## 关联

- [ADR-0132-twin-status-snapshot-probe.md](ADR-0132-twin-status-snapshot-probe.md)
- [../project/PHX-G114_ARCHITECTURE_GATE.md](../project/PHX-G114_ARCHITECTURE_GATE.md)
