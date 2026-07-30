# 发货（Delivery Order）— Legacy Knowledge

**Evidence strength:** Strong（Sales 创建、Inventory 出库、Finance AR）  
**Chain role:** SO → DO Open → Ship → Complete；并行 DO → AR  
**Operational hub:** `/delivery_orders`  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

---

## 1. 范围

当前发货单不是模块规格中尚未落地的独立 Shipment 模块。运行事实由 Sales 创建 DO、Inventory 管理出库/完成/重开、Finance 可选形成 AR。承运商、跟踪号、POD/e-sign 未持久化。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外/缺口 | EAOS 重写备注 |
|----|----------|----------|-----------|---------------|
| D-R1 | 创建 DO 复制 SO 全部行，但不扣库存 | Create DO | 历史残留实现曾在创建时扣库存 | 仅 Ship 过账 |
| D-R2 | Sales 创建路径使用时间戳 DO 号、当天发货日期，并把 SO 置 Delivery Created | `/create_do` | 无服务端 RBAC | 单一路径 |
| D-R3 | Inventory 转换路径使用 SO ID 编号、SO 订单日期，不改 SO 状态 | `/convert_do` | 需 Sales Orders edit | 消除副作用差异 |
| D-R4 | 两种路径都把 DO 建为 Pending/Open 阶段 | Create | 同一 SO 可重复创建 | 定义拆单/合单规则 |
| D-R5 | Ship 仅允许开放阶段；已出库、已完成或存在相同出库台账时拒绝 | Ship | 幂等依赖台账字符串 | 唯一过账号 |
| D-R6 | Ship 同时扣库存记录、产品库存镜像并追加 `DO Ship` 台账 | Ship | 多写风险 | 单一库存过账 |
| D-R7 | 任一有效行库存不足时阻断 Ship | Ship | 零/负数量或无产品行被静默跳过 | 行级严格校验 |
| D-R8 | Ship 成功后 DO 置 Shipped；不立即更新 SO | Ship | SO 可能仍为 Delivery Created | 事件同步 |
| D-R9 | Complete 仅从 Shipped 进入 Delivered，同时把 SO 置 Delivered | Complete | GET 动作，无 Type A 人工门 | 使用命令与审计 |
| D-R10 | Reopen 仅从 Complete 回 Pending，并把 SO 改为 Open；不恢复库存 | Reopen | 与原 Delivery Created 不对称 | 显式冲销/退库 |
| D-R11 | Type A Ship 与 DO→AR 都要求人工确认 | POST action | Complete/Reopen 仅浏览器确认 | 统一高风险授权 |
| D-R12 | DO→AR 形成未收应收，`source_no` 使用 DO 号；不是税务发票 | Invoice approve | 未出库也可形成 AR | 决定计提时点 |
| D-R13 | 重复 AR 仅在 UI 警告，服务端仍可再次创建 | Invoice approve | | 以唯一约束阻断 |
| D-R14 | 收款仍以 SO 为对象，DO 详情只是链接回 SO 收款 | Receipt | AR 与 Receipt 并行 | 明确核销关系 |
| D-R15 | 非 Admin/Manager 的 DO 列表按 SO 业务员姓名过滤 | List | KPI 使用全局计数 | 报表与数据范围一致 |
| D-R16 | 删除 DO 在 UI 禁用；没有完整 cancel/reverse 服务 | Operations | | 用取消与冲销 |
| D-R17 | 扫码仓动作是第二个 Ship 入口，但复用同一出库服务 | Scan action | 自动选择开放 DO | 明确目标单据 |
| D-R18 | Complete 代表 Legacy 的送达确认 | Complete | 无承运商、跟踪或 POD 证据 | 不把状态等同物流证明 |

---

## 3. 流程

### 3.1 履约主链

1. Sales 或 Inventory 从 SO 创建 DO 并复制全部行。
2. DO 进入 Pending/Open；此时不扣库存，也不预留库存。
3. 仓管进入 Type A Ship 或扫码 Ship，人工确认。
4. 系统校验阶段、重复台账和逐行库存。
5. 成功后扣减库存、同步镜像、写出库台账，DO → Shipped。
6. Complete 将 DO 和 SO 都置为 Delivered。
7. Reopen 只回退状态；如要回补库存必须另做调整。

### 3.2 财务并行链

DO 任意阶段 → Type A Post AR → 建立未收应收 → 后续收款仍走 SO Receipt。

UI 会提示“尚未出库”和“已有 AR”，但这两项不是服务端硬阻断。

### 3.3 打印

Legacy 提供 DO 文档和装箱单打印预览。打印能力不等于承运、签收或 POD 数据已经存在。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| D-V1 | 创建时 SO 存在 | Hard | |
| D-V2 | Ship 仅限开放阶段 | Hard | |
| D-V3 | Ship 无既有同 DO 出库台账 | Hard | 应用层查重 |
| D-V4 | Ship 每行库存充足 | Hard | |
| D-V5 | Ship 可取得或建立库存记录 | Hard | |
| D-V6 | Complete 仅限 Shipped 且不可重复 | Hard | |
| D-V7 | Reopen 仅限 Complete | Hard | |
| D-V8 | Type A Ship/Invoice 要求 `human_confirm=1` | Hard | |
| D-V9 | Ship/Complete/Reopen 需 Delivery Orders edit | Hard | |
| D-V10 | Sales create_do 服务端权限 | Absent | |
| D-V11 | 创建 DO 要求 SO 已 Open | Absent | 任意状态可建 |
| D-V12 | 同一 SO 不得重复建 DO | Absent | |
| D-V13 | Post AR 不得重复 | Soft | 只有 UI 警告 |
| D-V14 | Post AR 前必须 Shipped | Soft | 只有 UI 警告 |
| D-V15 | Complete/Reopen 人工批准 | Weak | GET + 浏览器确认 |
| D-V16 | DO 行数量与产品有效 | Weak | 无效行可能静默跳过 |
| D-V17 | 列表 KPI 遵守用户数据范围 | Absent | 全局 KPI |

---

## 5. 数据含义

### 5.1 实体

| Entity | Meaning |
|--------|---------|
| `delivery_orders` | 发货/出库单头，关联 SO 与客户 |
| `delivery_order_items` | 从 SO 复制的产品、数量、价格和金额 |
| `inventory` | Ship 扣减的现存量 |
| `products.stock_qty` | 同步扣减的 Legacy 镜像 |
| `inventory_ledger` | `DO Ship` 出库事实和结余 |
| `ar_records` | 以 DO 号为来源的应收应计 |
| `receipts` | 以 SO 为对象的实收 |

### 5.2 创建路径差异

| Meaning | Sales create_do | Inventory convert_do |
|---------|-----------------|----------------------|
| DO 编号 | 时间戳 | SO ID 零填充 |
| 发货日期 | 创建当天 | SO 订单日期 |
| SO 状态 | Delivery Created | 不变 |
| 服务端权限 | 缺失 | Sales Orders edit |
| 跳转 | DO 详情 | DO 列表 |

### 5.3 状态词汇

| Stage | Canonical write | Accepted legacy values |
|-------|-----------------|------------------------|
| open | Pending | 待出库 / Pending Outbound |
| shipped | 已出库 | Shipped |
| complete | Delivered | 已完成 |
| other | — | 取消等未识别/无专用服务值 |

### 5.4 台账/AR 关联

| Field | Meaning |
|-------|---------|
| Ledger `trans_type` | `DO Ship` |
| Ledger `qty` | 出库为负 |
| Ledger `remark` | `DO-{do_no}`，兼作应用层幂等键 |
| AR `source_no` | DO 编号字符串；未见稳定 DO FK |
| AR `status` | 初始 Unpaid |

---

## 6. 诚实缺口与操作风险

- **双创建路径及残留旧实现：** 正常路由不在创建时扣库存，但残留代码与历史数据需要迁移核查。
- **无预留和部分发货：** DO 复制全量行；创建时不锁库存，也没有已发/待发行数量。
- **权限不一致：** Sales 创建入口缺服务端门；另一入口有权限校验。
- **状态与库存不对称：** Reopen 不回库存；手工 SO 状态也可能与 DO 不一致。
- **AR 软校验：** 未出库和重复 AR 均可在确认后继续。
- **运营数据缺失：** 承运商、跟踪号、POD、签收人未被记录。
- **KPI 越界：** 行列表按用户过滤，汇总卡片却可能展示全局数量。
- **Shipment 概念混淆：** `business_modules/shipment.md` 是未落地目标，不是当前 DO 权威。

---

## 7. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `apps/sales/services.py` / `router.py` | Sales 创建 DO | Strong |
| `apps/inventory/services.py` | 转换、Ship、Complete、Reopen、Type A | Strong |
| `apps/inventory/repository.py` | 出库台账、库存与状态访问 | Strong |
| `apps/inventory/router.py` | DO 路由、权限和扫码入口 | Strong |
| `apps/finance/services.py` / `router.py` | DO→AR 与 SO Receipt 交界 | Strong |
| `apps/platform/v14_residual.py` | 创建时扣库存的旧残留风险 | Medium |
| `templates/delivery_orders.html` | 列表、KPI、批量完成和删除禁用 | Strong UX evidence |
| `templates/delivery_order_detail.html` | 阶段动作与运营缺失说明 | Strong UX evidence |
| `templates/do_ship.html` / `do_invoice.html` | Type A 与 AR 非税票语义 | Strong |
| `business_modules/shipment.md` | 未落地 Shipment 边界 | Intent |
| `docs/reports/Business_Strong_A003_Delivery_Report.md` | 创建不扣库存和出库规则 | Strong |
| `docs/reports/Business_Strong_A009_Delivery_Ops_Report.md` | 发货运营诚实性 | Strong |
| `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | Type A 行为 | Strong |
| `docs/reports/V151E_Volume010_Finance_Inventory_Business_Chain_Extraction_Report.md` | 模块交界与迁移历史 | Strong historical |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
