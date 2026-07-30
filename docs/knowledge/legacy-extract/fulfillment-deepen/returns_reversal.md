# 退货 / 冲销 / 重开 — Legacy Deep Extract

**Evidence strength:** Strong（DO status-only reopen、人工库存调整）/ Strong negative（无退货/RMA闭环）/ Missing（库存与财务反向交易）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件调查销售退货、采购退货、DO 撤销、库存反向台账、收款/AR 冲销、Credit Note 与订单重开。Legacy 唯一明确的“reopen”运行能力是 completed DO 的状态重开；代码和页面均明确它不恢复库存。库存可通过通用 Adjust 加回，但没有 return source、RMA、质检或财务冲销语义。

**硬门槛计数：** 规则 16；校验 8；数据含义 13；证据 12；`UNKNOWN + 已查路径` 9。

## 2. 业务规则（稳定 ID，14 条）

| ID | 规则 | 证据强度 |
|---|---|---|
| RETURN-REVERSAL-RULE-001 | DO 只有 Complete 后才允许 Reopen | Strong |
| RETURN-REVERSAL-RULE-002 | Reopen 把 DO 改为 Pending，把关联 SO 改为 Open | Strong |
| RETURN-REVERSAL-RULE-003 | Reopen 明确不回补 inventory、不回补 products.stock_qty、不写反向 ledger | Strong |
| RETURN-REVERSAL-RULE-004 | 原 `DO Ship` ledger 保留；再次 Ship 会因台账判重而报 already_shipped | Strong |
| RETURN-REVERSAL-RULE-005 | SO 页面可把状态手工设为已取消/已完成/已发货，但提示“status only, no post” | Strong |
| RETURN-REVERSAL-RULE-006 | SO 取消不自动撤销 DO、恢复库存、释放收款或关闭 AR | Strong negative |
| RETURN-REVERSAL-RULE-007 | 通用 Inventory Adjust 支持正数加回并写 ledger，但默认语义是 Manual Adjustment | Strong |
| RETURN-REVERSAL-RULE-008 | scan-action 的 Move 可写 Transfer In/Out，但只调整同一库存行，不能证明退货或库间转移 | Strong negative |
| RETURN-REVERSAL-RULE-009 | DO Complete 后可 Post AR；Reopen 未见撤销该 AR | Strong / Strong negative |
| RETURN-REVERSAL-RULE-010 | receipt 只见新增与汇总，未见退款/负收款/receipt void 的业务入口 | Strong negative |
| RETURN-REVERSAL-RULE-011 | `CREDIT_NOTE`/`DEBIT_NOTE` 出现在文档类型注册，但未见销售退货触发或金额冲销服务 | Metadata-only |
| RETURN-REVERSAL-RULE-012 | 未见 RMA、return header/items、退货收货或退货质检实体 | Strong negative |
| RETURN-REVERSAL-RULE-013 | 未见采购退货到供应商及 AP 反向闭环 | Strong negative |
| RETURN-REVERSAL-RULE-014 | 重开、退货、财务冲销之间没有统一事务或追溯编号 | Missing |
| RETURN-REVERSAL-RULE-015 | DO 页面/列表可识别取消词汇，但 `apps/inventory` 未见专用 cancel handler；不能把 UI 状态当作冲销 | Strong negative |
| RETURN-REVERSAL-RULE-016 | PO Receive 只写正数 `PO Receipt`；Draft/Open purchase delete 不是已收货采购退货 | Strong |

## 3. 流程

### 3.1 已实现的 DO Reopen

1. DO 必须处于 Delivered/已完成。
2. 有 Delivery Orders edit 权限的用户点击 Reopen。
3. 系统把 DO 状态改为 Pending，把 SO 状态改为 Open。
4. 库存、产品镜像和原 DO Ship ledger 保持不变。
5. 页面提示如需回库使用 Inventory Adjust。
6. 因原 Ship ledger 仍在，直接再次 Ship 会被幂等判重阻断。

### 3.2 可用但无退货语义的人工补偿

1. 用户打开库存 Adjust。
2. 输入正数 delta、自由文本 remark 和 trans_type。
3. 系统增加 inventory 与 product stock，写一条 ledger。
4. 此动作不绑定退货客户、SO/DO 行、原因、质检和 Credit Note。

### 3.3 缺失的闭环

`退货申请 → 授权/RMA → 收货质检 → 可售/隔离库存 → DO/SO 反向 → Credit Note/退款 → 结案`：`UNKNOWN`。采购退货和 AP reversal 同样 `UNKNOWN`。

## 4. 校验（8 条）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| RETURN-REVERSAL-VAL-001 | Reopen 的 DO 必须存在 | 强 | 不存在回列表 |
| RETURN-REVERSAL-VAL-002 | 仅 complete DO 可 Reopen | 强 | 否则 `not_complete` |
| RETURN-REVERSAL-VAL-003 | Reopen 需要 Delivery Orders edit | 强 | 路由门禁 |
| RETURN-REVERSAL-VAL-004 | Reopen 前确认库存是否应回补 | 缺失 | 固定 status-only |
| RETURN-REVERSAL-VAL-005 | Reopen 前检查 AR/receipt/invoice | 缺失 | 未见财务依赖门禁 |
| RETURN-REVERSAL-VAL-006 | Inventory Adjust 不能产生负库存且 qty≠0 | 强 | validator + new balance |
| RETURN-REVERSAL-VAL-007 | 回库必须引用原 DO/RMA 并防重复 | 缺失 | remark/trans_type 自由输入 |
| RETURN-REVERSAL-VAL-008 | 退款/credit note 金额不得超过原交易 | 缺失 | 未见运行入口 |

## 5. 数据含义（12 项）

| 数据 | 业务含义 |
|---|---|
| `delivery_orders.status` | Reopen 直接修改的交付阶段 |
| `sales_orders.status` | 随 DO reopen 改为 Open；也可手工 status-only 更新 |
| `inventory.stock_qty` | Reopen 不改；人工 Adjust 可加回 |
| `products.stock_qty` | inventory delta 的镜像 |
| `inventory_ledger.trans_type` | DO Ship、Manual Adjustment、Transfer In/Out 等动作标签 |
| `inventory_ledger.qty` | 正数可表达人工回补，但没有 return 类型约束 |
| `inventory_ledger.remark` | 自由文本，可人工写来源但不是外键 |
| `ar_records` | DO 可生成的应收；未见 reopen reversal |
| `receipts` | SO 客户收款；未见 refund/void 状态 |
| `CREDIT_NOTE` | Document registry 类型，不是已证业务单据表 |
| `PO Receipt` | 采购正向入库 ledger 类型，不表示 supplier return |
| RMA / return order | `UNKNOWN`；无主表/明细表 |
| return disposition | `UNKNOWN`；无可售、隔离、报废判定字段 |

## 6. 状态词汇

| 词汇 | 含义/限制 |
|---|---|
| Delivered / 已完成 | Reopen 的唯一允许起点 |
| Pending | DO reopen 后状态，不代表库存已恢复 |
| Open | SO reopen 后状态 |
| 已取消 / Cancelled / Canceled | SO 标签；不触发反向业务动作 |
| already_shipped | 原 Ship 台账仍在时阻断再次出库 |
| Manual Adjustment | 通用库存补偿，不等于 Return Receipt |
| Transfer In / Transfer Out | 扫描 Move 的台账词汇，不等于跨仓或退货 |
| Returned / Refunded / Reversed / Voided | `UNKNOWN`；未见运行状态机 |

## 7. 证据表（10 项）

| Evidence | Path | 观察 | 强度 |
|---|---|---|---|
| E-RR-001 | `apps/inventory/services.py::_legacy_reopen_do` | 仅状态更新，不恢复库存 | Strong |
| E-RR-002 | `apps/inventory/services.py::ship_delivery_order` | 原 ledger 阻断再次 Ship | Strong |
| E-RR-003 | `templates/delivery_order_detail.html` | 页面明示 reopen status-only | Strong |
| E-RR-004 | `apps/sales/services.py::update_so_status` | SO 状态直接写入 | Strong |
| E-RR-005 | `templates/sales_order_detail.html` | 手工状态入口明确 no post | Strong |
| E-RR-006 | `apps/inventory/services.py::adjust_inventory` | 正/负 delta + ledger 的通用补偿 | Strong |
| E-RR-007 | `apps/finance/repository.py` | receipt/AR 读取新增，未见 refund/reverse | Strong negative |
| E-RR-008 | `runtime/v14/legacy_support.py` | 无 return/RMA 表；Credit Note 仅文档类型 | Strong negative / Metadata |
| E-RR-009 | `docs/reports/Business_Strong_A003_Delivery_Report.md` | 报告明确 reopen 不 auto-restore | Strong corroboration |
| E-RR-010 | `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | Post AR 是 AR accrual，非税务发票/冲销 | Strong corroboration |
| E-RR-011 | `apps/procurement/services.py::receive_purchase` | 采购侧只有正向 Receipt；删除仅限未收货阶段 | Strong |
| E-RR-012 | `document/nde_engine.py`、`templates/documents/credit_note.html` | Credit Note 可打印/映射，但无业务过账调用链 | Document-only |

## 8. UNKNOWN + 已查路径（8 项）

| UNKNOWN | 已查路径 |
|---|---|
| 销售退货/RMA 主表、明细和编号 | `apps/sales/**`；`apps/inventory/**`；`runtime/v14/legacy_support.py` |
| 退货授权、原因、客户和原 DO 行追溯 | sales/inventory routers/services/templates；delivery reports |
| 退货收货后的质检、隔离、报废和重新上架 | `apps/inventory/**`；inventory templates；business_modules/inventory.md |
| DO/SO 取消自动恢复库存 | sales/inventory services；sales/delivery templates |
| AR reversal、Credit Note 入账与原 DO 对冲 | `apps/finance/**`；finance templates；business_modules/finance.md |
| receipt refund/void 和客户退款 | finance repository/services/router；receipt templates |
| 采购退货、供应商退款和 AP reversal | `apps/procurement/**`；`apps/finance/**`；business_modules/procurement.md |
| 重开后的可重发策略与库存幂等重置 | `ship_delivery_order`、`_legacy_reopen_do`、inventory ledger schema |
| DO cancelled 状态的后端动作与库存处理 | `apps/inventory/**`；`templates/delivery_orders.html`；delivery reports |

## 9. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\delivery_order_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sales_order_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\adjust_inventory.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\inventory.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\sales.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\finance.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A003_Delivery_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V18_SO_DO_Invoice_TypeA_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\documents\credit_note.html`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
