# Delivery Order Ship：出库时点与库存扣减

**Evidence strength:** Strong for active Ship service and stock effects  
**Cross-reference:** [`../delivery/delivery_order.md`](../delivery/delivery_order.md)、[`../fulfillment-deepen/README.md`](../fulfillment-deepen/README.md)

## Scope 与关键结论

Create DO 与 Ship 是两个分离动作。Sales 创建 DO 时只复制 SO 行并把 DO 置 Pending，不扣库存；Ship 才检查开放阶段、出库流水和逐行库存，然后同步减少 `inventory.stock_qty`、`products.stock_qty`，追加负数 `DO Ship` 流水，最后把 DO 写为 `已出库`。Complete/Delivered 是后续状态动作，不再过账。

## 业务规则

| ID | 规则 |
|---|---|
| DOS-R01 | Sales Create DO 复制 SO 全部行，创建时不扣库存、不写 `inventory_ledger`。 |
| DOS-R02 | Create DO 生成 Pending DO，并把关联 SO 写为 `Delivery Created`。 |
| DOS-R03 | Ship 只允许 open stage：`Pending / 待出库 / Pending Outbound`。 |
| DOS-R04 | Shipped 或 Complete stage 再 Ship 返回 `already_shipped`。 |
| DOS-R05 | Ship 前以 `trans_type='DO Ship'` + `remark='DO-{do_no}'` 查询既有流水。 |
| DOS-R06 | 每条有效行必须有正数量和 product id；无效行当前被跳过而非阻断。 |
| DOS-R07 | 产品缺库存行时，可从 `products.stock_qty` 建立 inventory 基线。 |
| DOS-R08 | 任一有效行现存量小于发货量时返回 `insufficient_stock`。 |
| DOS-R09 | 每条有效行把 inventory 减 qty，并对 product 镜像应用同量负 delta。 |
| DOS-R10 | 每条有效行追加负数 qty、过账后余额、产品代码/名称和 DO remark 的流水。 |
| DOS-R11 | 全部循环完成后 DO 状态写为中文 `已出库` 并提交。 |
| DOS-R12 | Ship 不把 SO 直接写 Delivered；SO 完成由后续 Complete 动作处理。 |
| DOS-R13 | V18 Ship 要求页面人工确认 `human_confirm=1`，GET 别名只重定向到确认页。 |
| DOS-R14 | Ship GET 要求 Delivery Orders view，POST 要求 edit。 |
| DOS-R15 | 扫码 Ship 最终复用同一 `ship_delivery_order`，不是第二套库存算法。 |
| DOS-R16 | Ship 幂等依赖应用层先查后写，没有观察到数据库唯一过账键。 |
| DOS-R17 | 多行过账在末尾 commit；中途返回前已执行的 SQL 是否统一回滚未被显式证明。 |

## Create DO 与 Ship 差异

| 维度 | Create DO | Ship |
|---|---|---|
| Owner | Sales | Inventory |
| 入口 | `/create_do/{so_id}` GET | Type A GET/POST |
| 行为 | 复制 SO 头/全部行 | 读取 DO 行并逐行过账 |
| inventory | 不变 | 减少 |
| product stock | 不变 | 同步减少 |
| ledger | 不写 | `DO Ship` 负数流水 |
| DO 状态 | Pending | 已出库 |
| SO 状态 | Delivery Created | 不变 |
| 人工门 | 创建 handler 无 Type A | Human Confirm |

## Ship 流程

1. 用户打开 Type A Ship，核对客户、DO/SO、行和金额。
2. POST 校验 edit 权限和 `human_confirm=1`。
3. 服务读取 DO，确认 open stage 且不存在同 DO Ship 流水。
4. 逐行确保库存行并检查现存量。
5. 逐行扣 inventory、扣产品镜像、写负数流水。
6. DO 写为 `已出库`，统一提交并返回详情。
7. 后续 Complete 才把 DO/SO 推进 Delivered。

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| DOS-V01 | DO 必须存在 | Hard |
| DOS-V02 | 状态必须为 open stage | Hard |
| DOS-V03 | 不得已有同 DO Ship 流水 | Hard application guard |
| DOS-V04 | V18 POST 必须 `human_confirm=1` | Hard |
| DOS-V05 | POST 必须 Delivery Orders edit | Hard |
| DOS-V06 | 每条有效行库存必须充足 | Hard |
| DOS-V07 | 库存行必须可读取或建立 | Hard |
| DOS-V08 | DO 必须至少有一条有效行 | Missing；空/无效行可走到成功 |
| DOS-V09 | qty 必须大于零且 product id 有效 | Weak；无效行被跳过 |
| DOS-V10 | 幂等键必须数据库唯一 | Missing |
| DOS-V11 | 多行库存校验必须先整体完成再写 | Missing；当前边查边写 |
| DOS-V12 | 库存扣减必须使用原子条件更新/锁 | Missing |
| DOS-V13 | 创建 DO 前 SO 必须 Open 且未已有 DO | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `delivery_orders.status` | Ship 前阶段与 Ship 后 `已出库` |
| `delivery_order_items.product_id` | 要扣减的产品 |
| `delivery_order_items.qty` | 本次计划出库数量 |
| `inventory.stock_qty` | Ship 实际扣减的现存量 |
| `products.stock_qty` | 同量更新的 Legacy 镜像 |
| `inventory_ledger.trans_type` | `DO Ship` 标识出库类型 |
| `inventory_ledger.qty` | 出库为负数 `-qty` |
| `inventory_ledger.balance_qty` | 该行过账后的 inventory 余额 |
| `inventory_ledger.remark` | `DO-{do_no}`，同时充当应用层幂等关联 |
| `product_code/product_name` | 出库时写入流水的产品快照 |
| `create_time` | 应用服务器生成的出库时间文本 |
| `Pending` | Create DO 后可 Ship 的默认值 |
| `已出库` | Ship 成功写入的 canonical 状态 |
| `Delivery Created` | Create DO 对 SO 的状态副作用 |
| `human_confirm` | Type A Ship 的人工确认输入 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| DOS-E01 | Create DO 复制行但明确不扣库存 | 强 | `apps/sales/services.py::create_delivery_order` |
| DOS-E02 | Create DO 写 SO Delivery Created | 强 | `apps/sales/repository.py` |
| DOS-E03 | Ship 状态、流水判重与库存检查 | 强 | `apps/inventory/services.py::ship_delivery_order` |
| DOS-E04 | Inventory/product/ledger 三写 | 强 | `apps/inventory/services.py`、`repository.py` |
| DOS-E05 | 缺库存行按产品库存建基线 | 强 | `apps/inventory/repository.py::ensure_inventory_for_product` |
| DOS-E06 | Type A 权限和 Human Confirm | 强 | `apps/inventory/router.py`、`templates/do_ship.html` |
| DOS-E07 | 页面明确 Ship 后再 Complete | 强 | `templates/delivery_order_detail.html`、`do_ship.html` |
| DOS-E08 | 创建不扣库存的 A-003 验收 | 强佐证 | `docs/reports/Business_Strong_A003_Delivery_Report.md` |
| DOS-E09 | Type A Ship/Invoice 行为 | 强佐证 | `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` |
| DOS-E10 | 运行模块交界迁移 | 中 | `docs/reports/V151E_Volume010_Finance_Inventory_Business_Chain_Extraction_Report.md` |

## UNKNOWN + 已查路径

1. **多行 Ship 中途失败是否由外层连接自动完整回滚 UNKNOWN。** 已查：`apps/inventory/services.py`、`repository.py`、连接 factory/commit 点。
2. **`DO Ship + remark` 是否有数据库唯一约束 UNKNOWN。** 已查：repository 查询、`runtime/v14/legacy_support.py` 流水 DDL、升级脚本。
3. **并发 Ship 是否可能同时通过先查和库存校验 UNKNOWN。** 已查：Ship service/repository；未见锁、版本或原子条件更新。
4. **空 DO 或全部无效行成功写 Shipped 是否为有意政策 UNKNOWN。** 已查：Ship service、Create DO、Type A 页面。
5. **历史版本 Create DO 是否曾直接扣库存及存量数据如何识别 UNKNOWN。** 已查：`apps/platform/v14_residual.py`、A-003/A-002 报告、inventory ledger。
6. **多仓/库位应从哪一库存行扣减 UNKNOWN。** 已查：inventory repository 只 `product_id LIMIT 1`、fulfillment-deepen warehouse。
7. **租户隔离是否覆盖 Ship 全部读写 UNKNOWN。** 已查：Inventory/Sales repositories、tenant scope/migration 相关路径。

## 交叉引用

- DO 基线：[`../delivery/delivery_order.md`](../delivery/delivery_order.md)
- 预留、分批和仓位缺口：[`../fulfillment-deepen/README.md`](../fulfillment-deepen/README.md)
- 库存台账：[`../inventory-deepen/stock_ledger.md`](../inventory-deepen/stock_ledger.md)
