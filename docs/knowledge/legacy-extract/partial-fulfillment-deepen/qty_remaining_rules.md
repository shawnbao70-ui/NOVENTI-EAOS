# 已发/未发数量累计与超发控制

**Evidence strength:** Strong negative for cumulative fulfillment controls  
**结论：** Legacy 保存 SO qty 和每张 DO qty，Ship ledger 保存每次负变动，但没有 `shipped_qty/delivered_qty/remaining_qty/backorder_qty` 字段，也没有按 SO/line 汇总已发的服务。Ship 只校验当前 DO qty 对库存是否足够、当前 DO 是否已发；第二张全量 DO 可再次扣库，跨 DO 超发不被订单数量阻断。

## 期望公式与实际

期望：

`remaining(line) = SO ordered qty - Σ shipped qty across all non-reversed DO lines`

Legacy 实际：

- Create DO：`DO.qty = SO.qty`
- Ship：只检查 `inventory.on_hand >= DO.qty`
- Idempotency：只检查当前 `do_no`
- SO status：不读取任何累计 qty

因此系统没有可执行的 remaining 公式。

## 业务规则

| ID | 规则 |
|---|---|
| QRR-R01 | sales_order_items.qty 是订单原数量。 |
| QRR-R02 | 每次 Create DO 原样复制该 qty。 |
| QRR-R03 | delivery_order_items 没有 source_so_item_id。 |
| QRR-R04 | Ship 对当前 DO 每个正 qty 行扣库存。 |
| QRR-R05 | Ship 不查询同 SO 的其他 DO。 |
| QRR-R06 | Ship 不汇总历史 DO Ship ledger 到 SO line。 |
| QRR-R07 | Ship 充足性只以当前产品库存为上限。 |
| QRR-R08 | 同 DO 防重不等于同 SO 防超发。 |
| QRR-R09 | 第二张不同 do_no DO 可有独立 ledger 判重空间。 |
| QRR-R10 | 若库存足够，第二张全量 DO 可再次 Ship。 |
| QRR-R11 | ledger 只有 product_id 和文本 DO remark，没有 SO/DO item FK。 |
| QRR-R12 | 多个相同 product 的 SO 行无法仅凭 ledger 精确回配原行。 |
| QRR-R13 | 无 partial delivered/backorder/short-close 容差政策。 |
| QRR-R14 | Complete 不计算数量，只看当前 DO stage。 |
| QRR-R15 | SO detail 的 DO count 不等于累计已发 qty。 |
| QRR-R16 | AI partial 标签按 DO 头状态组合推断，不是数量核算。 |
| QRR-R17 | NDE `delivered_qty` 只是当前 DO 行 qty 的展示映射。 |
| QRR-R18 | Reopen 不冲销 shipped qty，因为该累计本就未建模。 |
| QRR-R19 | AI closed/open DO 分类与 Inventory 的 shipped/complete 阶段不完全一致，不能替代 qty 累计。 |

## 数量场景

| 场景 | SO qty | DOs | 可观察结果 |
|---|---:|---|---|
| 正常单 DO | 10 | DO1=10 | Ship 扣 10 |
| 两张 canonical 全量 DO | 10 | DO1=10, DO2=10 | 库存足够时可累计扣 20 |
| legacy 同号 DO | 10 | 两张均 `DO{so_id}` | 第一张 ledger 可能阻断第二张 |
| 想分批 6+4 | 10 | 无 qty 输入 | 两张默认均 10 |
| 第一张只改为6 | 10 | 无正式编辑/remaining链 | 第二张仍默认复制10 |
| 同产品两 SO 行 | 6+4 | DO复制两行 | ledger按产品/DO，缺 source line |

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| QRR-V01 | 当前 DO qty >0/product有效 | Weak；无效行跳过 |
| QRR-V02 | 当前 inventory 足够 | Hard per line |
| QRR-V03 | 当前 DO 未 Ship | Hard stage+ledger |
| QRR-V04 | 本批 qty <= SO line remaining | Missing |
| QRR-V05 | 跨 DO 累计 shipped <= ordered | Missing |
| QRR-V06 | DO line 必须引用 source SO item | Missing |
| QRR-V07 | ledger 必须引用 DO item/SO item | Missing |
| QRR-V08 | 部分发货必须更新 remaining | Missing |
| QRR-V09 | 超发容差与审批 | Missing |
| QRR-V10 | 短交关闭/backorder 处理 | Missing |
| QRR-V11 | reversal 必须冲减累计已发 | Missing |
| QRR-V12 | 同产品多行的精确归集 | Missing |
| QRR-V13 | 并发多 DO Ship 的 SO-level lock | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `sales_order_items.qty` | ordered qty |
| `sales_order_items.id` | 未复制到 DO line 的源行键 |
| `delivery_order_items.qty` | 当前 DO 计划 Ship qty |
| `delivery_order_items.do_id` | DO 归属 |
| `delivery_order_items.product_id` | 产品关联，不能唯一识别 SO line |
| `inventory.stock_qty` | Ship 的实际数量上限 |
| ledger qty | 当前 DO Ship 的负库存变动 |
| ledger remark | DO no 文本关联 |
| shipped qty | 可事后推导但无权威累计字段 |
| delivered qty | 未建模；打印名不等于累计事实 |
| remaining qty | 未建模 |
| backorder qty | 未建模 |
| over-delivery tolerance | 未建模 |
| short close | 未建模 |
| DO count | 单据计数，不是数量进度 |
| fulfillment:partial | AI 头状态推断标签 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| QRR-E01 | DO line 每次复制 SO qty | 强 | `apps/sales/services.py::create_delivery_order` |
| QRR-E02 | SO→DO SELECT 无 remaining 聚合 | 强 | `apps/sales/repository.py::fetch_so_items_for_delivery` |
| QRR-E03 | DO item DDL 无 source line/remaining 字段 | 强负向 | `runtime/v14/legacy_support.py` |
| QRR-E04 | Ship 只读当前 DO items | 强 | `apps/inventory/services.py::ship_delivery_order` |
| QRR-E05 | Ship 防重只按当前 do_no | 强 | `apps/inventory/repository.py::count_inventory_ledger_for_do` |
| QRR-E06 | ledger DDL 无 DO/SO item FK | 强负向 | `runtime/v14/legacy_support.py` |
| QRR-E07 | Complete 不做数量累计 | 强负向 | `apps/inventory/services.py::_legacy_complete_do` |
| QRR-E08 | SO detail 只列 DO/计数 | 强 | `templates/sales_order_detail.html` |
| QRR-E09 | AI partial 以 DO 头组合推断 | 中等 | `v15/ai_operating_depth/semantics.py` |
| QRR-E10 | NDE delivered_qty 来自当前 DO item | 中等 | `document/nde_engine.py` |
| QRR-E11 | AI `_DO_CLOSED` 与 Inventory do_stage 口径不同 | 强 | `v15/ai_operating_depth/semantics.py`、`apps/inventory/services.py` |

## UNKNOWN + 已查路径

1. **业务是否允许超发及容差比例 UNKNOWN。** 已查：Sales/Inventory、business_modules、reports。
2. **生产数据是否已有跨 DO 超发 UNKNOWN。** 已查静态代码；未读生产 DB。
3. **是否有离线报表计算 remaining qty UNKNOWN。** 已查：docs/reports、analytics/dashboard、scripts。
4. **同产品多 SO 行的履约分摊规则 UNKNOWN。** 已查：SO/DO item schema、services、templates。
5. **取消/退货应如何冲减 shipped 累计 UNKNOWN。** 已查：Reopen、Inventory Adjust、returns docs。
6. **超发是否需要客户审批 UNKNOWN。** 已查：approval/governance、Sales/Delivery modules。
7. **并发多个 DO Ship 是否有外部 SO-level serialization UNKNOWN。** 已查：routes/services/DB config。
8. **历史 ledger remark 能否可靠 join 回唯一 DO UNKNOWN。** 已查：do_no 生成、DDL、duplicate guard。

## 交叉引用

- Partial delivery 权威：[`../fulfillment-deepen/partial_delivery.md`](../fulfillment-deepen/partial_delivery.md)
- Ship：[`../ship-complete-deepen/do_ship.md`](../ship-complete-deepen/do_ship.md)
