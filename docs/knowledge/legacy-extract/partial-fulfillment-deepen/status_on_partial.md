# 部分履约下 SO / DO 状态漂移

**Evidence strength:** Strong  
**结论：** DO 状态按单据独立推进，但 SO 状态不是所有 DO 的聚合结果。canonical Create 任意一张 DO 就写 `Delivery Created`；Ship 不改 SO；任意一张 DO Complete 就写 `Delivered`；任意一张 complete DO Reopen 就写 `Open`。这些覆盖不查询同 SO 的其他 DO 或累计数量，因此多 DO 下 SO 状态由“最后一次动作”决定，而非真实履约比例。

## 状态覆盖矩阵

| 动作 | 当前 DO | SO 写入 | 是否汇总其他 DO |
|---|---|---|---|
| canonical Create DO | 新 Pending | Delivery Created | 否 |
| legacy Convert DO | 新 Pending | 不变 | 否 |
| Ship DO | 已出库 | 不变 | 否 |
| Complete DO | Delivered | Delivered | 否 |
| Reopen DO | Pending | Open | 否 |
| 再 canonical Create | 新 Pending | Delivery Created | 否 |

## 典型漂移

| DO 集合事实 | 最后动作 | SO 状态 | 漂移 |
|---|---|---|---|
| DO1 Delivered，DO2 Pending | Complete DO1 | Delivered | 未完成 DO2 被掩盖 |
| DO1 Delivered，DO2 Pending | Reopen DO1 后再 Complete | Delivered | 仍无数量聚合 |
| DO1 Delivered，DO2 Shipped | Reopen DO1 | Open | 已完成/已出库事实被掩盖 |
| DO1 Delivered | 新建 DO2 | Delivery Created | 已完成状态被降级 |
| legacy DO Pending | legacy create | 原 SO status | 已有 DO 但状态可能不反映 |
| 两张全量 DO 均 Shipped | 无 Complete | Delivery Created/其他 | 已超发但 SO 不显示 |

## 业务规则

| ID | 规则 |
|---|---|
| SOP-R01 | SO status 是单一文本字段。 |
| SOP-R02 | 每张 DO 有独立 status。 |
| SOP-R03 | canonical Create DO 无条件写 SO Delivery Created。 |
| SOP-R04 | legacy Convert DO 不写 SO status。 |
| SOP-R05 | Ship 只更新当前 DO。 |
| SOP-R06 | Ship 不写 Partially Shipped/Delivered。 |
| SOP-R07 | Complete 只要求当前 DO Shipped。 |
| SOP-R08 | Complete 无条件把关联 SO 写 Delivered。 |
| SOP-R09 | Complete 不查询该 SO 的其他 DO。 |
| SOP-R10 | Complete 不累计 SO line shipped qty。 |
| SOP-R11 | Reopen 只要求当前 DO Complete。 |
| SOP-R12 | Reopen 无条件把关联 SO 写 Open。 |
| SOP-R13 | Reopen 不查询其他 completed/shipped DO。 |
| SOP-R14 | 新 Create 可覆盖 Delivered/Open 等 SO 状态。 |
| SOP-R15 | SO detail 展示 linked DO count，但不派生权威 aggregate stage。 |
| SOP-R16 | 页面时间线把 DO count 标成 Shipped，数量为0/状态Pending也可能计入。 |
| SOP-R17 | AI partial 标签可从 open/closed DO 组合推断，但不回写业务状态。 |
| SOP-R18 | 批量 Complete 逐 DO 发 GET，不是 SO 级原子聚合。 |
| SOP-R19 | 不存在 Partially Delivered/Backordered canonical 状态。 |
| SOP-R20 | AI `_DO_CLOSED` 可把 Shipped 归入 closed，而 Inventory `do_stage` 仍把 Shipped 与 Complete 分开。 |

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| SOP-V01 | Ship 当前 DO 必须 open | Hard |
| SOP-V02 | Complete 当前 DO 必须 shipped | Hard |
| SOP-V03 | Reopen 当前 DO 必须 complete | Hard |
| SOP-V04 | SO Delivered 前所有 DO complete | Missing |
| SOP-V05 | SO Delivered 前 ordered qty 全部 shipped | Missing |
| SOP-V06 | SO Open 回退前检查其他 DO | Missing |
| SOP-V07 | Create DO 前检查 SO terminal status | Missing |
| SOP-V08 | Create 后 SO status 与 existing DO aggregate 一致 | Missing |
| SOP-V09 | 状态 transition matrix | Missing |
| SOP-V10 | 多 DO 更新使用 SO-level lock/version | Missing |
| SOP-V11 | Partially Shipped/Delivered 状态 | Missing |
| SOP-V12 | 批量 Complete 全部成功才提交 SO状态 | Missing |
| SOP-V13 | Complete/Reopen POST/CSRF/Human Confirm | Missing；GET |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `sales_orders.status` | 最后动作写入的标签，不是履约聚合 |
| `Delivery Created` | canonical Create 至少执行一次 |
| `Open` | SO Approve 或任一 DO Reopen 写入 |
| `Delivered` | 任一 DO Complete 写入 |
| `delivery_orders.so_id` | 可用于聚合，但状态 service 未聚合 |
| DO Pending | 当前 DO 待 Ship |
| DO 已出库/Shipped | 当前 DO 已扣库存 |
| DO Delivered/已完成 | 当前 DO Complete |
| linked DO count | SO detail 计数 |
| DO open/closed mix | AI partial 推断输入 |
| ordered qty | SO line qty，状态更新不读取 |
| shipped qty | ledger 事实，状态更新不读取 |
| remaining qty | 未建模 |
| partial status | AI 派生，不是 canonical SO 值 |
| batch Complete | 多个独立 GET 命令 |
| last writer wins | 多 DO 状态覆盖的实际语义 |
| AI closed DO | 启发式集合，可能包含库存已出但尚未 Complete 的 DO |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| SOP-E01 | canonical Create 写 Delivery Created | 强 | `apps/sales/services.py::create_delivery_order`、repository |
| SOP-E02 | legacy Convert 不更新 SO | 强负向 | `apps/inventory/services.py::_legacy_convert_do` |
| SOP-E03 | Ship 只更新 DO状态 | 强 | `apps/inventory/services.py::ship_delivery_order` |
| SOP-E04 | Complete 当前 DO 后直接 SO Delivered | 强 | `apps/inventory/services.py::_legacy_complete_do` |
| SOP-E05 | Reopen 当前 DO 后直接 SO Open | 强 | `apps/inventory/services.py::_legacy_reopen_do` |
| SOP-E06 | Complete/Reopen 无其他 DO 查询 | 强负向 | `apps/inventory/services.py` |
| SOP-E07 | SO detail 展示多个 DO/计数 | 强 | `templates/sales_order_detail.html` |
| SOP-E08 | Delivery list 批量逐个 GET Complete | 强 | `templates/delivery_orders.html` |
| SOP-E09 | AI partial 仅是派生语义 | 中等 | `v15/ai_operating_depth/semantics.py` |
| SOP-E10 | Complete/Reopen 权威边界 | 强交叉 | `../ship-complete-deepen/do_complete.md`、`do_reopen.md` |
| SOP-E11 | Order-chain SO→DO 状态说明 | 强交叉 | `../order-chain/so_to_do.md` |
| SOP-E12 | AI closed/open 分类与 Inventory 三阶段不完全一致 | 强 | `v15/ai_operating_depth/semantics.py`、`apps/inventory/services.py::do_stage` |

## UNKNOWN + 已查路径

1. **业务权威 SO aggregate 状态算法 UNKNOWN。** 已查：Sales/Inventory services、business_modules、reports。
2. **Partially Shipped/Delivered 是否允许作为状态值 UNKNOWN。** 已查：templates、i18n、status handlers、DDL。
3. **生产数据中 SO/DO 漂移规模 UNKNOWN。** 已查静态代码；未读生产 DB。
4. **多个 DO 中任一取消/失败时 SO 状态政策 UNKNOWN。** 已查：Delivery statuses、cancel/reopen、reports。
5. **批量 Complete 中途失败后的用户反馈/重试 UNKNOWN。** 已查：delivery_orders template JS、routes。
6. **AI partial 标签是否被任何业务 gate 使用 UNKNOWN。** 已查：semantics/forewarn、Inventory/Sales services。
7. **legacy/canonical 路径混用造成的状态不一致修复 UNKNOWN。** 已查：route ownership、residual reports。
8. **并发 Complete/Reopen 的最终状态确定性 UNKNOWN。** 已查：service SQL/commit、DB config。
9. **AI 将 Shipped 视为 closed 是否为有意业务口径 UNKNOWN。** 已查：AI semantics、Inventory stage、reports。

## 交叉引用

- SO→DO：[`../order-chain/so_to_do.md`](../order-chain/so_to_do.md)
- Partial delivery：[`../fulfillment-deepen/partial_delivery.md`](../fulfillment-deepen/partial_delivery.md)
- Ship：[`../ship-complete-deepen/do_ship.md`](../ship-complete-deepen/do_ship.md)
- Complete：[`../ship-complete-deepen/do_complete.md`](../ship-complete-deepen/do_complete.md)
- Reopen：[`../ship-complete-deepen/do_reopen.md`](../ship-complete-deepen/do_reopen.md)
