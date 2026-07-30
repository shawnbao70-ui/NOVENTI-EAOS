# Legacy Knowledge Extract — Inventory Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** Legacy 业务知识均衡深挖；不继承 Legacy 架构  
**Verified:** 2026-07-23

## Purpose

本包深化库存台账、盘点差异、调拨/移库及安全库存到采购补货的交界。核心区分：

- `inventory.stock_qty` 现存量、`products.stock_qty` 镜像与 `inventory_ledger` 变动事实；
- PO 收货、DO 出库、样品入库、人工调整的实际过账时点；
- “Cycle Count”交易标签与完整盘点单流程；
- “Transfer In/Out”单边调整标签与真正双边调拨；
- 低库存提示、Draft PO 建议与采购批准/收货。

缺证据一律标注 `UNKNOWN + 已查路径`。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题、证据强度、边界索引 |
| [stock_ledger.md](stock_ledger.md) | 库存台账、双写与过账时点 |
| [stocktake.md](stocktake.md) | 盘点、差异与盈亏调整 |
| [transfer.md](transfer.md) | 调拨、移库与单边 Move 限制 |
| [safety_stock.md](safety_stock.md) | 安全库存、低库存与补货建议 |

## Cross-package boundary

- 库存运行概览：[`../ops/inventory.md`](../ops/inventory.md)
- 履约、仓位与出库：[`../fulfillment-deepen/README.md`](../fulfillment-deepen/README.md)
- 采购深化边界：[`../procurement-deepen/README.md`](../procurement-deepen/README.md)

本包只做证据深化，不回写或复制上述正文。
