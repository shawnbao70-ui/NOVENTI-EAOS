# 分仓 / 分批 / 行级拆分证据

**Evidence strength:** Strong negative for DO allocation model  
**结论：** 生产 DO header/item 没有 warehouse、location、lot/batch、allocation 或 source_so_item 字段。Create DO 无选择界面，完整复制全部 SO 行；Ship 按 product_id 找第一条 inventory（`LIMIT 1`），不是按 DO 指定仓位扣减。Inventory location 与 Warehouse360/扫描能力存在，但没有形成 DO 行级分配。

## 能力矩阵

| 能力 | 生产事实 | 判定 |
|---|---|---|
| 选择本批行 | 无输入 | 缺失 |
| 输入本批 qty | 无输入 | 缺失 |
| DO header warehouse | 无字段 | 缺失 |
| DO item warehouse/location | 无字段 | 缺失 |
| lot/batch/serial | DO item 无字段 | 缺失 |
| source SO item | 无字段 | 缺失 |
| reservation/allocation | 无实体/写路径 | 缺失 |
| inventory location | 产品库存行有文本 location | 存在但未接 DO |
| Ship 库存选择 | product_id + LIMIT 1 | 弱/非分仓 |
| carton/packing | 页面/打印占位 | 非 allocation |

## 业务规则

| ID | 规则 |
|---|---|
| ALS-R01 | Create DO 不接受 warehouse 参数。 |
| ALS-R02 | Create DO 不接受行选择。 |
| ALS-R03 | Create DO 不接受 per-line partial qty。 |
| ALS-R04 | delivery_orders DDL 无 warehouse/location。 |
| ALS-R05 | delivery_order_items DDL 只有 do/product/qty/price/amount。 |
| ALS-R06 | DO item 不保存 source_so_item_id。 |
| ALS-R07 | DO item 不保存 lot/batch/serial。 |
| ALS-R08 | inventory 有 location 文本，但不是仓库 FK。 |
| ALS-R09 | Ship 只按 product_id 查询 inventory。 |
| ALS-R10 | 查询使用 LIMIT 1，未定义多库存行选择顺序。 |
| ALS-R11 | 缺 inventory 时以产品镜像创建空 location 基线。 |
| ALS-R12 | Ship UI 展示 DO 行/on-hand，不提供仓位分配。 |
| ALS-R13 | Warehouse scan/action 是独立库存操作面，不回写 DO allocation。 |
| ALS-R14 | Warehouse360 enrichment 不改变 Ship repository 选择逻辑。 |
| ALS-R15 | packing/carton 未成为批次拆分实体。 |
| ALS-R16 | 多 DO 可被人为当“批次”，但每张仍是全量复制。 |
| ALS-R17 | 多仓库存汇总/预留/释放没有进入 SO→DO→Ship 链。 |
| ALS-R18 | 分批发货目标态规格不能替代当前运行证据。 |
| ALS-R19 | platform v14 residual 的创建即扣产品库存是历史重复路由，不是 reservation/allocation；标准 cutover 通常跳过。 |

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| ALS-V01 | DO 必须指定仓库 | Missing |
| ALS-V02 | DO line 必须指定库位 | Missing |
| ALS-V03 | 本批 qty 必须 <= remaining | Missing |
| ALS-V04 | allocation 必须 <= warehouse available | Missing |
| ALS-V05 | lot/serial 必须有效且可追溯 | Missing |
| ALS-V06 | source SO item 必须唯一 | Missing |
| ALS-V07 | inventory product_id 必须唯一 | Missing in public DDL |
| ALS-V08 | 多 inventory 行必须有选择策略 | Missing；LIMIT 1 |
| ALS-V09 | Ship 仓库必须等于 allocation 仓库 | Missing |
| ALS-V10 | reservation 与 Ship 原子消费 | Missing |
| ALS-V11 | 取消/Reopen 必须释放 allocation | Missing |
| ALS-V12 | 空/无效 allocation 不得 Ship | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `inventory.product_id` | Ship 查找库存的产品键 |
| `inventory.location` | 自由文本库位元数据 |
| inventory row `id` | 实际被扣的库存行 |
| `LIMIT 1` | 无排序的首条产品库存选择 |
| `delivery_orders` | 不含仓库的履约头 |
| `delivery_order_items` | 不含 allocation 的履约行 |
| DO item qty | 整单复制数量，不是分配数量 |
| source SO item id | 未持久化 |
| warehouse_id | 生产 DO 未持久化 |
| lot/batch/serial | 生产 DO 未持久化 |
| reserved qty | 未建模 |
| allocated qty | 未建模 |
| pick qty | 未建模 |
| carton | 打印/页面包装概念，不是库存批次 |
| Warehouse360 | 平行展示/enrichment 能力 |
| scan action | 独立 Receive/Ship/Move 库存动作 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| ALS-E01 | Create DO 参数无仓/批/本批 qty | 强 | `apps/sales/services.py::create_delivery_order` |
| ALS-E02 | DO header/item DDL 无 allocation 字段 | 强负向 | `runtime/v14/legacy_support.py` |
| ALS-E03 | SO item SELECT 只取 product/qty/price/amount | 强 | `apps/sales/repository.py::fetch_so_items_for_delivery` |
| ALS-E04 | inventory 按 product_id LIMIT 1 | 强 | `apps/inventory/repository.py::fetch_inventory_by_product_id` |
| ALS-E05 | Ship 不读取 warehouse/location | 强负向 | `apps/inventory/services.py::ship_delivery_order` |
| ALS-E06 | DO detail 无 allocation 输入 | 强负向 | `templates/delivery_order_detail.html` |
| ALS-E07 | Inventory location 仅库存 metadata | 强 | `apps/inventory/repository.py`、templates |
| ALS-E08 | Warehouse scan/action 独立于 DO | 强 | `apps/inventory/services.py::build_scan_action_context` |
| ALS-E09 | Partial delivery 权威确认无行选择 | 强交叉 | `../fulfillment-deepen/partial_delivery.md` |
| ALS-E10 | Shipment 模块是目标规格 | 中等 | `business_modules/shipment.md` |
| ALS-E11 | historical residual create/do_ship 均直接扣 products | 强历史 | `apps/platform/v14_residual.py` |
| ALS-E12 | canonical 路径优先、重复 residual 路径过滤 | 强 | `bootstrap/enterprise_cutover.py`、`bootstrap/v14_residual.py` |

## UNKNOWN + 已查路径

1. **生产 DB 是否私加 warehouse/allocation 字段 UNKNOWN。** 已查：公开 DDL、database patches、tenant schemas。
2. **多个 inventory row 同 product 是否存在 UNKNOWN。** 已查：DDL/query；未读生产 DB。
3. **LIMIT 1 实际选择哪个仓位是否稳定 UNKNOWN。** 已查：SQLite query，无 ORDER BY。
4. **Warehouse360 是否有未公开写回 DO 插件 UNKNOWN。** 已查：core/object360/warehouse、Inventory integration。
5. **扫描 Ship 是否被运营当作 DO 拣货 UNKNOWN。** 已查：scan action、DO routes/templates、reports。
6. **carton/packing 是否线下记录批次 UNKNOWN。** 已查：packing templates/docs、DO schema。
7. **lot/serial 在其他私有模块是否与 DO 关联 UNKNOWN。** 已查：apps、business_modules、reports 关键词。
8. **多仓优先级、波次、预留释放政策 UNKNOWN。** 已查：Inventory/Sales/Shipment specs、reports。

## 交叉引用

- Partial delivery 权威：[`../fulfillment-deepen/partial_delivery.md`](../fulfillment-deepen/partial_delivery.md)
- 库存/仓位缺口：[`../fulfillment-deepen/warehouse.md`](../fulfillment-deepen/warehouse.md)
