# Ship / Complete Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| Create DO | [do_ship.md](do_ship.md) | 强 | 复制 SO 全部行，不扣库存、不写出库流水 |
| Ship | [do_ship.md](do_ship.md) | 强 | Open + Human Confirm 后执行库存双写和负数流水 |
| Ship 幂等 | [do_ship.md](do_ship.md) | 强应用层/弱数据库层 | 用 `DO Ship + DO-{do_no}` 查询判重 |
| Complete | [do_complete.md](do_complete.md) | 强 | 仅 Shipped→Delivered，并同步 SO Delivered |
| Complete 入口 | [do_complete.md](do_complete.md) | 强风险 | GET 写操作，仅浏览器 confirm，无 Type A 令牌 |
| Reopen | [do_reopen.md](do_reopen.md) | 强 | Complete→Pending，SO→Open；库存和流水不反转 |
| 重开后重发 | [do_reopen.md](do_reopen.md) | 强负向 | 原 Ship 流水仍在，因此再次 Ship 被判重 |
| DO Invoice | [do_invoice_ar.md](do_invoice_ar.md) | 强 | Type A 人工确认后写未收 `ar_records` |
| 重复/未发运 AR | [do_invoice_ar.md](do_invoice_ar.md) | 强 | 仅告警，不阻断 |
| 税务发票边界 | [do_invoice_ar.md](do_invoice_ar.md) | 强负向 | Post AR 不是税务/NDE 商业发票 |

## Reading order

1. [do_ship.md](do_ship.md)：先定位真实库存过账点。
2. [do_complete.md](do_complete.md)：再区分出库与送达状态。
3. [do_reopen.md](do_reopen.md)：确认状态回退不等于库存/财务冲销。
4. [do_invoice_ar.md](do_invoice_ar.md)：最后理解并行 AR 计提。

## Shared vocabulary

- **Create DO**：建立交付单头/行，不出库。
- **Ship**：库存余额、产品镜像和台账的实际负向过账。
- **Complete / Delivered**：履约状态推进，不再扣库存。
- **Reopen**：状态回退，不是退货或冲销。
- **Type A Invoice / Post AR**：人工确认建立应收，不是正式销售发票。
- **Open stage**：Pending / 待出库 / Pending Outbound。
- **Shipped stage**：已出库 / Shipped。
- **Complete stage**：Delivered / 已完成。
