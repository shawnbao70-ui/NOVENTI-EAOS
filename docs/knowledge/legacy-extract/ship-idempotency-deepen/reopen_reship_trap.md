# Complete → Reopen 后 Re-Ship 陷阱与幽灵流水

**Evidence strength:** Strong  
**结论：** Complete 将 Shipped DO/SO 推进 Delivered；Reopen 只把 DO→Pending、SO→Open，不恢复库存，也不删除/冲销原 `DO Ship` ledger。再次 Ship 虽通过 open 状态门，却被原 `DO Ship + DO-{do_no}` 判重返回 `already_shipped`。因此 Reopen 是状态回退，不是可重发复位；原流水在状态视图中成为“幽灵锚”，既证明库存已出，又阻止同 DO 第二次发运。

## 状态/事实链

1. 首次 Ship：库存和产品镜像扣减、ledger 写入、DO→已出库。
2. Complete：只把 DO→Delivered、SO→Delivered。
3. Reopen：只把 DO→Pending、SO→Open。
4. 原库存扣减、product 镜像和 ledger 全部保留。
5. 再次 Ship：状态为 open，通过第一门。
6. ledger count 仍 >0，第二门返回 `already_shipped`。
7. DO 保持 Pending，SO 保持 Open，但系统没有合法 Re-Ship 动作。

## 业务规则

| ID | 规则 |
|---|---|
| RRT-R01 | Complete 只允许 Shipped stage。 |
| RRT-R02 | Complete 将 DO 写 Delivered。 |
| RRT-R03 | Complete 将关联 SO 写 Delivered。 |
| RRT-R04 | Reopen 只允许 Complete stage。 |
| RRT-R05 | Reopen 将 DO 写 canonical Pending。 |
| RRT-R06 | Reopen 将关联 SO写 Open。 |
| RRT-R07 | Reopen 不恢复 inventory.stock_qty。 |
| RRT-R08 | Reopen 不恢复 products.stock_qty。 |
| RRT-R09 | Reopen 不删除原 ledger。 |
| RRT-R10 | Reopen 不新增 reversal/return ledger。 |
| RRT-R11 | Reopen 不生成新的 shipment attempt/idempotency key。 |
| RRT-R12 | 再 Ship 的状态门把 Pending 识别为 open。 |
| RRT-R13 | 再 Ship 的 ledger 门因旧流水返回 already_shipped。 |
| RRT-R14 | Inventory Adjust 可人工回补库存，但不清除 Ship 判重锚。 |
| RRT-R15 | 即使人工删除 ledger 以绕过判重，也没有正式政策保证库存不被二次扣减。 |
| RRT-R16 | Reopen 页面说明 status-only / stock not restored。 |
| RRT-R17 | Reopen 是 GET 写动作 + 浏览器 confirm，不是 Type A reversal。 |
| RRT-R18 | AR、receipt、invoice/POD 不随 Reopen 撤销。 |
| RRT-R19 | 多 DO 对同一 SO 时，单个 DO Reopen 仍可把 SO 直接写 Open。 |

## “幽灵流水”定义

原 ledger 不是会计意义上的错误流水：它准确记录首次 Ship 已扣库存。但 Reopen 后业务状态声称“Pending/Open”，没有“已发货但重新打开”的中间态；同一旧流水继续被当作当前 DO 的永久幂等锁。于是：

- 状态层：像是待发货；
- 库存层：货已经离库；
- ledger 层：已有发货事实；
- 操作层：再次发货被拒绝；
- 承运/POD 层：没有 shipment attempt 可解释究竟要重送、纠错还是退货。

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| RRT-V01 | Complete 前必须 Shipped | Hard |
| RRT-V02 | Reopen 前必须 Complete | Hard |
| RRT-V03 | Delivery Orders edit 权限 | Hard |
| RRT-V04 | 再 Ship 状态必须 open | 通过 |
| RRT-V05 | 再 Ship 不得有旧 ledger | Hard，导致陷阱 |
| RRT-V06 | Reopen 前必须选择“状态纠错/退货/重送”原因 | Missing |
| RRT-V07 | Reopen 必须决定库存 reversal | Missing |
| RRT-V08 | Reopen 必须生成新 shipment attempt | Missing |
| RRT-V09 | Re-Ship 必须使用 attempt-level idempotency key | Missing |
| RRT-V10 | Inventory Adjust 必须引用 DO 与 reversal | Missing |
| RRT-V11 | 已有 AR/收款/POD 时必须阻断或冲销 | Missing |
| RRT-V12 | 多 DO/SO 状态一致性 | Missing |
| RRT-V13 | Reopen 必须 POST/CSRF/Human Confirm | Missing |
| RRT-V14 | Reopen reason/operator/time audit | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `已出库` | 已执行三写的 DO 状态 |
| `Delivered` | Complete 后 DO/SO 业务完成 |
| `Pending` | Reopen 后状态，不代表库存已恢复 |
| `Open` | Reopen 后 SO 状态，不代表可再次 Ship |
| original inventory balance | 首次 Ship 后余额，Reopen 不改 |
| original product mirror | 首次 Ship 后镜像，Reopen 不改 |
| original `DO Ship` ledger | 首次出库事实兼永久判重锚 |
| `DO-{do_no}` | Reopen 后仍相同的 remark |
| `already_shipped` | Re-Ship 返回结果 |
| Inventory Adjust | 独立人工库存变动，不是 DO reversal |
| reversal ledger | 当前 Reopen 未生成的数据 |
| shipment attempt | 当前未建模的重送轮次 |
| reopen reason | 当前未采集的业务原因 |
| `ar_records.source_no` | 可能引用 DO，Reopen 不处理 |
| GET reopen route | 直接状态回退入口 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| RRT-E01 | Complete 仅 Shipped 且更新 DO/SO | 强 | `apps/inventory/services.py::_legacy_complete_do` |
| RRT-E02 | Reopen 仅 Complete 且 DO→Pending/SO→Open | 强 | `apps/inventory/services.py::_legacy_reopen_do` |
| RRT-E03 | Reopen 不调用任何库存 helper | 强负向 | `apps/inventory/services.py` |
| RRT-E04 | Reopen 不写/delete inventory_ledger | 强负向 | `apps/inventory/services.py` |
| RRT-E05 | Ship 状态门后再查旧 ledger | 强 | `apps/inventory/services.py::ship_delivery_order` |
| RRT-E06 | ledger 判重只认原 do_no remark | 强 | `apps/inventory/repository.py::count_inventory_ledger_for_do` |
| RRT-E07 | Reopen UI 明示 stock not restored | 强 | `templates/delivery_order_detail.html` |
| RRT-E08 | Inventory Adjust 是独立通用动作 | 强 | `apps/inventory/services.py::adjust_inventory` |
| RRT-E09 | Reopen 权威页确认 status-only | 强交叉 | `../ship-complete-deepen/do_reopen.md` |
| RRT-E10 | A-003 报告明确不自动恢复 | 中等佐证 | `docs/reports/Business_Strong_A003_Delivery_Report.md` |

## 失败/绕行矩阵

| 尝试 | 结果 | 风险 |
|---|---|---|
| Reopen 后直接 Ship | already_shipped | Pending 永久卡住 |
| 只做正数 Inventory Adjust | 库存回补，旧 ledger 仍在 | 仍不能 Re-Ship |
| 手删旧 ledger 后 Ship | 可能再次扣减 | 审计破坏/双扣风险 |
| 新建另一个 DO | 可能可 Ship | 原 DO/SO/AR 关系不清 |
| 只把状态改回 Shipped | 无新过账 | 状态冒充物流动作 |

## UNKNOWN + 已查路径

1. **Reopen 的真实业务目的（纠错/退货/重送）UNKNOWN。** 已查：Inventory service/template、business_modules、reports。
2. **正式 reset/reversal 命令是否存在于私有插件 UNKNOWN。** 已查：apps/inventory、sales、finance、scripts。
3. **重送应复用 DO 还是创建 shipment attempt/新 DO UNKNOWN。** 已查：Delivery/Shipment specs、GFIP、templates。
4. **人工 Inventory Adjust 的标准 remark 是否要求引用 DO UNKNOWN。** 已查：adjust service/template、ledger reports。
5. **已有 AR/收款时 Reopen 应如何处理 UNKNOWN。** 已查：Inventory invoice、Finance AR/receipt、邻包文档。
6. **多 DO 对同一 SO 的正确 SO 回退聚合规则 UNKNOWN。** 已查：Create DO、DO/SO queries、fulfillment docs。
7. **生产数据中 Pending+旧 DO Ship 的卡单规模 UNKNOWN。** 已查：代码/报告；未读生产 DB。
8. **管理员是否会手删 ledger 解除判重 UNKNOWN。** 已查：inventory routes/templates、权限、reports。

## 交叉引用

- Reopen 权威：[`../ship-complete-deepen/do_reopen.md`](../ship-complete-deepen/do_reopen.md)
- Ship 权威：[`../ship-complete-deepen/do_ship.md`](../ship-complete-deepen/do_ship.md)
- 退货/冲销：[`../fulfillment-deepen/returns_reversal.md`](../fulfillment-deepen/returns_reversal.md)
