# Receipt → Stock：库存/产品镜像/台账三写

**Evidence strength:** Strong for order; conditional for atomic conservation  
**结论：** 每条有效 PO 行按 inventory absolute balance、products positive delta、PO Receipt ledger 顺序三写；所有行后 PO→Received，再由共享连接 commit。正常单线程且 inventory/products 起点一致时守恒。实现没有全单预检、显式 rollback、rowcount/镜像对账或 DB 约束，中途失败与并发不能证明原子守恒。

## 守恒公式

对每个有效 qty `q>0`：

- `inventory_after = inventory_before + q`
- `product_after = product_before + q`
- `ledger.qty = +q`
- `ledger.balance_qty = inventory_after`

前提是两份起始余额一致、inventory/product 更新均命中、ledger 成功且整单提交。

## 三写顺序

1. 按 product_id 取得/建立 inventory。
2. 读取 inventory on_hand。
3. `new_qty = on_hand + receipt qty`。
4. 写 `inventory.stock_qty = new_qty`。
5. 写 `products.stock_qty += qty`。
6. 插入正 qty 与 new balance 的 `PO Receipt` ledger。
7. 所有行完成后 PO→Received。
8. Procurement repository commit 提交共享连接。

## 业务规则

| ID | 规则 |
|---|---|
| RTS-R01 | Receive 读取 PO 全部 item 的 product_id/qty。 |
| RTS-R02 | qty<=0 或 product_id=0 的行跳过。 |
| RTS-R03 | 缺 inventory 时从 products.stock_qty 建基线。 |
| RTS-R04 | inventory 使用绝对新余额写入。 |
| RTS-R05 | products 使用正 delta 更新。 |
| RTS-R06 | ledger qty 为正收货数量。 |
| RTS-R07 | ledger balance 使用 inventory new_qty。 |
| RTS-R08 | product code/name 写入 ledger 快照。 |
| RTS-R09 | 同一次 PO Receive 所有 ledger 共用 create_time/remark。 |
| RTS-R10 | 同产品多行逐行三写，不预聚合。 |
| RTS-R11 | inventory helpers 不自行 commit。 |
| RTS-R12 | Procurement 与 Inventory repositories 共享 cursor/conn。 |
| RTS-R13 | PO status 与三写在末尾同一次显式 commit。 |
| RTS-R14 | 中途 inventory_missing 直接 return，不显式 rollback。 |
| RTS-R15 | SQL exception 未在 Receive 内统一 catch/compensate。 |
| RTS-R16 | product UPDATE 不检查 rowcount。 |
| RTS-R17 | 收货前不对账 inventory 与 products 镜像。 |
| RTS-R18 | inventory.product_id 公开 DDL 未见 unique，查询 LIMIT 1。 |
| RTS-R19 | product 不存在时可能形成空产品快照/孤立库存风险，未见 FK 硬门。 |

## 失败边界

| 场景 | inventory | products | ledger | PO status |
|---|---|---|---|---|
| 正常成功 | +q | +q | +q row | Received |
| 无 items | 不变 | 不变 | 无 | open |
| 全无效 items | 不变 | 不变 | 无 | Received |
| 后续行失败 | 前行 SQL 已执行、未明确 rollback | 同左 | 前行 insert 已执行 | 未更新 |
| product UPDATE 0 rows | inventory 已加 | 未加 | 仍可能写 | 可 Received |
| ledger INSERT 异常 | inventory/product 已执行 | 已执行 | 当前行失败 | 未更新 |
| 并发 Receive | 可能丢失/双加 | 可能双加 | 可能重复 | 竞态 |

“已执行”不等于持久化；early return 后连接如何 rollback/复用由外层决定，service 没有明确化。

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| RTS-V01 | PO open/未重复/有 items | Hard |
| RTS-V02 | inventory 可取得/建立 | Hard per line |
| RTS-V03 | qty 必须正且 product有效 | Weak；无效行跳过 |
| RTS-V04 | 至少一条有效行 | Missing |
| RTS-V05 | 全单先预检再写 | Missing |
| RTS-V06 | product 必须存在 | Missing/weak |
| RTS-V07 | inventory/product UPDATE rowcount=1 | Missing |
| RTS-V08 | inventory/product 起始一致 | Missing |
| RTS-V09 | ledger/余额自动对账 | Missing |
| RTS-V10 | 显式 rollback on return/exception | Missing |
| RTS-V11 | 原子锁/版本防并发 | Missing |
| RTS-V12 | inventory product_id 唯一 | Missing in public DDL |
| RTS-V13 | 小数精度/单位换算 | Missing |
| RTS-V14 | commit 异常重试与结果确认 | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| purchase item qty | 本次一次性入库数量 |
| inventory row id | 被绝对更新的库存行 |
| inventory.product_id | 查找键 |
| inventory.stock_qty | 收货后 on-hand |
| products.stock_qty | Legacy 产品镜像 |
| `PO Receipt` | 正向入库交易类型 |
| ledger qty | 正数变动 |
| ledger balance_qty | inventory after 快照 |
| product code/name | ledger 文本快照 |
| `PO-{purchase_id}` | 来源/判重 remark |
| create_time | 应用服务器收货时间 |
| Received | 全循环后 PO 状态 |
| shared connection | 两 repository 三写提交边界 |
| rowcount | 未检查的命中证据 |
| rollback | 未显式调用的失败清理 |
| conservation | 三份库存事实一致的条件性不变量 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| RTS-E01 | Receive 逐行三写顺序 | 强 | `apps/procurement/services.py::receive_purchase` |
| RTS-E02 | Inventory absolute update | 强 | `apps/inventory/repository.py::update_inventory_stock_qty` |
| RTS-E03 | Product positive delta | 强 | `apps/inventory/repository.py::apply_product_stock_delta` |
| RTS-E04 | Ledger insert | 强 | `apps/inventory/repository.py::insert_inventory_ledger` |
| RTS-E05 | 缺 inventory 从 product 镜像建基线 | 强 | `apps/inventory/repository.py::ensure_inventory_for_product` |
| RTS-E06 | 两 repository 共享 cursor/conn | 强 | `apps/procurement/services.py::_inv_repo` |
| RTS-E07 | PO status 后末尾 commit | 强 | `apps/procurement/services.py` |
| RTS-E08 | 中途 return 无 rollback | 强负向 | `apps/procurement/services.py` |
| RTS-E09 | inventory DDL 无 product unique/FK | 强负向 | `runtime/v14/legacy_support.py` |
| RTS-E10 | A-004 验证正向三写 | 中等 | `docs/reports/Business_Strong_A004_Purchase_Report.md` |

## UNKNOWN + 已查路径

1. **early return 后共享连接是否自动 rollback UNKNOWN。** 已查：Procurement router/service、DB context/adapter/bootstrap。
2. **生产 inventory/product 镜像漂移规模 UNKNOWN。** 已查代码/报告；未读生产 DB。
3. **重复 inventory product 行是否存在 UNKNOWN。** 已查：DDL/query；未读生产数据。
4. **生产 DB foreign_keys/unique 私补 UNKNOWN。** 已查：公开 DDL/index/migrations。
5. **并发双 Receive 的实际 SQLite 调度 UNKNOWN。** 已查：adapter/config/service。
6. **产品不存在的 purchase item 是否有历史数据 UNKNOWN。** 已查：add item、product delete、DDL。
7. **成本估值是否应随收货更新 product cost UNKNOWN。** 已查：Receive/Inventory/Product/Finance；当前不改成本。
8. **浮点 qty 与单位换算政策 UNKNOWN。** 已查：REAL/float 使用、templates、business modules。

## 交叉引用

- Procurement 运行权威：[`../ops/procurement.md`](../ops/procurement.md)
- Inventory 运行权威：[`../ops/inventory.md`](../ops/inventory.md)
