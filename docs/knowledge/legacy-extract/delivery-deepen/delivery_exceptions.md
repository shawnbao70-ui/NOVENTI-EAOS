# 发货异常、拦截与重开

## Scope与证据强度

本页覆盖 DO cancel、hold、Ship 拦截、Complete、Reopen、库存补偿、SO/AR 联动、权限和重复操作。

- **强证据：** Inventory/Sales/Finance 的运行服务、路由、台账及 Type A 页面。
- **中证据：** 页面诚实提示与 gates 互证，但异常审计仍不完整。
- **明确缺失：** 没有 DO Cancel、Hold、Reverse Ship 专用 API；Reopen 不是库存冲销。
- **核心结论：** 异常处理由状态机、Ship 前置校验、人审和手工库存调整拼接而成，不是独立异常子系统。

## 业务规则

1. **DE-R01** DO 原始状态被归一为 open、shipped、complete 或 other。
2. **DE-R02** Ship 是正式库存出库写路径，同时更新 inventory、products 和 ledger。
3. **DE-R03** 创建 DO 不扣库存，避免创建与 Ship 双扣。
4. **DE-R04** 已 Ship/Complete 或已有 DO ledger 时拒绝再次 Ship。
5. **DE-R05** Complete 必须先 Ship。
6. **DE-R06** Complete 将 DO 和关联 SO 都推进为 Delivered。
7. **DE-R07** Reopen 只允许 complete DO，回写 DO Pending、SO Open，不恢复库存。
8. **DE-R08** 错误出库的库存补偿只能使用 Inventory Adjust 等人工路径。
9. **DE-R09** 没有 DO Delete/Cancel 服务；列表按钮禁用也不构成取消流程。
10. **DE-R10** 没有 Hold/Intercept 状态或工作流。
11. **DE-R11** Ship 和 Invoice Type A 只有 action=approve 且人工确认时执行。
12. **DE-R12** DO→AR 不强制要求 Ship；未出库只显示警告。
13. **DE-R13** 已有 AR 只产生 UI 警告，不阻止重复应计。
14. **DE-R14** Ship/Complete/Reopen 需要 Delivery Orders edit 权限。
15. **DE-R15** 非管理角色的 DO 可按 SO 销售人员归属过滤。
16. **DE-R16** A-003 之前的历史 DO 可能已在创建时扣库存，Ship 存在历史双扣风险。

## 流程

1. SO 生成 Pending DO。
2. Ship 前，系统检查状态、ledger、库存记录和在手量；任一失败即形成实际“拦截”。
3. 人工确认后 Ship，系统扣库存并写台账。
4. Shipped DO 才能 Complete，随后 SO 变为 Delivered。
5. Delivered DO 可 Reopen；状态回到 Pending/Open，但库存和 AR 不变。
6. 若需要恢复库存，用户另行 Inventory Adjust。
7. AR 可在任意 DO 阶段人工确认入账；重复只警告。

## 校验

1. **DE-V01** Ship 前 DO 必须处于 open。
2. **DE-V02** 状态或 ledger 均可阻止重复 Ship。
3. **DE-V03** Ship 只处理有效产品和正数量行。
4. **DE-V04** 库存记录必须存在或可自动建立。
5. **DE-V05** 在手库存必须足够。
6. **DE-V06** Complete 前必须 Shipped。
7. **DE-V07** 已 Complete 不可重复 Complete。
8. **DE-V08** Reopen 只允许 complete。
9. **DE-V09** Type A Ship 必须人工确认。
10. **DE-V10** Type A Invoice 必须人工确认。
11. **DE-V11** Inventory Adjust 不得产生负库存。
12. **DE-V12** Inventory Adjust 数量不得为零。

缺失校验包括：重复 AR 硬阻断、Ship→AR 顺序、Reopen 后 AR 一致性、Cancel/Hold、部分 Ship 事务回滚。

## 数据含义

| 数据 | 含义 |
|---|---|
| `delivery_orders.do_no` | DO 标识和 ledger 幂等键来源 |
| `delivery_orders.status` | 中英文混合原始状态 |
| `delivery_orders.so_id` | SO 联动依据 |
| `delivery_orders.total_amount` | AR 应计金额来源 |
| `delivery_order_items.qty` | Ship 扣减量 |
| `inventory.stock_qty` | 仓内在手量 |
| `products.stock_qty` | 产品库存镜像 |
| `inventory_ledger.trans_type` | 出库固定 `DO Ship` |
| `inventory_ledger.qty` | Ship 负向数量 |
| `inventory_ledger.remark` | `DO-{do_no}` 幂等锚点 |
| `ar_records.source_no` | AR 来源 DO 号 |
| `ar_records.status` | 新建应收为 Unpaid |
| `sales_orders.status` | 创建/完成/重开时随 DO 改变 |
| `do_stage` | 服务层归一阶段，不是数据库列 |

## 状态词汇

| 状态 | 归一阶段/含义 |
|---|---|
| `Pending` / `待出库` / `Pending Outbound` | open |
| `已出库` / `Shipped` | shipped |
| `Delivered` / `已完成` | complete |
| `Cancelled` / `Canceled` / `已取消` | UI 可识别，但无写入流程 |
| `Delivery Created` | SO 已建 DO |
| `Open` | Reopen 后 SO 状态 |
| `Unpaid` | 新建 AR 状态 |
| `already_shipped` / `ship_first` / `not_complete` | 异常阻断错误词 |

## 证据表

| # | 观察事实 | 强度 | 只读路径 |
|---|---|---|---|
| E1 | 三态归一状态机 | 强 | `apps/inventory/services.py` |
| E2 | Ship 库存三写 | 强 | `apps/inventory/services.py` |
| E3 | Reopen 只改状态 | 强 | `apps/inventory/services.py` |
| E4 | Complete 联动 SO | 强 | `apps/inventory/services.py` |
| E5 | Type A 路由和权限 | 强 | `apps/inventory/router.py` |
| E6 | AR 创建无硬防重 | 强 | `apps/finance/services.py` |
| E7 | A-003 gate 验证出库链 | 强 | `docs/reports/Business_Strong_A003_Delivery_Report.md` |
| E8 | Delete/Cancel UI 诚实禁用 | 中 | `templates/delivery_orders.html` |
| E9 | 创建 DO 不扣库存 | 强 | `apps/sales/services.py` |
| E10 | Customs registry 与 DO 无交界 | 强（缺失证据） | `apps/customs_center/shipping_registry.py` |

## UNKNOWN

1. **正式 DO Cancel 流程 UNKNOWN/未实现。** 已查 Inventory 服务、路由、模板与 Legacy 写入点。
2. **Hold/Intercept 是否存在于未纳入分支 UNKNOWN。** 已查 Shipment 规格及当前 apps。
3. **重复 AR 的生产处置策略 UNKNOWN。** 已查 Finance repository、DDL 和索引。
4. **Ship 多行中途失败的事务语义 UNKNOWN。** 已查服务 commit 点和 repository factory。
5. **Customs 报关节点是否应拦截 DO UNKNOWN。** 已查 Customs core 与 Center。
6. **Workflow Center 是否应承接 DO 异常 UNKNOWN。** 已查 workflow repository 和目录报告。
7. **DO tenant 隔离完整性 UNKNOWN。** 已查 V41 tenant patch 与查询。
8. **Ship/Complete/Reopen 是否写操作审计 UNKNOWN/未证明。** 已查 Inventory 服务和 history scaffold。
9. **历史双扣 DO 的识别与修复策略 UNKNOWN。** 已查 A-003 报告与 ledger 规则。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customs_center\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\delivery_order_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\delivery_orders.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\do_ship.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\do_invoice.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ai_operating_depth\`
- `H:\Workspace\EZAM_CRM - 9.0\scripts\business_strong_a003_delivery_gate.py`
- `H:\Workspace\EZAM_CRM - 9.0\scripts\v18_so_do_invoice_gate.py`
