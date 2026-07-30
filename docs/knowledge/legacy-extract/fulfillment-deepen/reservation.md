# 库存预留 / 占用 / 释放 — Legacy Deep Extract

**Evidence strength:** Strong（on-hand、DO Ship 扣减、台账幂等）/ Strong negative（无 reservation model）/ Missing（占用释放与并发保证）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件调查 Sales Order、Delivery Order 与 Inventory 之间是否存在库存预留、占用、释放和 available-to-promise。运行证据显示库存权威字段是 `inventory.stock_qty`；SO 审批、SO→DO 创建都不形成占用，DO 到 Ship 才检查现存量并扣减。`business_modules/inventory.md` 中 “Sales → stock reservation” 与 “Define reservation contract” 属边界意图/未来重构项，不是运行实现。

**硬门槛计数：** 规则 14；校验 8；数据含义 11；证据 12；`UNKNOWN + 已查路径` 7。

## 2. 业务规则（稳定 ID，12 条）

| ID | 规则 | 证据强度 |
|---|---|---|
| RESERVATION-RULE-001 | Legacy 运行库存以 `inventory.stock_qty` 表示 on-hand，未见 reserved/allocated/available 字段 | Strong negative |
| RESERVATION-RULE-002 | SO 从报价转换时复制数量、金额并进入待交付状态，但不查询或占用库存 | Strong |
| RESERVATION-RULE-003 | SO Human Approve 只把合格 pending 状态改为 `Open`，不做库存承诺 | Strong |
| RESERVATION-RULE-004 | 创建 DO 时复制 SO 全部行；A-003 后明确不在创建时扣减库存 | Strong |
| RESERVATION-RULE-005 | DO Ship 是首个强制库存检查点：逐行要求 on-hand ≥ DO qty | Strong |
| RESERVATION-RULE-006 | Ship 成功同时更新 inventory、镜像 products.stock_qty，并写 `DO Ship` 负数台账 | Strong |
| RESERVATION-RULE-007 | 同一 DO 以 `trans_type='DO Ship' + remark='DO-{do_no}'` 判重，已出库或已完成也拒绝再次 Ship | Strong |
| RESERVATION-RULE-008 | 安全库存仅用于 `stock_qty <= safe_stock` 的告警；Ship 不保留 safety stock 下限 | Strong |
| RESERVATION-RULE-009 | Open DO 查询只是为扫描动作寻找某产品最近一张待出库 DO，不产生占用 | Strong |
| RESERVATION-RULE-010 | inventory 缺行时 Ship 可按 products.stock_qty 建基线库存行；这不是预留建立 | Strong |
| RESERVATION-RULE-011 | DO reopen 只改 DO/SO 状态，不释放或回补库存，因为此前没有 reservation，且实物已出库 | Strong |
| RESERVATION-RULE-012 | 可用量、承诺量、释放量、预留过期和订单优先级均为 `UNKNOWN` | Missing |
| RESERVATION-RULE-013 | 多张 open DO 争用同一 SKU 时没有分配顺序；先成功 Ship 者直接消耗 on-hand | Strong negative |
| RESERVATION-RULE-014 | 主业务 repository 的库存读写未见 tenant predicate，虽 migration/scoped utilities 有 tenant 支持，隔离有效性仍为 `UNKNOWN` | Partial / risk |

## 3. 流程

### 3.1 已实现的“无预留”路径

1. 报价转 SO：复制订单行，不读取库存。
2. 人工审批 SO：pending → Open，不读取库存。
3. 创建 DO：复制 SO 全量行，不扣库存、不写 reservation。
4. DO 保持 Pending/待出库；期间其他订单或调整可改变 on-hand。
5. Ship 时逐行读取库存，库存不足则阻断。
6. 全部处理后写 DO 状态 `已出库` 并 commit。
7. Complete 只更新交付和 SO 状态；不再改库存。

### 3.2 预留/释放目标流程

`SO 确认 → 建立行级 reservation → 计算 available → 调整/取消释放 → DO 消耗 reservation`：`UNKNOWN`。已查 `apps/sales/**`、`apps/inventory/**`、相关 templates、`runtime/v14/legacy_support.py`、`business_modules/*.md` 与库存/交付报告，未找到运行闭环。

## 4. 校验（8 条）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| RESERVATION-VAL-001 | Ship 的 DO 必须存在 | 强 | 不存在返回 `not_found` |
| RESERVATION-VAL-002 | 仅 open 同义状态可 Ship | 强 | shipped/complete 拒绝重发，其他状态 `bad_status` |
| RESERVATION-VAL-003 | DO 级台账判重 | 强 | 防止同一 do_no 再次整体扣库 |
| RESERVATION-VAL-004 | 每个有效行 qty 必须由 on-hand 覆盖 | 强 | 不足返回 product id |
| RESERVATION-VAL-005 | Ship 需要 Delivery Orders edit 权限和 Human Approved 表单确认 | 强 | Type A POST 门禁 |
| RESERVATION-VAL-006 | safety stock 不得被突破 | 缺失 | Ship 仅检查不得小于零 |
| RESERVATION-VAL-007 | SO/DO 创建时可承诺量检查 | 缺失 | 没有预留或 ATP 校验 |
| RESERVATION-VAL-008 | 多行 Ship 先整体预检并失败回滚 | 缺失/风险 | 逐行边验边写，未见显式 rollback |

## 5. 数据含义（11 项）

| 数据 | 业务含义 |
|---|---|
| `inventory.stock_qty` | 当前 on-hand；Ship 与人工 Adjust 直接更新 |
| `products.stock_qty` | 镜像库存量；随 inventory delta 更新 |
| `inventory.safe_stock` | 低库存告警阈值，不是硬预留底线 |
| `inventory.location` | 自由文本位置，不区分预留库存 |
| `sales_order_items.qty` | 客户订单行需求数量 |
| `delivery_order_items.qty` | 本 DO 出库数量；当前创建时复制 SO qty |
| `delivery_orders.status` | DO 是否可执行 Ship/Complete 的阶段标签 |
| `inventory_ledger.qty` | 库存变动量；DO Ship 为负数 |
| `inventory_ledger.balance_qty` | 当次写入后的 SKU 余额 |
| `inventory_ledger.remark` | DO Ship 使用 `DO-{do_no}` 作为幂等关联 |
| available / reserved / allocated | `UNKNOWN`；无持久字段或计算服务证据 |

## 6. 状态词汇

| 词汇 | 含义/限制 |
|---|---|
| Pending / 待出库 / Pending Outbound | DO open 同义词；不是 reserved |
| 已出库 / Shipped | 已实际扣减库存 |
| Delivered / 已完成 | 交付完成；库存早在 Ship 扣减 |
| Open | SO 审批结果；不等于库存已锁定 |
| Delivery Created | SO 已创建 DO；不等于占用 |
| low stock | on-hand ≤ safety stock 的告警 |
| reserved / released / expired | `UNKNOWN`；未见运行状态 |

## 7. 证据表（10 项）

| Evidence | Path | 观察 | 强度 |
|---|---|---|---|
| E-RES-001 | `apps/inventory/services.py::ship_delivery_order` | Ship 才检查并扣 on-hand | Strong |
| E-RES-002 | `apps/inventory/repository.py` | inventory 读写只有 stock/safe/location | Strong |
| E-RES-003 | `apps/sales/services.py::convert_so` | SO 创建不查库存 | Strong |
| E-RES-004 | `apps/sales/services.py::apply_so_approve` | Approve 只改状态 | Strong |
| E-RES-005 | `apps/sales/services.py::create_delivery_order` | DO 复制行，创建不扣库存 | Strong |
| E-RES-006 | `runtime/v14/legacy_support.py` | inventory schema 无 reservation 字段 | Strong |
| E-RES-007 | `templates/inventory_detail.html` | 页面只显示 On-hand/Safety/Location | Strong |
| E-RES-008 | `templates/delivery_order_detail.html` | DO 行仅显示 qty 与 on-hand | Strong |
| E-RES-009 | `business_modules/inventory.md` | reservation contract 位于 Future Refactor Scope | Metadata-only |
| E-RES-010 | `docs/reports/Business_Strong_A003_Delivery_Report.md` | A-003 明确 Ship dual-write 与 reopen 不回库 | Strong corroboration |
| E-RES-011 | `database/v41_tenant_column_schema.py`、`apps/inventory/repository.py` | tenant 列迁移存在，但主库存 SQL 未见 scoped 条件 | Partial / risk |
| E-RES-012 | `apps/procurement/services.py::receive_purchase` | 对称入库使用 on-hand + ledger，不建立供应预留 | Strong |

## 8. UNKNOWN + 已查路径（7 项）

| UNKNOWN | 已查路径 |
|---|---|
| 行级 reservation 实体、编号、创建者和时间 | `apps/inventory/**`；`apps/sales/**`；`runtime/v14/legacy_support.py` |
| SO 审批时 ATP/available 计算 | `apps/sales/services.py`；`apps/sales/repository.py`；`templates/so_approve.html` |
| 订单取消时自动 release | `apps/sales/**`；`apps/inventory/**`；`templates/sales_order_detail.html` |
| reservation 部分消费与剩余占用 | `apps/inventory/services.py`；`apps/inventory/repository.py`；`templates/delivery_order_detail.html` |
| 预留过期、优先级、抢占和延期 | `apps/inventory/**`；`business_modules/inventory.md`；`docs/reports/Business_Strong_A002_Inventory_Report.md` |
| 并发 Ship/Adjust 的锁、版本号或原子条件更新 | `apps/inventory/repository.py`；`core/database/**`；`runtime/v14/legacy_support.py` |
| tenant 维度 reservation 隔离 | `database/v41_tenant_column_schema.py`；`apps/_tenant_query.py`；inventory/sales repositories |

## 9. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\validator.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\inventory.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\inventory_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sales_order_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\delivery_order_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\inventory.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\sales.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\shipment.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A002_Inventory_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A003_Delivery_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V151E_Volume010_Finance_Inventory_Business_Chain_Extraction_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v41_tenant_column_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\database\tenant_scope.py`
