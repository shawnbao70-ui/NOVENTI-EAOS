# Ship Posting：库存/产品镜像/台账三写守恒与失败边界

**Evidence strength:** Strong for statement order; conditional for atomic conservation  
**结论：** 每条有效 DO 行按 `inventory.stock_qty = on_hand-qty`、`products.stock_qty += -qty`、ledger `qty=-qty/balance=new_qty` 顺序三写；所有行完成后才更新 DO 状态并 commit。正常、单线程、两份起始余额一致时可守恒。但服务边校验边写，没有预检全单、显式 BEGIN/rollback、受影响行数校验或镜像对账；中途 return/exception 与并发下的原子性不能由该实现保证。

## 守恒公式

对每个有效行 `q > 0`：

- `inventory_after = inventory_before - q`
- `product_after = product_before - q`
- `ledger.qty = -q`
- `ledger.balance_qty = inventory_after`

只有当 `inventory_before == product_before`、两次 UPDATE 均命中同一产品、ledger INSERT 成功且整单原子提交时，才有：

`inventory_after == product_after == ledger.balance_qty`

## 三写顺序

1. 从 inventory 行读取 `on_hand`。
2. 校验 `on_hand >= qty`。
3. 计算 `new_qty = on_hand - qty`。
4. 绝对写 `inventory.stock_qty = new_qty`。
5. delta 写 `products.stock_qty += -qty`。
6. 插入负 qty、new balance 与 DO remark 的 ledger。
7. 下一条 DO 行重复以上步骤。
8. 循环后 DO→`已出库`，统一 commit。

## 业务规则

| ID | 规则 |
|---|---|
| SPC-R01 | qty<=0 或 product_id 无效的 DO 行被跳过。 |
| SPC-R02 | 缺 inventory 行时从 products.stock_qty 建立基线。 |
| SPC-R03 | 库存充足校验只看选中的 inventory 行。 |
| SPC-R04 | inventory 使用读取后计算的绝对余额更新。 |
| SPC-R05 | products 使用相对 delta 更新。 |
| SPC-R06 | ledger qty 固定为负发货数量。 |
| SPC-R07 | ledger balance 固定使用本次计算的 inventory new_qty。 |
| SPC-R08 | ledger code/name 是产品当时快照；产品缺失时可为空。 |
| SPC-R09 | 每个有效 DO item 产生一条 ledger，不按 product 聚合。 |
| SPC-R10 | 同 product 多行按循环顺序读取连接内最新 inventory 值。 |
| SPC-R11 | 三写 helper 本身都不 commit；Ship 末尾统一 commit。 |
| SPC-R12 | DO 状态更新也在末尾 commit 中。 |
| SPC-R13 | 中途库存不足发生在前面行已执行 SQL 之后。 |
| SPC-R14 | 中途 return 没有显式 rollback。 |
| SPC-R15 | 任一 SQL exception 没有在 Ship service 内捕获/补偿。 |
| SPC-R16 | 不校验 product UPDATE/ inventory UPDATE 的 rowcount。 |
| SPC-R17 | 不在 Ship 前核对 inventory 与 products 镜像一致。 |
| SPC-R18 | inventory.product_id 公开 DDL 未见唯一约束，查询 `LIMIT 1`。 |
| SPC-R19 | 空 DO/全无效行仍更新 DO 为 Shipped，三写为零次。 |
| SPC-R20 | Inventory router 在配置时把注入的 cursor/conn 固化到模块级 service，而非每请求创建 repository。 |

## 成功与失败边界

| 场景 | inventory | product mirror | ledger | DO status |
|---|---|---|---|---|
| 正常成功 | -q | -q | 新增 -q | 已出库 |
| 空/全无效行 | 不变 | 不变 | 无 | 已出库 |
| 第一行库存不足 | 无三写 | 无三写 | 无 | open |
| 后续行库存不足 | 前行 SQL 已执行、未显式 rollback | 同左 | 前行 insert 已执行 | 未更新 |
| product UPDATE 未命中 | inventory 已执行 | 0 rows | 仍可能插入 | 末尾可成功 |
| ledger INSERT 异常 | inventory/product SQL 已执行 | 已执行 | 当前行失败 | 未更新 |
| commit 异常 | 提交结果未知 | 提交结果未知 | 提交结果未知 | 提交结果未知 |
| 并发 Ship | 可能丢失更新 | 可能双 delta | 可能重复 | 竞态 |

“SQL 已执行”不等于已经持久化；最终是 rollback、连接内悬挂后被后续 commit，还是部分可见，取决于外层连接生命周期/事务处理，当前 service 没有明确化。

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| SPC-V01 | DO 存在且 open | Hard |
| SPC-V02 | 每个有效行 inventory 可取得/建立 | Hard per line |
| SPC-V03 | inventory on_hand >= qty | Hard per line |
| SPC-V04 | human_confirm 与 edit 权限 | Hard request gate |
| SPC-V05 | 先预检所有行再执行写入 | Missing |
| SPC-V06 | qty/product 无效即整单失败 | Missing；当前跳过 |
| SPC-V07 | 至少一条有效行 | Missing |
| SPC-V08 | inventory/product 起始镜像一致 | Missing |
| SPC-V09 | 两个 UPDATE 均影响恰好一行 | Missing |
| SPC-V10 | ledger 与余额守恒对账 | Missing |
| SPC-V11 | 显式 rollback on return/exception | Missing |
| SPC-V12 | 原子条件扣减防超卖 | Missing |
| SPC-V13 | inventory product_id 唯一 | Missing in public DDL |
| SPC-V14 | commit 成功后再响应 ok | 有调用；异常处理缺失 |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `delivery_order_items.qty` | 计划且一次性发出的数量 |
| `delivery_order_items.product_id` | 三写关联产品 |
| `inventory.id` | 被绝对更新的库存行 |
| `inventory.product_id` | 查找键，但公开 DDL 非唯一 |
| `inventory.stock_qty` | Ship 充足性判断的权威在手量 |
| `products.stock_qty` | Legacy 展示/兼容镜像 |
| `inventory_ledger.qty` | 本次变动，Ship 为负 |
| `inventory_ledger.balance_qty` | 当前 item 过账后的 inventory 余额 |
| `product_code/name` | ledger 文本快照 |
| `remark` | DO 文本关联与判重锚 |
| `create_time` | 全次 Ship 共用的应用时间文本 |
| repository commit | 三写与 DO 状态的预期提交点 |
| rowcount | 当前未检查的写命中证据 |
| rollback | 当前 service 未调用的失败清理动作 |
| conservation | 三份结果一致的条件性不变量 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| SPC-E01 | 逐行校验后立即三写 | 强 | `apps/inventory/services.py::ship_delivery_order` |
| SPC-E02 | inventory absolute update | 强 | `apps/inventory/repository.py::update_inventory_stock_qty` |
| SPC-E03 | product delta update | 强 | `apps/inventory/repository.py::apply_product_stock_delta` |
| SPC-E04 | ledger 负 qty/new balance insert | 强 | `apps/inventory/repository.py::insert_inventory_ledger` |
| SPC-E05 | 缺 inventory 从 product stock 建基线 | 强 | `apps/inventory/repository.py::ensure_inventory_for_product` |
| SPC-E06 | 后续行失败直接 return，无 rollback | 强负向 | `apps/inventory/services.py` |
| SPC-E07 | DO status 与末尾 commit 顺序 | 强 | `apps/inventory/services.py` |
| SPC-E08 | inventory DDL product_id 非唯一 | 强负向 | `runtime/v14/legacy_support.py` |
| SPC-E09 | inventory 查 product 使用 LIMIT 1 | 强 | `apps/inventory/repository.py::fetch_inventory_by_product_id` |
| SPC-E10 | 既有权威页记录“三写” | 强交叉 | `../ship-complete-deepen/do_ship.md` |
| SPC-E11 | bootstrap 注入 cursor/conn，router 持有单例 page service | 强 | `bootstrap/application.py`、`apps/inventory/router.py` |
| SPC-E12 | SQLite adapter 配 busy_timeout/journal，但未配置 Ship 专用事务 | 强 | `core/database/adapters/sqlite.py` |

## UNKNOWN + 已查路径

1. **FastAPI 外层在 early return 后是否 close/rollback 当前 transaction UNKNOWN。** 已查：router dependencies、bootstrap deps、database adapter、repository factory。
2. **共享注入 conn 是否会把失败请求的前行 SQL 随后续请求 commit UNKNOWN。** 已查：bootstrap 注入、inventory route 单例 service、connection setup；未见 early-return rollback。
3. **生产 DB 是否开启 foreign_keys、WAL、busy_timeout UNKNOWN。** 已查：SQLite adapter/config、runtime initialization。
4. **历史 inventory 与 products 镜像漂移规模 UNKNOWN。** 已查：services/repository/reports；未读生产数据。
5. **重复 inventory product 行是否存在 UNKNOWN。** 已查：DDL 与查询；未读生产数据。
6. **产品 UPDATE 0 rows 时 SQLite rowcount 是否被外层监控 UNKNOWN。** 已查：repository/service、logging。
7. **commit 失败后的客户端重试策略 UNKNOWN。** 已查：Ship router/template、exception handlers、reports。
8. **浮点 qty 长期累积误差容忍度 UNKNOWN。** 已查：REAL 字段与 float 运算，未见精度政策。

## 交叉引用

- Ship 权威：[`../ship-complete-deepen/do_ship.md`](../ship-complete-deepen/do_ship.md)
- 库存台账：[`../inventory-deepen/stock_ledger.md`](../inventory-deepen/stock_ledger.md)
