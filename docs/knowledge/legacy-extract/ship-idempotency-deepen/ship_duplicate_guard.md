# Ship 幂等：应用层判重键 vs DB 唯一/锁

**Evidence strength:** Strong for application guard; strong negative for DB uniqueness/locking  
**结论：** Ship 使用两层顺序门：DO 状态阶段，以及 `inventory_ledger` 中 `trans_type='DO Ship' AND remark='DO-{do_no}'` 的计数。第二层是应用层“先查后写”，锚定可变业务号而非 DO id/attempt id；公开 DDL 没有唯一约束，库存更新没有条件 CAS、行锁或版本号，因此不能证明并发 exactly-once。

## 判重链

1. 读取 DO 的 `id/do_no/status/so_id`。
2. Shipped/Complete 直接返回 `already_shipped`。
3. 非 open 阶段返回 `bad_status`。
4. 查询同 `DO Ship + DO-{do_no}` 流水数量。
5. 数量大于零返回 `already_shipped`。
6. 逐行扣库存、扣产品镜像并插入同 remark 的流水。
7. 最后 DO→`已出库` 并 commit。

## 业务规则

| ID | 规则 |
|---|---|
| SDG-R01 | Ship 先要求 DO 存在。 |
| SDG-R02 | Shipped 或 Complete 阶段先由状态门拒绝。 |
| SDG-R03 | 只有 Pending/待出库/Pending Outbound 归入 open。 |
| SDG-R04 | 流水判重条件固定为 trans_type `DO Ship`。 |
| SDG-R05 | 流水关联值固定为 remark `DO-{do_no}`。 |
| SDG-R06 | 判重不使用 delivery_order id、SO id 或 shipment attempt id。 |
| SDG-R07 | 一个 DO 多行会生成多条同一判重键的流水；判重只要求 count>0。 |
| SDG-R08 | 无效行被跳过；即使零有效行，也会把 DO 写 Shipped。 |
| SDG-R09 | DO 状态更新发生在所有行循环之后。 |
| SDG-R10 | 所有 Ship SQL 依赖末尾 repository commit。 |
| SDG-R11 | 公开 ledger DDL 只有自增 id，无业务唯一键。 |
| SDG-R12 | inventory/product 更新未带旧余额条件或版本号。 |
| SDG-R13 | 未见 `BEGIN IMMEDIATE`、显式锁或 per-DO mutex。 |
| SDG-R14 | 两个并发请求理论上可同时通过 count=0，再分别过账。 |
| SDG-R15 | do_no 重用可能让不同 DO 相互误判；do_no 修改又可能绕过旧流水。 |
| SDG-R16 | Type A Human Confirm 与 RBAC 控制操作者，不提供数据库幂等性。 |
| SDG-R17 | 扫码 Ship 复用同 service，因此共享同一判重强弱。 |

## 应用层与数据库对照

| 控制 | 当前实现 | 保护范围 | 缺口 |
|---|---|---|---|
| 状态门 | stage open/shipped/complete | 顺序重复 | 状态与流水可失配 |
| ledger count | type + remark | 历史重复 | 先查后写竞态 |
| DB UNIQUE | 未观察到 | 无 | 并发重复 insert 可成立 |
| row lock | 未观察到 | 无 | 共享库存并发超卖 |
| CAS stock update | 未观察到 | 无 | 读取后绝对赋值 |
| transaction id | 未建模 | 无 | 无 shipment attempt 边界 |
| Human Confirm | POST 参数 | 人工意图 | 不防重放/并发 |

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| SDG-V01 | DO 必须存在 | Hard |
| SDG-V02 | 当前状态必须 open | Hard |
| SDG-V03 | 不得已有同 type+remark 流水 | Application hard |
| SDG-V04 | Type A POST 要 human_confirm=1 | Hard request gate |
| SDG-V05 | Delivery Orders edit 权限 | Hard route gate |
| SDG-V06 | ledger 业务键 DB 唯一 | Missing |
| SDG-V07 | DO id 必须进入幂等键 | Missing |
| SDG-V08 | do_no 必须唯一且不可变 | UNKNOWN |
| SDG-V09 | 并发请求必须串行 | Missing |
| SDG-V10 | 库存扣减必须原子 `stock>=qty` | Missing |
| SDG-V11 | Ship 必须至少有一条有效行 | Missing |
| SDG-V12 | 重放必须绑定 request/idempotency token | Missing |
| SDG-V13 | 判重与写流水必须同一原子语句/事务门 | 未显式证明 |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `delivery_orders.id` | Ship route 主键，但不进入 ledger 关联 |
| `delivery_orders.do_no` | 展示号，也是 remark 幂等来源 |
| DO status | 第一层顺序门 |
| `DO_OPEN` | Pending/待出库/Pending Outbound |
| `DO_SHIPPED` | 已出库/Shipped |
| `DO_COMPLETE` | Delivered/已完成 |
| `inventory_ledger.trans_type` | 交易类别，Ship 固定 `DO Ship` |
| `inventory_ledger.remark` | 文本说明兼任关联/判重键 |
| ledger count | count>0 即认为整个 DO 已 Ship |
| ledger `id` | 唯一技术键，不表达业务幂等 |
| `human_confirm` | Type A 人工确认位 |
| `already_shipped` | 状态或流水门共用错误 |
| shipment attempt | 未建模的一次过账尝试 |
| request id | 未建模的重放令牌 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| SDG-E01 | 状态门与 ledger count 顺序 | 强 | `apps/inventory/services.py::ship_delivery_order` |
| SDG-E02 | count SQL 只按 type+remark | 强 | `apps/inventory/repository.py::count_inventory_ledger_for_do` |
| SDG-E03 | 每行写相同 remark 的 ledger | 强 | `apps/inventory/services.py` |
| SDG-E04 | ledger DDL 无 UNIQUE/DO FK | 强负向 | `runtime/v14/legacy_support.py` |
| SDG-E05 | inventory 更新为绝对余额，无旧值条件 | 强 | `apps/inventory/repository.py::update_inventory_stock_qty` |
| SDG-E06 | product 镜像为无条件 delta update | 强 | `apps/inventory/repository.py::apply_product_stock_delta` |
| SDG-E07 | 全循环后才更新状态和 commit | 强 | `apps/inventory/services.py` |
| SDG-E08 | Type A POST 权限/人工确认 | 强 | `apps/inventory/router.py`、`templates/do_ship.html` |
| SDG-E09 | A-003 gate 验证的是静态行为，不建立 DB 唯一键 | 中等 | `docs/reports/Business_Strong_A003_Delivery_Report.md` |

## 并发窗口

`T1 count=0 → T2 count=0 → T1 read stock → T2 read stock → T1 三写 → T2 三写`

可能结果取决于连接与事务调度：重复 ledger、产品镜像双扣、inventory 丢失更新或数据库锁错误均未被当前业务层归一化处理。这里是静态可见风险，不宣称已在生产复现。

## UNKNOWN + 已查路径

1. **生产数据库是否被私有迁移加了 UNIQUE/index UNKNOWN。** 已查：runtime DDL、database patches、公开 scripts。
2. **do_no 是否有 DB 唯一约束且禁止修改 UNKNOWN。** 已查：delivery_orders DDL、Sales create DO、Inventory service。
3. **SQLite/目标 DB 的实际隔离级别和 busy timeout UNKNOWN。** 已查：database adapter、runtime connection/config。
4. **共享 cursor/connection 是否允许真实并发进入同 service UNKNOWN。** 已查：router configure、dependency binding、repository factory。
5. **外层 middleware 是否统一 BEGIN/rollback UNKNOWN。** 已查：core/router、database adapter、bootstrap。
6. **ledger count 是否应按行数与产品核对而非 count>0 UNKNOWN。** 已查：Ship service/repository、reports。
7. **历史 do_no 重用/修改数据是否存在 UNKNOWN。** 已查：创建编号规则与公开 schema；未读生产 DB。
8. **数据库锁错误如何呈现和重试 UNKNOWN。** 已查：Ship router/service、exception handlers、reports。

## 交叉引用

- Ship 权威：[`../ship-complete-deepen/do_ship.md`](../ship-complete-deepen/do_ship.md)
- 库存台账权威：[`../inventory-deepen/stock_ledger.md`](../inventory-deepen/stock_ledger.md)
