# 仓库 / 仓位 / 库位组织 — Legacy Deep Extract

**Evidence strength:** Strong（扁平 SKU 库存与自由文本 location）/ Metadata-only（Warehouse360/模块规范）/ Missing（仓库与库位主数据）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件调查 warehouse master、bin/location、每仓库存、库间转移、默认收发仓、容量、批次与序列号。Legacy 运行 schema 只确认 `inventory(product_id, stock_qty, safe_stock, location)`；页面称 location/no bin，但它是单个自由文本字段。`business_modules/inventory.md` 列出的 warehouses、warehouse_locations、stock_movements 等是模块规范/未来边界，未在运行 schema 和页面中落地。

**硬门槛计数：** 规则 16；校验 8；数据含义 13；证据 12；`UNKNOWN + 已查路径` 8。

## 2. 业务规则（稳定 ID，14 条）

| ID | 规则 | 证据强度 |
|---|---|---|
| WAREHOUSE-RULE-001 | 运行库存记录以 product_id 为中心，保存 stock_qty、safe_stock、location | Strong |
| WAREHOUSE-RULE-002 | location 是可直接编辑的自由文本，无 warehouse/bin 外键 | Strong |
| WAREHOUSE-RULE-003 | inventory 列表支持按 product code/name/location 搜索 | Strong |
| WAREHOUSE-RULE-004 | Safety/Loc 编辑不改数量、不写库存台账 | Strong |
| WAREHOUSE-RULE-005 | 数量变化必须走 Adjust、PO Receive、Sample Receipt 或 DO Ship 等路径写 ledger | Strong |
| WAREHOUSE-RULE-006 | 扫描动作按产品代码找到单条 inventory row，并展示其 location | Strong |
| WAREHOUSE-RULE-007 | scan “Move” 实际对同一 inventory row 应用正/负 delta，台账标 Transfer In/Out | Strong |
| WAREHOUSE-RULE-008 | Move 不接收 source warehouse、target warehouse 或 target bin，不能证明库间转移 | Strong negative |
| WAREHOUSE-RULE-009 | Ship/Receive 按 product 找库存行，不选择收发仓或库位 | Strong |
| WAREHOUSE-RULE-010 | 缺库存行时可从 products.stock_qty 创建 location='' 的 inventory 行 | Strong |
| WAREHOUSE-RULE-011 | 删除 inventory row 仅允许 qty=0，ledger 不随行删除 | Strong |
| WAREHOUSE-RULE-012 | Warehouse360 runtime 在 inventory 列表上合成 `INV-CENTER / Inventory Center` 虚拟 warehouse，并非读取仓库主表 | Strong |
| WAREHOUSE-RULE-013 | Warehouse360 的 warehouse id/code/status/sections 为并行 Object360 context；legacy renderer 仍权威 | Metadata/parallel |
| WAREHOUSE-RULE-014 | 仓库层级、库位容量、批次序列和跨仓余额均为 `UNKNOWN` | Missing |
| WAREHOUSE-RULE-015 | 全库未见 `warehouses`/`warehouse_locations` 运行 DDL、`/warehouse` 路由或 `warehouse.html` 模板；规范清单不可当作已实现 | Strong negative |
| WAREHOUSE-RULE-016 | PO Receive 是已证收仓动作，写正数 `PO Receipt` ledger；但同样不选择 warehouse/bin | Strong |

## 3. 流程

### 3.1 Location 维护

1. 用户打开 inventory row。
2. 以 Inventory edit 权限进入 Safety/Loc。
3. 更新 safe_stock 与自由文本 location。
4. 页面返回 Inventory 360；不写 movement ledger。

### 3.2 Scan action

1. 扫描/输入产品代码，系统解析到 inventory row。
2. 展示 on-hand 与 location，并寻找该产品最近 open PO/DO。
3. Receive 分支调用整张 PO receive；Ship 分支调用整张 DO Ship。
4. Move 分支对当前 row 输入正/负 qty，以 Transfer In/Out 做通用调整。
5. 没有 source/target warehouse 两边同时过账。

### 3.3 Warehouse360 并行装配

Inventory list context 缺 `warehouse` 时，runtime 固定合成 id=1、code=`INV-CENTER`、name=`Inventory Center`、status=`Active`，再派生 Warehouse360 sections。该流程不证明真实仓库主数据存在。

## 4. 校验（8 条）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| WAREHOUSE-VAL-001 | Safety/Loc 更新需要 Inventory edit | 强 | router 门禁 |
| WAREHOUSE-VAL-002 | location 必须匹配已登记仓/位 | 缺失 | 任意字符串可保存 |
| WAREHOUSE-VAL-003 | Adjust qty 不得为 0 | 强 | validator |
| WAREHOUSE-VAL-004 | 调整后库存不得为负 | 强 | service 计算阻断 |
| WAREHOUSE-VAL-005 | scan action 需要 Human Approved | 强 | human_confirm=1 |
| WAREHOUSE-VAL-006 | Receive/Ship 必须找到 open PO/DO | 强（入口） | 但不校验仓库归属 |
| WAREHOUSE-VAL-007 | 库间转移 source 减与 target 加必须原子平衡 | 缺失 | Move 只有单行 delta |
| WAREHOUSE-VAL-008 | 仓位容量、SKU 混放、批次/序列约束 | 缺失 | 无结构化字段 |

## 5. 数据含义（12 项）

| 数据 | 业务含义 |
|---|---|
| `inventory.id` | 扁平库存行标识 |
| `inventory.product_id` | 该库存行对应产品 |
| `inventory.stock_qty` | 产品总 on-hand，不分仓 |
| `inventory.safe_stock` | 低库存阈值 |
| `inventory.location` | 人工自由文本位置 |
| `products.stock_qty` | 镜像总库存 |
| `inventory_ledger.trans_type` | 收、发、调整或 Transfer 标签 |
| `inventory_ledger.balance_qty` | 单产品变动后余额 |
| `Transfer In/Out` | 同一行人工 delta 的标签，不是 transfer order |
| `INV-CENTER` | Warehouse360 runtime 合成 code |
| `safety_stock` / `location_code` | migration 曾追加，但 `apps/inventory` 活跃路径仍读取 `safe_stock` / `location` |
| warehouse_id / bin_id | `UNKNOWN`；运行 inventory 无字段 |
| lot/serial/expiry/capacity | `UNKNOWN`；未见结构化库存维度 |

## 6. 状态词汇

| 词汇 | 含义/限制 |
|---|---|
| low stock | stock_qty ≤ safe_stock |
| Active | 合成 Warehouse360 profile 的默认状态 |
| runtime / shadow | 并行 Warehouse360 bundle 模式 |
| Transfer In / Transfer Out | 单行 inventory adjustment 类型 |
| Receive / Ship / Move | scan action 分支 |
| no bin | 页面在空 location 时的展示词，不证明 bin 实体 |
| Available / Blocked / Quarantine | `UNKNOWN`；未见仓位库存状态 |

## 7. 证据表（10 项）

| Evidence | Path | 观察 | 强度 |
|---|---|---|---|
| E-WH-001 | `runtime/v14/legacy_support.py` | inventory schema 仅含 location 文本 | Strong |
| E-WH-002 | `apps/inventory/repository.py` | 查询/更新 location，无 warehouse join | Strong |
| E-WH-003 | `apps/inventory/services.py::update_inventory_meta` | Safety/Loc 独立更新 | Strong |
| E-WH-004 | `apps/inventory/services.py::apply_scan_action` | Move 转为单行 Adjust | Strong |
| E-WH-005 | `templates/inventory.html` | 一列 Location，无仓库/库位层级 | Strong |
| E-WH-006 | `templates/inventory_detail.html` | 显示 On-hand/Safety/Location | Strong |
| E-WH-007 | `templates/inventory_scan_action.html` | Receive/Ship/Move，无 source/target | Strong |
| E-WH-008 | `core/object360/warehouse/runtime.py` | 合成 INV-CENTER，而非查 warehouse | Strong |
| E-WH-009 | `business_modules/inventory.md` | warehouses/location tables 属规范清单 | Metadata-only |
| E-WH-010 | `docs/reports/V151E_Volume010_Finance_Inventory_Business_Chain_Extraction_Report.md` | 明确无离散 Warehouse Location 路由 | Strong corroboration |
| E-WH-011 | `apps/procurement/services.py::receive_purchase` | PO Receipt 增库存并写正数 ledger，但无仓别 | Strong |
| E-WH-012 | 全库 route/template/schema 检索 | 无 `/warehouse` handler、`warehouse.html` 与 warehouse master DDL | Strong negative |

## 8. UNKNOWN + 已查路径（8 项）

| UNKNOWN | 已查路径 |
|---|---|
| warehouses 运行主表、仓库代码和地址 | `runtime/v14/legacy_support.py`；`apps/inventory/**`；`business_modules/inventory.md` |
| warehouse_locations/bin 主表与层级 | 同上；inventory templates；`core/object360/warehouse/**` |
| 每仓每 SKU 余额与唯一键 | inventory repository/schema；Warehouse360 runtime |
| source/target 双边库间转移单 | scan action service/template；inventory ledger |
| 默认采购收货仓与销售发货仓 | procurement/inventory/sales services；相关 templates |
| 库位容量、冻结、隔离、可售状态 | inventory schema/templates；docs/reports inventory |
| lot、serial、expiry、FIFO/FEFO | inventory/sales/procurement apps；runtime schema |
| tenant/company 维度仓库权限和库存隔离 | tenant schema；inventory repository；Object360 warehouse context |

## 9. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\inventory.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\inventory_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\edit_inventory.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\inventory_scan_action.html`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\warehouse\runtime.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\warehouse\warehouse_integration.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\warehouse\warehouse_context.py`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\inventory.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A002_Inventory_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A018_Inventory_Ops_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V151E_Volume010_Finance_Inventory_Business_Chain_Extraction_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V18_P5_Recognize_Gate_Report.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\warehouse\Warehouse360_Architecture.md`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
