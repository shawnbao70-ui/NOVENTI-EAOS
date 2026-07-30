# Legacy Knowledge Extract — Finance Pack

**Source:** `H:\Workspace\EZAM_CRM - 9.0` (read-only)  
**Writable home:** `docs/knowledge/legacy-extract/finance/**`  
**Date:** 2026-07-23  
**Milestone:** PHX-G291

See [INDEX.md](INDEX.md). Upstream: [../sales/](../sales/), [../crm/](../crm/).

Phase-3 additions: [应收与收款勾兑](ar_receipt_reconciliation.md) · [应付付款与清算](ap_payment_clearing.md)

## Scope

本知识包覆盖应收应付、发票、价格与结算规则。Legacy 无字面“结算规则”模块；可确认的对应能力是 Commission Center 的提成/佣金规则与 TC 台账。

关键边界：

- DO Invoice 实际为应收计提，不是税务或商业发票。
- 销售应收存在订单减收款与交付应收台账双轨口径。
- 采购发票会建立 AP，但付款未自动核销 AP。
- 报价毛利率定价与独立成本加成计算器采用不同公式。
- Commission Center 展示规则不参与主计算；主路径采用销售职级费率，结果停留在 `Pending`。
