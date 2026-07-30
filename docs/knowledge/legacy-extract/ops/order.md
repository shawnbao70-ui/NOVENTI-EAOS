# 订单（Sales Order）— Legacy Knowledge

**Evidence strength:** Strong（Sales 页面服务与持久化）/ Medium（残留路径与增强层）  
**Domain identity:** Sales owns `sales_orders` / `sales_order_items`  
**Chain role:** Quotation → Sales Order → Delivery Order → Inventory Ship；Receipt 与 AR 并行  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

---

## 1. 范围

本文件聚焦订单运营交界，不重复 CRM 报价细节。当前权威转单路径位于 `apps/sales`；代码库仍保留旧转单实现，但正常挂载顺序会优先使用 Sales 路由。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外/缺口 | EAOS 重写备注 |
|----|----------|----------|-----------|---------------|
| O-R1 | 同一报价只创建一个销售订单 | Quote convert | 应用层查重 | 数据库唯一约束 |
| O-R2 | SO 编号由 `SO` 加零填充报价 ID 构成 | Convert | 与独立号段无关 | 使用编号服务 |
| O-R3 | 转单复制客户、业务员、报价日期、总金额和全部报价行 | Convert | 允许空行转单 | 转单前校验完整性 |
| O-R4 | 转单后履约状态为待处理，收款状态为未收 | Convert | 存储值受中英文/i18n 影响 | 规范枚举 |
| O-R5 | 转单把报价状态写为中文“已确认” | Convert | 与 Quote Sent/Won 不一致 | 定义单一报价状态机 |
| O-R6 | 权威转单会尽力复制需求/商机追溯链接 | Convert | 失败被静默忽略；旧路径无此动作 | 在同一事务内保证 |
| O-R7 | 转单时可按业务员等级和订单金额计提待处理佣金 | Convert | 缺业务员或异常时静默跳过 | 领域事件驱动 |
| O-R8 | 非 Admin/Manager 的列表按业务员姓名等于会话用户名过滤 | List | 姓名不是稳定身份键 | 使用主体 ID 与数据范围 |
| O-R9 | 新建订单表单实际仍要求选择报价，提交后进入转单；表单业务员字段不生效 | New SO | 业务员取报价值 | 删除装饰字段 |
| O-R10 | V18 订单审批要求待处理阶段、至少一行和人工确认；成功后状态 Open | Approve | 与转单分离 | 明确批准与建单边界 |
| O-R11 | Open 快捷状态会进入审批页；其他状态字符串可直接写入 | Status change | 无完整状态白名单 | 状态机命令 |
| O-R12 | Sales `create_do` 复制全部订单行、将 SO 标为 Delivery Created，但不扣库存 | Create DO | 无重复 DO 校验、无服务端 RBAC | 单一履约编排 |
| O-R13 | Inventory `convert_do` 也可建 DO，但编号、日期和 SO 副作用不同 | Convert DO | 需 Sales Orders edit；不更新 SO | 合并双入口 |
| O-R14 | 创建 DO 不检查库存；仅 Ship 时由 Inventory 校验并扣减 | Ship | 短缺不会自动触发采购 | 预留/补货策略另建 |
| O-R15 | DO Ship 不更新 SO；DO Complete 才把 SO 标为 Delivered；Reopen 又把 SO 改为 Open | Fulfillment | 与 Delivery Created 不对称 | 事件驱动的同步状态 |
| O-R16 | 实收按 SO 写入 receipts 并更新收款镜像；DO 可另行形成 AR 应计 | Finance actions | 两条链无自动互斥 | 明确应计、实收与核销 |
| O-R17 | SO 硬删除在 UI 中禁用，取消依赖状态 | Operations | 任意状态写入仍较弱 | 取消命令和留痕 |
| O-R18 | 采购模块不直接读取或写入 SO | Stock shortage | 只能通过 Inventory 间接关联 | 保持域解耦 |

---

## 3. 流程

### 3.1 报价转订单

1. 校验报价存在。
2. 校验该报价尚无销售订单。
3. 建订单头、复制报价行。
4. 尝试佣金计提和生命周期追溯。
5. 报价置“已确认”，订单进入待处理履约阶段。

转单服务端不要求报价已 Sent/Won/Approved。

### 3.2 订单履约

待处理订单 → Type A Approve → Open → 创建 DO（不扣库存）→ Inventory Ship（扣库存）→ DO Complete → SO Delivered。

现存偏差：

- Sales 与 Inventory 各有一个 DO 创建入口。
- 同一 SO 可创建多张 DO。
- Ship 不回写 SO，Complete 才回写。
- 用户仍可直接写部分 SO 状态，可能与 DO 状态不一致。

### 3.3 财务交界

- **Receipt:** 以 SO 为对象，代表实收并维护 Paid/Partial 等状态。
- **DO → AR:** 以 DO 编号形成应收应计，不是税务发票。
- 订单详情按 receipts 实时求和，列表/KPI 可能读取 SO 头的已收与余额镜像。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| O-V1 | 报价存在 | Hard | |
| O-V2 | 同一报价无既有 SO | Hard | 仅应用层 |
| O-V3 | SO Approve 仅限待处理阶段 | Hard | |
| O-V4 | SO Approve 至少一行 | Hard | |
| O-V5 | SO Approve 要求 `human_confirm=1` | Hard | |
| O-V6 | 列表/详情/状态编辑 RBAC | Mixed | convert/new/create_do 缺服务端硬门 |
| O-V7 | 详情访问再次校验订单归属 | Absent | 列表过滤不能保护按 ID 直访 |
| O-V8 | 转单要求 Quote 已批准 | Absent | |
| O-V9 | 状态转移白名单 | Weak | Open 之外可写任意字符串 |
| O-V10 | 集中订单校验器 | Absent | validator 是空占位 |
| O-V11 | 同一 SO 不可重复创建 DO | Absent | |
| O-V12 | 创建 DO 前库存可用 | Absent by design | Ship 时才校验 |
| O-V13 | DO Ship 库存与幂等 | Hard | Inventory 负责 |
| O-V14 | 列表余额与详情余额一致 | Weak | 头镜像 vs receipts 汇总 |

---

## 5. 数据含义

### 5.1 实体

| Entity | Meaning |
|--------|---------|
| `sales_orders` | 报价转单后的商业订单头 |
| `sales_order_items` | 产品、数量、售价和金额 |
| `tc_ledger` | 转单形成的待处理佣金计提 |
| `delivery_orders` / items | 下游履约单及复制行 |
| `receipts` | SO 维度实收 |
| `ar_records` | DO 维度应收应计 |

### 5.2 关键字段

| Field | Meaning |
|-------|---------|
| `so_no` | Legacy 销售订单号 |
| `quote_id` | 源报价 |
| `customer_id` | 售达客户 |
| `salesperson_id` | 报价继承的订单归属 |
| `order_date` | 报价日期复制值 |
| `total_amount` | 报价总额复制值 |
| `status` | 履约状态，受 Sales 与 Inventory 共同影响 |
| `payment_status` | Finance 维护的收款状态 |
| `received_amount` / `balance_amount` | 头上的实收和余额镜像 |
| `requirement_id` / `opportunity_id` | 可选上游追溯 |

### 5.3 状态词汇

| Value / family | Stage | Meaning |
|----------------|-------|---------|
| Pending / 待发货 / 空 | pending | 转单后待批准/履约 |
| Open | open | 人工批准 |
| Delivery Created | pending-like | 已创建 DO |
| 已发货 / Shipped | shipped | 已发货；不一定由 DO 自动同步 |
| 已完成 / Completed / Delivered | complete | 履约完成 |
| 已取消 / Cancel* | cancelled | 取消 |

Payment 并存 Uncollected/未收款、Unpaid、Partial、Paid。

---

## 6. 诚实缺口

- **双 DO 创建入口：** 编号、日期、权限、跳转和 SO 状态副作用不同。
- **权限空洞：** 转单和 Sales 建 DO 依赖 UI 门控，服务端路由未见同等校验。
- **所有权空洞：** 列表过滤后，详情未复验同一数据范围。
- **状态可漂移：** SO 可手工改状态，DO Ship/Complete 又有另一套状态机。
- **余额双源：** SO 头镜像和 receipts 汇总可能不一致。
- **Quote 门缺失：** 转单不受 Quote Approve 的硬约束。
- **采购零耦合：** 缺货只会在 Ship 失败，不自动生成补货或采购需求。

---

## 7. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `apps/sales/services.py` | 转单、审批、佣金、建 DO | Strong |
| `apps/sales/repository.py` | SO/DO 持久化与列表数据 | Strong |
| `apps/sales/router.py` | 路由和权限分布 | Strong |
| `apps/sales/validator.py` | 空校验器缺口 | Strong gap evidence |
| `apps/quotation/quote_pages.py` | 残留重复转单 | Medium |
| `apps/inventory/services.py` / `router.py` | 第二 DO 入口及履约状态 | Strong |
| `apps/finance/services.py` | Receipt、付款状态与 AR 交界 | Strong |
| `v15/business_lifecycle/workflow.py` | 报价到订单追溯 | Medium |
| `templates/sales_orders.html` / `sales_order_detail.html` | 运营入口与状态行为 | Medium |
| `templates/so_approve.html` | Type A 人工门 | Strong UX evidence |
| `business_modules/sales.md` | Sales 边界意图 | Intent |
| `docs/reports/Business_Strong_A012_SO_Ops_Report.md` | SO 操作诚实性 | Strong |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | Sales 迁移与边界 | Strong historical |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
