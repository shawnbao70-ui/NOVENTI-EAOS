# ADR-0365 — PO Goods Receipt + Inventory Boundary

**状态：** Accepted（PHX-G333 / AP4）  
**日期：** 2026-07-26  
**里程碑：** PHX-G333  
**授权源：** [Coding Authorization](../project/PURCHASE_GOODS_RECEIPT_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. AP4 增加最小 PO lines（inventory_item_id + qty）；全量收货。  
2. GRN 与库存 `PO_RECEIVE` 同事务；库存按 item_id 余额（不复用 DO ship / SO line）。  
3. 拒客户端 qty override；Defer 部分收货；不自动建 AP Bill。
