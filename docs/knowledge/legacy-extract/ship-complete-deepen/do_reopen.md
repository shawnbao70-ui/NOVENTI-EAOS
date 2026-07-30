# Delivery Order Reopen：状态回退与反向业务缺口

**Evidence strength:** Strong for status-only behavior; strong negative for inventory/AR reversal

## Scope 与关键结论

Reopen 只允许 complete stage，成功后把 DO 写回 Pending、关联 SO 写回 Open。它不恢复库存、不更新产品库存镜像、不删除或冲销 `DO Ship` 流水，也不撤销 DO 来源 AR。因为原流水仍存在，同一 DO 直接再次 Ship 会命中 `already_shipped`。因此 Reopen 不是退货、撤销出库或可重发复位。

## 业务规则

| ID | 规则 |
|---|---|
| DOR-R01 | Reopen 要求 Delivery Orders edit 权限。 |
| DOR-R02 | DO 不存在时返回 DO 列表。 |
| DOR-R03 | 只有 complete stage（`Delivered / 已完成`）可 Reopen。 |
| DOR-R04 | 非 complete 调用返回 `reopen_error=not_complete`。 |
| DOR-R05 | 成功后 DO 状态写为 canonical `Pending`。 |
| DOR-R06 | 有关联 SO 时把 SO 状态写为 `Open`。 |
| DOR-R07 | 无关联 SO 时仍可完成 DO 状态回退。 |
| DOR-R08 | Reopen 不增加 `inventory.stock_qty`。 |
| DOR-R09 | Reopen 不增加 `products.stock_qty` 镜像。 |
| DOR-R10 | Reopen 不写反向 inventory ledger，也不删除原 `DO Ship`。 |
| DOR-R11 | 原流水保留使再次 Ship 被同 DO 幂等检查阻断。 |
| DOR-R12 | Reopen 不检查或冲销 `ar_records`。 |
| DOR-R13 | Reopen 不检查 SO receipts、税务发票或商业发票文档。 |
| DOR-R14 | 页面明确提示 status-only；需要库存回补时引导用户另做 Inventory Adjust。 |
| DOR-R15 | Inventory Adjust 可以正数回补，但没有 DO/RMA 强关联，不能等同正式退货。 |
| DOR-R16 | Reopen 是 GET 写动作，只有浏览器 confirm，没有 Type A Human Confirm。 |
| DOR-R17 | DO→Pending 与 SO→Open 不恢复原 `Delivery Created` 状态，状态回退不对称。 |

## 当前 Reopen 流程

1. 用户在 Delivered/已完成 DO 详情点击 Reopen。
2. 浏览器弹出 confirm，随后 GET `/reopen_do/{id}`。
3. 服务检查 edit 权限、DO 存在和 complete stage。
4. DO→Pending；有 SO 时 SO→Open；commit。
5. 库存、流水、AR、收款和文档保持原样。
6. 若再次 Ship，原 `DO Ship + DO-{do_no}` 流水会阻断。

## 副作用矩阵

| 对象 | Reopen 结果 |
|---|---|
| DO status | Delivered/已完成 → Pending |
| SO status | → Open |
| inventory | 不变 |
| products.stock_qty | 不变 |
| inventory_ledger | 原 DO Ship 保留，无反向流水 |
| ar_records | 不变 |
| receipts | 不变 |
| delivery date / POD | 不变/未建模 |
| 可再次 Ship | 否，原流水判重 |

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| DOR-V01 | Delivery Orders edit 权限 | Hard |
| DOR-V02 | DO 必须存在 | Hard |
| DOR-V03 | 当前阶段必须 complete | Hard |
| DOR-V04 | Reopen 应使用 POST/命令 | Missing |
| DOR-V05 | 必须 CSRF/Human Confirm | Missing |
| DOR-V06 | 必须检查是否存在 AR | Missing |
| DOR-V07 | 必须决定是否冲销/恢复库存 | Missing；固定不恢复 |
| DOR-V08 | 必须检查关联 SO 及其他 DO | Missing |
| DOR-V09 | 必须填写重开原因 | Missing |
| DOR-V10 | 必须写操作审计 | Missing |
| DOR-V11 | 重开后再次 Ship 必须有正式 reset/reversal | Missing |
| DOR-V12 | 人工 Adjust 回补必须防重复并引用 DO | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `Delivered` / `已完成` | Reopen 唯一接受的起点 |
| `Pending` | Reopen 后 DO 状态；不表示库存已恢复 |
| `Open` | Reopen 后关联 SO 状态 |
| `delivery_orders.so_id` | 关联 SO 状态更新依据 |
| `inventory.stock_qty` | 已 Ship 后现存量；Reopen 不改 |
| `products.stock_qty` | 库存镜像；Reopen 不改 |
| `inventory_ledger` | 原出库事实保留 |
| `DO Ship` | 阻断再次 Ship 的流水类型 |
| `DO-{do_no}` | 原出库流水关联/幂等 remark |
| `ar_records.source_no` | DO 来源 AR；Reopen 不改 |
| `reopen_error=not_complete` | 非 complete 重开反馈 |
| Inventory Adjust | 可人工回补的通用工具，不是 Reopen 副作用 |
| GET `/reopen_do/{id}` | 直接执行状态回退的入口 |
| RMA / Return Receipt | 未建模的正式退货语义 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| DOR-E01 | complete-only 条件和状态写入 | 强 | `apps/inventory/services.py::_legacy_reopen_do` |
| DOR-E02 | DO→Pending、SO→Open 同一 commit | 强 | `apps/inventory/services.py` |
| DOR-E03 | Reopen 代码不触碰库存/流水 | 强负向 | `apps/inventory/services.py` |
| DOR-E04 | Ship 以原流水判重 | 强 | `ship_delivery_order`、`repository.py::count_inventory_ledger_for_do` |
| DOR-E05 | GET 路由直接执行 Reopen | 强 | `apps/inventory/router.py` |
| DOR-E06 | 页面明确 status-only / stock not restored | 强 | `templates/delivery_order_detail.html` |
| DOR-E07 | Inventory Adjust 是独立通用过账 | 强 | `apps/inventory/services.py::adjust_inventory` |
| DOR-E08 | DO Post AR 不读取 Reopen 状态 | 强 | `apps/inventory/services.py::apply_do_invoice`、Finance service |
| DOR-E09 | 退货/冲销知识证据 | 强佐证 | `../fulfillment-deepen/returns_reversal.md` |
| DOR-E10 | A-003 报告明确不自动恢复 | 强佐证 | `docs/reports/Business_Strong_A003_Delivery_Report.md` |

## UNKNOWN + 已查路径

1. **Reopen 的业务目的（纠错、重送、退货还是取消完成）UNKNOWN。** 已查：Inventory services/templates、business modules、delivery reports。
2. **重开后允许再次 Ship 的正式 reset 机制 UNKNOWN。** 已查：Ship 幂等、Reopen、ledger repository、templates。
3. **库存回补应使用何种专用反向交易 UNKNOWN。** 已查：Inventory Adjust、ledger 类型、Sales/Inventory、fulfillment-deepen。
4. **已有 AR 的 Reopen 应冲销、冻结还是保留 UNKNOWN。** 已查：Inventory/Finance services、ar_records、invoice/AR 文档。
5. **多 DO 对同一 SO 时 SO→Open 的正确性 UNKNOWN。** 已查：Sales create DO、DO/SO 查询、partial delivery 文档。
6. **重开原因、操作者和时间的审计位置 UNKNOWN。** 已查：handler、operation_logs、history、templates。
7. **客户退货、RMA、质检和 Credit Note 闭环 UNKNOWN。** 已查：apps/sales、inventory、finance、templates、business_modules、reports。

## 交叉引用

- 退货/冲销全景：[`../fulfillment-deepen/returns_reversal.md`](../fulfillment-deepen/returns_reversal.md)
- Ship 幂等：[`do_ship.md`](do_ship.md)
- AR 副作用：[`do_invoice_ar.md`](do_invoice_ar.md)
