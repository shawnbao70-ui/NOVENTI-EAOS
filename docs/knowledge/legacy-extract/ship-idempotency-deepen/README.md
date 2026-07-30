# Legacy Knowledge Extract — Ship Idempotency Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Mode:** DO Ship 幂等、三写守恒、Reopen 重发与承运/POD 断点深化  
**Verified:** 2026-07-23

## Purpose

本包聚焦 Ship 的四个高风险边界：

- 幂等依赖 `DO Ship + DO-{do_no}` 的应用层先查后写，而非数据库唯一键或锁；
- `inventory`、`products.stock_qty`、`inventory_ledger` 逐行三写，成功时同一末尾 commit，但没有显式事务/rollback 边界；
- Complete→Reopen 只回退状态，保留原流水和库存结果，导致再次 Ship 被永久判重；
- carrier、tracking、POD 未接入生产 DO 状态机，Complete 只是人工业务确认。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题与风险索引 |
| [ship_duplicate_guard.md](ship_duplicate_guard.md) | 应用层判重键、DB unique/lock 缺口 |
| [ship_posting_conservation.md](ship_posting_conservation.md) | 库存镜像与台账三写守恒 |
| [reopen_reship_trap.md](reopen_reship_trap.md) | Reopen 后重 Ship/幽灵流水陷阱 |
| [carrier_pod_gap.md](carrier_pod_gap.md) | 承运、跟踪、POD 与状态脱节 |

## Authority boundary

- Ship 权威：[`../ship-complete-deepen/do_ship.md`](../ship-complete-deepen/do_ship.md)
- Reopen 权威：[`../ship-complete-deepen/do_reopen.md`](../ship-complete-deepen/do_reopen.md)
- Delivery 跟踪权威：[`../delivery-deepen/carrier_tracking.md`](../delivery-deepen/carrier_tracking.md)
- Sample POD 权威：[`../sample/pod.md`](../sample/pod.md)

本包仅深化幂等、守恒和跨状态断点，不改写邻包权威正文。
