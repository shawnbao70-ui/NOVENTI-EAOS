# Partial Fulfillment Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| 一 SO 多 DO | [multi_do_from_so.md](multi_do_from_so.md) | 强 | 允许重复创建，无已有 DO gate |
| 行复制 | [multi_do_from_so.md](multi_do_from_so.md) | 强 | 每张 DO 全量复制全部 SO 行 |
| 已发/剩余 | [qty_remaining_rules.md](qty_remaining_rules.md) | 强缺口 | 无累计字段/查询/控制 |
| 超发 | [qty_remaining_rules.md](qty_remaining_rules.md) | 强风险 | 幂等只在单 DO 内，不跨 SO 聚合 |
| 分仓/分批 | [allocation_split.md](allocation_split.md) | 强缺口 | DO 不选仓、批次或本批 qty |
| 状态聚合 | [status_on_partial.md](status_on_partial.md) | 强风险 | 任一 DO Complete/Reopen 覆盖 SO |

## Reading order

1. [multi_do_from_so.md](multi_do_from_so.md)
2. [qty_remaining_rules.md](qty_remaining_rules.md)
3. [allocation_split.md](allocation_split.md)
4. [status_on_partial.md](status_on_partial.md)

## Shared vocabulary

- **order qty**：`sales_order_items.qty`。
- **DO qty**：创建时复制到 `delivery_order_items.qty` 的数量。
- **shipped qty**：可从 `DO Ship` ledger 推导，但系统不按 SO 行累计。
- **remaining qty**：order qty - cumulative shipped qty；Legacy 未建模。
- **partial fulfillment**：受控地选择本批行/数量并保留余量；Legacy 当前只是可重复创建全量 DO。
