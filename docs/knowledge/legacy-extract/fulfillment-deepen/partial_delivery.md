# 分批 / 部分发货 — Legacy Deep Extract

**Evidence strength:** Strong（SO→DO 全量复制、整 DO Ship）/ Strong negative（无累计履约）/ Missing（分批计划与剩余量控制）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件调查同一销售订单分多批交付、单行部分发货、累计已发和剩余量。Legacy 确实允许一个 SO 详情装配多张 DO，也未阻止重复创建；但两个创建入口都会复制 SO 全部行，没有用户输入本批数量、累计 delivered qty 或 remaining qty。运行能力是“可产生多张全量 DO”，不是受控的 partial delivery。

**硬门槛计数：** 规则 16；校验 8；数据含义 14；证据 12；`UNKNOWN + 已查路径` 7。

## 2. 业务规则（稳定 ID，13 条）

| ID | 规则 | 证据强度 |
|---|---|---|
| PARTIAL-DELIVERY-RULE-001 | SO 详情按 so_id 读取并展示多张关联 DO | Strong |
| PARTIAL-DELIVERY-RULE-002 | `/create_do/{so_id}` 创建 DO 时复制该 SO 全部行 qty/price/amount | Strong |
| PARTIAL-DELIVERY-RULE-003 | `/convert_do/{so_id}` 旧入口也复制全部 SO 行 | Strong |
| PARTIAL-DELIVERY-RULE-004 | 未见任一入口接受“本批数量”或行选择 | Strong negative |
| PARTIAL-DELIVERY-RULE-005 | 未见创建前检查该 SO 已有 DO 或累计已发数量，因此可重复生成全量 DO | Strong negative |
| PARTIAL-DELIVERY-RULE-006 | DO Ship 对当前 DO 全部正数量行统一扣库，没有单行 Ship 操作 | Strong |
| PARTIAL-DELIVERY-RULE-007 | 当前 DO 的幂等只按 do_no 台账控制，不跨同 SO 的其他 DO 汇总 | Strong |
| PARTIAL-DELIVERY-RULE-008 | Create DO 后 SO 状态写 `Delivery Created`，不表达 partially delivered 比例 | Strong |
| PARTIAL-DELIVERY-RULE-009 | 任一 DO Complete 都会把关联 SO 状态写 `Delivered` | Strong |
| PARTIAL-DELIVERY-RULE-010 | Reopen 任一 completed DO 会把关联 SO 改回 `Open`，不检查其他 DO | Strong |
| PARTIAL-DELIVERY-RULE-011 | Delivery list 的“batch complete”仅对 shipped DO 逐张完成，不是分批发货建模 | Strong |
| PARTIAL-DELIVERY-RULE-012 | 包装 carton 是逐行占位，不是批次/箱级分配 | Strong negative |
| PARTIAL-DELIVERY-RULE-013 | partial delivery policy、容差、尾差关闭和 backorder 均为 `UNKNOWN` | Missing |
| PARTIAL-DELIVERY-RULE-014 | AI `fulfillment:partial` 由同一 SO 下 closed/open DO 头数量推断，不读取行级已发 qty | Derived intelligence |
| PARTIAL-DELIVERY-RULE-015 | NDE 的 `delivered_qty` 是当前 DO 行 qty 的打印别名，不是跨 DO 累计字段 | Document-only |
| PARTIAL-DELIVERY-RULE-016 | Canonical 与 v14 residual 曾有创建时点差异；生产数据是否受旧“创建即扣产品库存”路径影响为 `UNKNOWN` | Historical risk |

## 3. 流程

### 3.1 实际流程

1. SO 保存固定订单行 qty。
2. 用户从 SO 触发 Create DO。
3. 系统复制全部 SO 行和订单总额到新 DO，并把 SO 标为 `Delivery Created`。
4. 用户执行整张 DO Ship；系统逐行扣减 qty。
5. 用户执行 Complete；DO → Delivered，SO → Delivered。
6. SO 详情可显示多张 DO，但不计算其累计数量。

### 3.2 重复 DO 风险路径

1. 对同一 SO 再次触发 Create/Convert DO。
2. 系统再次复制完整行；未见 remaining qty 限制。
3. 如果库存足够，第二张 DO 也可 Ship。
4. 每张 DO 仅以自身 do_no 幂等，无法阻止跨 DO 超出 SO qty。

受控流程 `选择未交数量 → 建本批行 → 累计 shipped → 余量/backorder → 全量完成` 为 `UNKNOWN`。

## 4. 校验（8 条）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| PARTIAL-DELIVERY-VAL-001 | 创建 DO 前 SO 必须存在 | 强 | 不存在返回/重定向 |
| PARTIAL-DELIVERY-VAL-002 | DO 创建权限 | 强 | 入口使用 Sales Orders edit 或 Delivery Orders add 相关门禁 |
| PARTIAL-DELIVERY-VAL-003 | 本批 qty > 0 且 ≤ SO remaining | 缺失 | 无本批输入/remaining |
| PARTIAL-DELIVERY-VAL-004 | 同一 SO 不得重复全量建 DO | 缺失 | 未见 existing DO 阻断 |
| PARTIAL-DELIVERY-VAL-005 | Ship 时每行库存足够 | 强 | 逐行 on-hand 校验 |
| PARTIAL-DELIVERY-VAL-006 | 同一 DO 不得重复 Ship | 强 | 状态 + ledger 判重 |
| PARTIAL-DELIVERY-VAL-007 | SO Delivered 必须所有行累计完成 | 缺失 | 任一 DO complete 即更新 SO |
| PARTIAL-DELIVERY-VAL-008 | 多 DO 完成/重开的一致性 | 缺失 | 未汇总其他 DO 状态 |

## 5. 数据含义（12 项）

| 数据 | 业务含义 |
|---|---|
| `sales_orders.id` | 分批履约的上游订单标识 |
| `sales_orders.status` | 当前订单标签；不是累计履约指标 |
| `sales_order_items.qty` | 原订单行数量 |
| `delivery_orders.id` | 单张交付单标识 |
| `delivery_orders.so_id` | DO 所属 SO；允许查询多张 |
| `delivery_orders.do_no` | DO 业务编号，也是 Ship ledger remark 的组成 |
| `delivery_orders.status` | 当前 DO 阶段 |
| `delivery_orders.total_amount` | 创建时复制 SO 总额，不按本批重新计算 |
| `delivery_order_items.qty` | 当前 DO 行数量；创建时等于 SO 行 qty |
| `inventory_ledger.qty` | Ship 的实际负数库存变动 |
| AI `fulfillment:partial` | 基于 DO 头 open/closed 组合的推断标签，不是 DB 履约状态 |
| NDE `delivered_qty` | 当前打印 DO 行 qty 的显示映射 |
| delivered/remaining/backorder qty | `UNKNOWN`；无字段 |
| carton/batch/lot | 页面 carton 为行占位；未见持久批次语义 |

## 6. 状态词汇

| 词汇 | 含义/限制 |
|---|---|
| Delivery Created | 已产生 DO；不说明交付比例 |
| Pending / 待出库 | DO 尚未 Ship |
| 已出库 / Shipped | 整张 DO 已扣库 |
| Delivered / 已完成 | DO 已完成；会直接同步 SO |
| Open | SO 审批或 DO reopen 后状态 |
| Partial | SO 页面只确认 payment_status 可见该词；不是 delivery status |
| fulfillment:欠交 / in_flight / partial / shipped | AI 推断词汇；以 DO 单据数量/状态分类 |
| Partially Shipped / Backordered | `UNKNOWN`；未见运行词汇 |

## 7. 证据表（10 项）

| Evidence | Path | 观察 | 强度 |
|---|---|---|---|
| E-PD-001 | `apps/sales/services.py::create_delivery_order` | 全量复制 SO 行 | Strong |
| E-PD-002 | `apps/inventory/services.py::_legacy_convert_do` | 第二入口同样全量复制 | Strong |
| E-PD-003 | `apps/sales/repository.py::fetch_delivery_orders_by_so` | SO 可装配多 DO | Strong |
| E-PD-004 | `apps/inventory/services.py::ship_delivery_order` | 按当前 DO 全部行扣库 | Strong |
| E-PD-005 | `apps/inventory/services.py::_legacy_complete_do` | 单 DO 完成即 SO Delivered | Strong |
| E-PD-006 | `apps/inventory/services.py::_legacy_reopen_do` | 单 DO 重开即 SO Open | Strong |
| E-PD-007 | `templates/sales_order_detail.html` | Delivery tab 列 DO 数，不显示累计 qty | Strong |
| E-PD-008 | `templates/delivery_order_detail.html` | 只显示 DO qty/on-hand，无 remaining | Strong |
| E-PD-009 | `runtime/v14/legacy_support.py` | DO item schema 无 delivered/remaining | Strong |
| E-PD-010 | `docs/reports/Business_Strong_A009_Delivery_Ops_Report.md` | batch complete 只处理 shipped DO | Strong corroboration |
| E-PD-011 | `v15/ai_operating_depth/semantics.py` | partial 由 DO 头 open/closed 组合推断 | Intelligence-only |
| E-PD-012 | `document/nde_engine.py` | delivered_qty 映射为当前 DO item qty | Document-only |

## 8. UNKNOWN + 已查路径（7 项）

| UNKNOWN | 已查路径 |
|---|---|
| SO 行级累计 delivered qty | `apps/sales/**`；`apps/inventory/**`；`runtime/v14/legacy_support.py` |
| 创建 DO 时选择本批行/数量 | `templates/sales_order_detail.html`；`templates/new_sales_order.html`；sales/inventory routers |
| remaining qty 与 backorder 实体 | sales/inventory repositories；`business_modules/sales.md`；`shipment.md` |
| 部分交付状态和自动完成阈值 | sales/inventory services；delivery templates；docs/reports A-003/A-009 |
| 超交、短交、尾差容忍规则 | `apps/inventory/**`；`apps/sales/**`；`docs/reports/**Delivery*` |
| 多 DO 并发创建与跨 DO 幂等键 | sales/inventory repositories；database schema；runtime v14 |
| 批次、序列号、箱号与本批追溯 | delivery templates；inventory schema；warehouse/object360 runtime docs |

## 9. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sales_order_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\delivery_orders.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\delivery_order_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\sales.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\shipment.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A003_Delivery_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A009_Delivery_Ops_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V18_SO_DO_Invoice_TypeA_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ai_operating_depth\semantics.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ai_operating_depth\forewarn.py`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
