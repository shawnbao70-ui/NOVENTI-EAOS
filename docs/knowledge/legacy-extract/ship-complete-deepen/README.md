# Legacy Knowledge Extract — Ship / Complete Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** 发货出库、完成、重开与应收交界均衡深挖  
**Verified:** 2026-07-23

## Purpose

本包把 Delivery Order 的四个不同业务动作拆开：

- Create DO 复制订单行，但不扣库存；
- Ship 是库存、产品镜像和流水的实际出库过账时点；
- Complete/Delivered 只推进 DO/SO 履约状态；
- Reopen 只回退状态，不恢复库存、撤销流水或冲销 AR；
- Type A “Invoice” 实际建立 `ar_records`，不是税务/商业发票。

缺证据一律标注 `UNKNOWN + 已查路径`。本文包不修改或复制 `delivery/`、`fulfillment-deepen/`、`order-chain/`、`ops/`、`finance/` 正文。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题、证据强度和阅读顺序 |
| [do_ship.md](do_ship.md) | Ship 出库时点、库存扣减及 Create DO 差异 |
| [do_complete.md](do_complete.md) | Complete/Delivered 条件与 GET 直链风险 |
| [do_reopen.md](do_reopen.md) | Reopen 条件、状态副作用与反向过账缺口 |
| [do_invoice_ar.md](do_invoice_ar.md) | DO Type A Invoice 与 `ar_records` 交界 |

## Cross-package boundary

- DO 基线：[`../delivery/delivery_order.md`](../delivery/delivery_order.md)
- 履约深化：[`../fulfillment-deepen/README.md`](../fulfillment-deepen/README.md)
- 订单到 DO：[`../order-chain/so_to_do.md`](../order-chain/so_to_do.md)
- 财务发票/AR：[`../finance/invoices.md`](../finance/invoices.md)

本包只深化动作语义与证据，不回写上述知识包。
