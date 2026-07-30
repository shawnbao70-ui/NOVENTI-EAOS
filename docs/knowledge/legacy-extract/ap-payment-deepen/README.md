# AP 付款深化包

本包深化 Legacy 的采购发票应付产生、Treasury 付款过账、PO/收货追溯和核销缺口。它不把银行余额扣减解释为 AP 核销，也不把 DDL 空壳或 UI 状态兼容解释为运行能力。

## 边界与交叉引用

- AP/付款权威概览：[`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md)
- 应收应付结构：[`../finance/receivables-payables.md`](../finance/receivables-payables.md)
- 本包仅深化 `ap_records` 生命周期、Treasury 镜像、PO/GR 链和缺失的 reconcile。

## 内容

- [`ap_records_lifecycle.md`](ap_records_lifecycle.md)
- [`ap_payment_posting.md`](ap_payment_posting.md)
- [`ap_po_gr_link.md`](ap_po_gr_link.md)
- [`ap_reconcile_absence.md`](ap_reconcile_absence.md)
- [`INDEX.md`](INDEX.md)

## 核心判定

运行链是 `PO → purchase_invoices + ap_records` 与独立的 `treasury_payment_records → bank balance`；两链不勾兑。`ap_records` 仅创建为 Unpaid，未找到付款后更新、分配、核销、三单匹配或银行对账。

## 只读证据根

`H:\Workspace\EZAM_CRM - 9.0`
