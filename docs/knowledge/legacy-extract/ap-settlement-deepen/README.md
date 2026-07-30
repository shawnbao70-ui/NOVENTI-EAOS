# Legacy Knowledge Extract — AP Settlement Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Verified:** 2026-07-23

## Purpose

本包聚焦采购发票、应付与供应商付款之间未闭合的清算链：

- Invoice 只复制 PO 头金额，不与结构化 GR、收货数量或价差做三单匹配；
- Treasury payment 只绑定 supplier 与 bank account，不分配到 AP/Invoice；
- AP/Invoice 的 paid/balance/status 字段会初始化，但付款后不更新；
- `ap_records` 是 Dashboard 应付口径，payment records 是资金口径，两者未对账，因此没有净供应商余额唯一权威。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题与权威边界索引 |
| [invoice_po_gr_match.md](invoice_po_gr_match.md) | Invoice/PO/GR 三单匹配 |
| [payment_allocation.md](payment_allocation.md) | 付款到 AP/Invoice 的分配缺口 |
| [partial_clearing_writeoff.md](partial_clearing_writeoff.md) | 部分清账、核销与 write-off |
| [supplier_balance_authority.md](supplier_balance_authority.md) | 供应商余额唯一权威判定 |

## Authority boundary

- AP payment deepen：[`../ap-payment-deepen/README.md`](../ap-payment-deepen/README.md)
- Finance：[`../finance/README.md`](../finance/README.md)

本包只深化 settlement 断点，不重写权威正文。
