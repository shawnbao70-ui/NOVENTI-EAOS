# 销售订单建立发货单（SO → DO）— Legacy Knowledge

**Evidence strength:** Strong for active Sales create path and Inventory ship boundary; mixed for duplicate route behavior  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块描述从 SO 建立 Delivery Order 的 header/line 复制、SO `Delivery Created` 状态写入，以及为何创建 DO 时不扣库存。创建与发货是两个独立动作：创建生成待发货指令；Inventory Ship 才验证库存、写库存与台账并改变 DO 状态。

活动 Sales create path 与 Inventory ship path证据强；另有 Inventory legacy convert 路径，编号、权限、重定向和 SO 状态写入并不完全相同，运行优先级需结合路由挂载。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| SD-R1 | 建 DO 以已存在 SO 为输入 | SO 不存在返回 404 |
| SD-R2 | 活动 Sales 路径创建 DO header 并复制全部 SO items | DO 是履约快照 |
| SD-R3 | DO 客户、总额来自 SO header | 不从报价重新读取 |
| SD-R4 | DO 初始状态为 `Pending` | 表示待出库 |
| SD-R5 | 活动 DO 编号使用当前时间到秒 | 同秒并发碰撞风险未证实有唯一保护 |
| SD-R6 | 创建完成后 SO 状态写为 `Delivery Created` | 仅履约标签变化 |
| SD-R7 | 创建 DO 不减少 `inventory.stock_qty` | 库存离库发生在 Ship |
| SD-R8 | 创建 DO 不写 inventory ledger | 无库存过账事实 |
| SD-R9 | 创建 DO 不要求 SO 已 `Open` | Pending、Cancelled、Delivered 等未见服务端 gate |
| SD-R10 | 创建 DO 不要求 SO 有行 | 可生成空 DO |
| SD-R11 | 创建 DO 不检查库存可用量 | 允许先建立待发货任务 |
| SD-R12 | 活动 Sales route 本身未见权限检查 | 模板按 Delivery Orders add 隐藏按钮但可直链 |
| SD-R13 | 活动路径未查已有 DO | 同一 SO 可重复创建多个 DO |
| SD-R14 | 每次重复创建都会把 SO 写回 `Delivery Created` | 不能表示 DO 数量或完成度 |
| SD-R15 | Inventory legacy convert 路径要求 Sales Orders edit | 与活动 route 的 UI 权限语义不一致 |
| SD-R16 | legacy convert 使用 `DO` + SO ID 编号并保留 SO order_date | 与时间编号路径不同 |
| SD-R17 | Ship 才要求 DO 为 open、库存存在且足够 | 发货具备更强服务端门槛 |
| SD-R18 | Ship 写 inventory、products 镜像和 inventory ledger | 属于库存双写边界 |
| SD-R19 | Ship 防重复同时检查 DO stage 和 DO ledger remark | 创建 DO 不具备对应防重 |
| SD-R20 | Complete 在 Shipped 后将 DO 置 Delivered 并把 SO 置 Delivered | 与创建阶段分离 |
| SD-R21 | Reopen 只改状态，不恢复库存 | 库存恢复需另走调整 |
| SD-R22 | EAOS 不得把 `Delivery Created` 解读为库存已承诺或已扣 | Legacy 无 reservation 事实 |
| SD-R23 | 只有 canonical `/create_do` 写 SO `Delivery Created` | legacy `/convert_do` 建 DO 后不更新 SO |
| SD-R24 | Complete 必须在 Shipped 之后，成功后联动 SO 为 `Delivered` | 该顺序比 Create DO 阶段严格 |
| SD-R25 | Post AR 是 DO Invoice Type A 的后续独立动作 | DO 创建本身不写 `ar_records` |

---

## 3. Process

### 3.1 活动 Sales create DO

1. 按 SO ID 读取订单；不存在返回 404。
2. 生成时间型 DO number。
3. 复制 customer、当前日期、SO total，建立 `Pending` DO。
4. 读取全部 SO items 并逐行复制为 delivery items。
5. 不触碰库存和 inventory ledger。
6. 将 SO status 写成 `Delivery Created`，提交并进入 DO 详情。

### 3.2 后续 Ship

1. Delivery Orders edit 权限进入 Ship/Type A 表面。
2. Human Approved 后要求 DO 为 open 且未有出库 ledger。
3. 逐行确保库存记录存在、数量充足。
4. 扣减 inventory 与 products 镜像，并写 `DO Ship` ledger。
5. DO 状态变为已出库；Complete 是后续独立动作。

### 3.3 重复与失败边界

创建阶段未硬拦重复、空行、非 Open SO 或库存不足。多行 Ship 在单一最终 commit 前逐行写，但未观察到显式 rollback 包装；中途失败的原子性需进一步证实。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| SD-V1 | SO 必须存在 | Hard | 不存在 404 |
| SD-V2 | 创建者必须有 Delivery Orders add | UI only / route missing | 可直链风险 |
| SD-V3 | SO 必须已 Open | Missing | 无状态 gate |
| SD-V4 | SO 不得 Cancelled/Delivered | Missing | 无反向 gate |
| SD-V5 | SO 必须至少一行 | Missing | 空 DO 可创建 |
| SD-V6 | 同一 SO 不得重复建 DO | Missing | 无 existing check |
| SD-V7 | DO number 必须唯一 | UNKNOWN | 时间到秒生成 |
| SD-V8 | 创建时库存必须足够 | Intentionally deferred | Ship 才检查 |
| SD-V9 | Ship 必须 open | Hard downstream | 非 open 拒绝 |
| SD-V10 | Ship 不得重复 | Hard downstream | stage + ledger 双门 |
| SD-V11 | 每行 product/qty 必须有效 | Partial | Ship 跳过非正 qty |
| SD-V12 | Ship 库存必须存在且足够 | Hard downstream | 不足停止 |
| SD-V13 | DO header 总额必须等于行合计 | Missing | 复制 header 无重算 |
| SD-V14 | 创建、行复制、SO 状态必须原子 | Mixed | 最终 commit，但内部状态方法先 commit |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `delivery_orders.so_id` | DO 的来源 SO 引用 |
| `delivery_orders.do_no` | 路径相关的时间型或 SO-ID 型编号 |
| `delivery_orders.customer_id` | 从 SO 复制的客户 |
| `delivery_orders.delivery_date` | 活动路径创建日期；legacy 路径可用 SO 日期 |
| `delivery_orders.total_amount` | 从 SO header 复制的商业金额 |
| `delivery_orders.status='Pending'` | 待出库，不是已扣库存 |
| `delivery_order_items` | SO item 的创建时履约快照 |
| `sales_orders.status='Delivery Created'` | 至少执行过一次活动 create DO |
| legacy `/convert_do` | 可建立 DO 但不写 SO `Delivery Created` 的平行入口 |
| `inventory.stock_qty` | Ship 时才减少的主库存事实 |
| `products.stock_qty` | Ship 同步减少的镜像库存 |
| `inventory_ledger.trans_type='DO Ship'` | 实际出库过账证据 |
| ledger remark | 以 DO number 标识，参与重复 Ship 检测 |
| DO stage `open` | Pending/待出库/Pending Outbound |
| DO stage `shipped` | 已出库/Shipped |
| DO stage `complete` | Delivered/已完成 |
| reservation | UNKNOWN / 未观察到创建 DO 时预留库存 |

---

## 6. State Vocabulary

| Value / family | Meaning / caveat |
|----------------|------------------|
| `Delivery Created` | SO 已建 DO 标签，不代表唯一 DO |
| Pending / 待出库 / Pending Outbound | DO open family |
| 已出库 / Shipped | 已执行库存离库 |
| Delivered / 已完成 | DO complete family |
| Open | SO Approve 或 DO reopen 后的 SO 标签 |
| `DO Ship` | inventory ledger 过账类型 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 两个 create/convert DO 路径哪个在运行时先匹配 | sales/inventory routers、runtime bootstrap、route reports |
| `delivery_orders.so_id` 是否有唯一约束 | runtime schemas、database migrations、repository |
| 时间到秒 DO number 是否有唯一索引与碰撞处理 | sales service、DDL、error handling |
| 业务是否允许一个 SO 多个 DO/分批发货 | sales/inventory templates、business modules、reports |
| `Delivery Created` 在多 DO 情况下如何表达部分履约 | sales status logic、delivery reports |
| 空 DO 是否有后续补行入口 | inventory services/templates/routes |
| 创建 DO 是否应做库存 reservation | inventory/product schemas、ledger、reports |
| 活动 `/create_do` 缺权限门是否由外层 middleware 补足 | sales router、bootstrap、permission reports |
| Ship 多行中途失败是否自动 rollback | database context、inventory repository/service |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | 活动 create DO、行复制和 SO 状态写入 |
| `apps/sales/repository.py` | DO/header/items 持久化 |
| `apps/sales/router.py` | `/create_do` 无路由权限门 |
| `apps/inventory/services.py` | legacy convert、Ship、Complete、Reopen |
| `apps/inventory/repository.py` | 库存、产品镜像、ledger 写入 |
| `apps/inventory/router.py` | Delivery 权限与 Ship/Complete 路由 |
| `apps/inventory/v14_residual.py` | 残留 DO 路由边界 |
| `runtime/v14/residual_loader.py` | residual namespace 与 legacy 路由装载 |
| `templates/sales_order_detail.html` | Create DO UI 仅按 add 权限显示 |
| `templates/sales_orders.html` | 行动作和批量单选表面 |
| `templates/delivery_order_detail.html` | DO stage 与 Ship 操作 |
| `templates/do_ship.html` | Human Approved Ship 表面 |
| `business_modules/sales.md` | SO 所有权与下游 |
| `business_modules/product.md` | 库存产品边界 |
| `docs/reports/Business_Strong_A009_Delivery_Ops_Report.md` | Delivery 活动事实审计 |
| `docs/reports/Business_Strong_A003_Delivery_Report.md` | 创建与库存扣减边界 |
| `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | SO→DO→Ship Type A 设计 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
