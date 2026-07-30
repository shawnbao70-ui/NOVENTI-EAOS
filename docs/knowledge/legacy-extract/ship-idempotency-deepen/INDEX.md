# Ship Idempotency Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| 判重键 | [ship_duplicate_guard.md](ship_duplicate_guard.md) | 强 | `trans_type + remark` 应用层查询 |
| DB unique/lock | [ship_duplicate_guard.md](ship_duplicate_guard.md) | 强缺口 | DDL 无唯一键，更新无锁/版本 |
| 三写顺序 | [ship_posting_conservation.md](ship_posting_conservation.md) | 强 | inventory→product mirror→ledger，逐行执行 |
| 守恒 | [ship_posting_conservation.md](ship_posting_conservation.md) | 条件性 | 正常单行守恒；并发/中途失败无证明 |
| Reopen 重 Ship | [reopen_reship_trap.md](reopen_reship_trap.md) | 强 | 状态已开放，但旧流水持续判重 |
| 幽灵流水 | [reopen_reship_trap.md](reopen_reship_trap.md) | 强风险 | 流水锚定 do_no，不表达 shipment attempt |
| Carrier/tracking | [carrier_pod_gap.md](carrier_pod_gap.md) | 强缺口 | 生产 DO 不持久化 |
| POD | [carrier_pod_gap.md](carrier_pod_gap.md) | 强缺口 | Complete 被当确认，但无签收证据 |

## Reading order

1. [ship_duplicate_guard.md](ship_duplicate_guard.md)
2. [ship_posting_conservation.md](ship_posting_conservation.md)
3. [reopen_reship_trap.md](reopen_reship_trap.md)
4. [carrier_pod_gap.md](carrier_pod_gap.md)

## Shared vocabulary

- **应用层判重键**：`trans_type='DO Ship' AND remark='DO-' + do_no`。
- **三写**：inventory 绝对余额、products 镜像 delta、ledger 负数流水。
- **守恒**：库存两份余额同量下降，流水 qty 等于负下降量且 balance 对齐 inventory。
- **幽灵流水**：业务状态已回退，但旧流水仍被当作当前发货事实/永久判重锚。
- **POD**：Proof of Delivery；签收人、时间、签名/照片等交付证据。
