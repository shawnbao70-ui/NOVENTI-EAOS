# Legacy Knowledge Extract — Partial Fulfillment Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Verified:** 2026-07-23

## Purpose

本包深化 SO→多 DO 的真实边界：

- 数据结构和页面允许一 SO 多 DO，但每次创建都复制全部 SO 行；
- 没有 delivered/remaining/backorder 累计，因此跨 DO 可超发；
- inventory 只有产品级 location，DO 行不选仓、不分批、不拆行；
- 任一 DO Complete/Reopen 都直接覆盖 SO 状态，无法表达部分履约。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题与风险索引 |
| [multi_do_from_so.md](multi_do_from_so.md) | 一 SO 多 DO 与全量复制 |
| [qty_remaining_rules.md](qty_remaining_rules.md) | 已发/未发累计与超发控制 |
| [allocation_split.md](allocation_split.md) | 分仓、分批、行级拆分证据 |
| [status_on_partial.md](status_on_partial.md) | 多 DO 下 SO/DO 状态漂移 |

## Authority boundary

- Partial delivery 权威：[`../fulfillment-deepen/partial_delivery.md`](../fulfillment-deepen/partial_delivery.md)
- SO→DO 权威：[`../order-chain/so_to_do.md`](../order-chain/so_to_do.md)
- Ship/Complete 权威：[`../ship-complete-deepen/README.md`](../ship-complete-deepen/README.md)

本包只补充多 DO、数量守恒和状态聚合断点，不改邻包正文。
