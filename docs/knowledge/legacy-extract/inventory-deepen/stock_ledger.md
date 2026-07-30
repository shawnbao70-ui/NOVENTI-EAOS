# 库存台账、流水与过账时点

## Scope与证据强度

本页深化 `inventory`、`products.stock_qty` 和 `inventory_ledger` 的关系及实际过账时点。运行逻辑、DDL、模板与 A-002/A-018 报告形成强证据。概览交叉引用 [`../ops/inventory.md`](../ops/inventory.md)；DO、仓位与冲销缺口交叉引用 [`../fulfillment-deepen/`](../fulfillment-deepen/)，不复制其正文。

结论：台账是追加式变动记录，但库存数量仍由可更新余额表维护；台账不是通过重放自动生成余额。PO Receipt、DO Ship、Sample Receipt 和人工调整是已证过账路径。

## 业务规则（稳定ID）

1. **SL-R01** `inventory.stock_qty` 是库存操作页面的现存量；`products.stock_qty` 是旧产品路径的镜像量。
2. **SL-R02** 正常过账依次更新库存行、对产品镜像应用同量 delta、追加 `inventory_ledger`，最后提交事务。
3. **SL-R03** 台账 `qty` 以正数表示入库、负数表示出库；`balance_qty` 保存本次过账后的余额。
4. **SL-R04** 手工调整在提交时过账，类型默认 `Manual Adjustment`，也可由请求传入 Cycle Count、Damage Write-off 或 Transfer 标签。
5. **SL-R05** PO 建立、批准和开放不增加库存；`receive_purchase` 才以 `PO Receipt` 增加库存、写流水并将 PO 置 Received。
6. **SL-R06** PO 收货通过 `PO-{purchase_id}` 备注及同类流水计数防重复。
7. **SL-R07** DO 创建不扣库存；`ship_delivery_order` 才以 `DO Ship` 扣减库存、写流水并将 DO 置 Shipped。
8. **SL-R08** DO 出库以 `DO-{do_no}` 备注查重，并在过账前检查开放阶段和逐行库存充足。
9. **SL-R09** Sample materialize 在绑定产品且未过账时，以 `Sample Receipt` 增库存并使用 `SAMPLE-{id}` 备注。
10. **SL-R10** 缺少库存行时，收发路径可从 `products.stock_qty` 建立库存基线，安全库存为 0、location 为空。
11. **SL-R11** 库存页面流水按 id 倒序读取，产品详情最多显示最近 40 条，全局流水页最多读取 500 条。
12. **SL-R12** 删除库存行只允许现存量为零，且不删除历史流水。
13. **SL-R13** DO Complete 只改变履约状态；Reopen 也只回退状态，不自动冲销出库流水或恢复库存。
14. **SL-R14** 产品编辑仍可直接改 `products.stock_qty` 而不写库存和流水，构成镜像漂移旁路。
15. **SL-R15** 台账记录产品代码/名称快照及自由文本备注，但没有强外键、单据类型/ID分列或数据库唯一幂等键。

## 流程

### 人工调整过账

1. 读取库存行当前量。
2. 校验 delta 非零，并计算新余额。
3. 若新余额为负则拒绝。
4. 更新 `inventory.stock_qty`，同步产品 delta。
5. 追加类型、delta、结余、备注和当前时间。
6. 单次提交。

### 采购收货与发货出库

- PO：Open → 检查未收货/有行 → 各行增加库存、镜像与 `PO Receipt` → PO Received。
- DO：Open → 检查未出库/库存充足 → 各行减少库存、镜像与 `DO Ship` → DO Shipped。
- 建 PO/DO、批准、Complete 均不是数量过账时点。

### 样品入库

样品绑定产品后，materialize 检查 `Sample Receipt + SAMPLE-{id}` 未存在，再增加库存、同步镜像、写流水并更新样品状态。

## 校验（强/弱/缺失）

1. **SL-V01（强）** 手工调整 delta 不得为零。
2. **SL-V02（强）** 手工调整后余额不得为负。
3. **SL-V03（强）** PO 收货要求单据存在、处于开放阶段、有行项且无既有收货流水。
4. **SL-V04（强）** DO 出库要求单据存在、处于开放阶段、未有同 DO 流水且库存充足。
5. **SL-V05（强）** 样品入库要求样品存在、已绑定产品、数量有效且未有同样品流水。
6. **SL-V06（强）** 删除库存行要求现存量精确为零。
7. **SL-V07（弱）** PO/DO 幂等依赖“类型+备注”的先查后写，无数据库唯一约束。
8. **SL-V08（缺失）** 未见库存行 `product_id` 唯一约束，查询仅取第一条。
9. **SL-V09（缺失）** 未见库存与产品镜像定期对账或一致性约束。
10. **SL-V10（缺失）** 未见并发版本、原子条件更新或数据库锁防止超卖。
11. **SL-V11（缺失）** `trans_type` 服务端没有严格枚举白名单。
12. **SL-V12（缺失）** 页面 SQL 未见一致 tenant 过滤，租户隔离端到端未知。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `inventory.id` | 库存余额行标识 |
| `inventory.product_id` | 余额对应 SKU |
| `inventory.stock_qty` | 当前现存量 |
| `products.stock_qty` | Legacy 产品库存镜像 |
| `inventory_ledger.id` | 流水顺序标识；页面按其倒序 |
| `product_code` / `product_name` | 过账时产品标识/名称快照 |
| `trans_type` | 过账业务标签 |
| `qty` | 本次增减量，入正出负 |
| `balance_qty` | 本次过账后的现存量 |
| `remark` | PO/DO/样品引用或人工原因字符串 |
| `create_time` | 应用服务器生成的过账时间文本 |
| `PO Receipt` | 采购收货入库类型 |
| `DO Ship` | 履约发货出库类型 |
| `Sample Receipt` | 样品转库存入库类型 |
| `Manual Adjustment` | 无上游单据的人工差异调整 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| Draft | 单据草稿，不过账 |
| Open | PO/DO 可执行收货或发货 |
| Received | PO 已执行库存入账 |
| Shipped | DO 已执行库存出账 |
| Delivered / Complete | 履约完成，不再动库存 |
| Reopen | 状态回退，不冲销库存 |
| 过账 | 余额、镜像、流水的数量变更 |
| 幂等检查 | 以类型和备注查既有流水 |

## 证据表

| # | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| SL-E01 | 库存与流水 DDL 字段 | 强 | `runtime/v14/legacy_support.py` |
| SL-E02 | 调整同时写库存、产品镜像和流水 | 强 | `apps/inventory/services.py`、`repository.py` |
| SL-E03 | PO Receive 以正数过账并置 Received | 强 | `apps/procurement/services.py` |
| SL-E04 | DO Ship 检查库存并以负数过账 | 强 | `apps/inventory/services.py` |
| SL-E05 | PO/DO 以类型+备注计数做幂等判断 | 强 | `apps/procurement/repository.py`、`apps/inventory/repository.py` |
| SL-E06 | 样品以 Sample Receipt 过账一次 | 强 | `apps/sample/services.py`、`repository.py` |
| SL-E07 | 流水页展示类型、变动、结余、备注与时间 | 强 | `templates/inventory_ledger.html` |
| SL-E08 | 零库存才可删余额行且保留流水 | 强 | `apps/inventory/services.py` |
| SL-E09 | 产品维护可直接写产品库存 | 强（风险） | `apps/product/router.py`、`repository.py` |
| SL-E10 | A-002 报告验证调整双写与校验 | 强 | `docs/reports/Business_Strong_A002_Inventory_Report.md` |

## UNKNOWN + 已查路径

1. **库存与产品镜像谁是最终账面权威：UNKNOWN。** 已查路径：`apps/inventory/`、`apps/product/`、`business_modules/inventory.md`。
2. **多行 PO/DO 中途失败时是否由统一事务完整回滚：UNKNOWN。** 已查路径：采购/库存 service、repository 与连接提交点。
3. **历史流水是否允许更新/删除及其权限：UNKNOWN。** 已查路径：`apps/inventory/router.py`、repository、templates。
4. **流水备注能否稳定关联单据重编号/删除后的业务对象：UNKNOWN。** 已查路径：PO/DO/样品幂等查询和 DDL。
5. **租户隔离是否覆盖全部库存读写：UNKNOWN。** 已查路径：`apps/inventory/`、`apps/procurement/`、tenant schema migration。
6. **生产领料、完工入库是否写同一流水：UNKNOWN。** 已查路径：`apps/production/`、`apps/inventory/`、全库 movement type 检索。
7. **退货/冲销的专用反向过账类型：UNKNOWN。** 已查路径：`apps/inventory/`、`apps/sales/`、`apps/procurement/`、fulfillment-deepen。
8. **历史数据是否存在旧 DO 直接改产品库存但无流水：UNKNOWN。** 已查路径：A-002/Volume010 报告、旧 delivery 路径。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
