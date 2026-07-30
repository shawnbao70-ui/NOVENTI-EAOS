# ADR-0310 — Legacy Knowledge Extract Finance Pack

**状态：** Accepted  
**日期：** 2026-07-23  
**里程碑：** PHX-G291  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U164**

## 决策

在 PHX-G290 之后继续 Knowledge Driven：接受 `docs/knowledge/legacy-extract/finance/**`（收款 / 双轨应收）。明确 `receipts`→SO `payment_status` 为收款契约；`ar_records` 为 DO 应计台账且与收款无自动勾兑。不实现 Finance 产品模块；包 `0.2.1`；Alembic `0029`。
