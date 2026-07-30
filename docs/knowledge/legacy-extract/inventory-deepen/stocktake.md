# 盘点、盈亏与库存调整

## Scope与证据强度

本页检验 Legacy 是否存在盘点任务、盘点单、实盘录入、差异审批和盈亏过账。强证据仅覆盖通用 Adjust 页面及 `Cycle Count` 类型标签；未发现 `inventory_counts` / `stock_adjustments` 运行 DDL、盘点路由或专用模板。

结论：可用能力是“人工先在系统外算出差异，再把 delta 作为 Cycle Count/Manual Adjustment 过账”，不是完整盘点子系统。模块规范中的盘点表属于目标边界，不能当作运行事实。

## 业务规则（稳定ID）

1. **ST-R01** 盘点差异通过通用库存调整入口处理，没有专用盘点单入口。
2. **ST-R02** 调整表单输入的是 `qty_delta`，不是实盘数量；使用者需自行计算“实盘−账面”。
3. **ST-R03** 表单允许把交易类型选为 `Cycle Count`，服务仅把该字符串写入流水。
4. **ST-R04** 差异为正时增加现存量，为负时减少现存量。
5. **ST-R05** 零差异不能过账；因此没有“已盘且无差异”的库存流水证据。
6. **ST-R06** 负差异若使余额低于零会被拒绝。
7. **ST-R07** 成功调整同时更新库存现存量、产品库存镜像并追加带结余流水。
8. **ST-R08** `remark` 可记录原因/参考，但非必填；缺省可退为 `INV-{inventory_id}`。
9. **ST-R09** 表单可选择 `Damage Write-off` 表示损耗出库，但服务端不约束其方向。
10. **ST-R10** 调整操作需要 Inventory edit 权限，并有浏览器确认；服务端没有独立盘点审批角色。
11. **ST-R11** 盘点前冻结库存、盲盘、复盘、抽盘和差异阈值审批均未见运行实现。
12. **ST-R12** 台账保存数量差异和过账后余额，不保存账面量、实盘量两个独立字段。
13. **ST-R13** 库存估值页面按当前量乘产品成本展示，但盘点调整不单独持久化盈亏金额。
14. **ST-R14** `business_modules/inventory.md` 所列 `inventory_counts`、`stock_adjustments` 是规范/未来边界；活动 Legacy DDL未找到。

## 流程

### 已证盘点替代流程

1. 用户在系统外取得实盘数量。
2. 查看库存当前 on-hand，自行计算差异 delta。
3. 打开 Adjust，选择 `Cycle Count`，填写正/负 delta 和可选原因。
4. 浏览器提示确认，服务端校验非零和非负结果。
5. 更新库存、产品镜像并写流水。
6. 返回库存详情，可查看该产品最近流水。

### 未形成的完整流程

未见“建立盘点范围→冻结/截点→生成盘点表→初盘→复盘→批准差异→批量过账→盘点关闭”的实体和状态机。不能由 Cycle Count 标签推断这些步骤存在。

## 校验（强/弱/缺失）

1. **ST-V01（强）** 调整量不得为零。
2. **ST-V02（强）** 调整后库存不得为负。
3. **ST-V03（强）** 目标库存行必须存在。
4. **ST-V04（强）** 提交调整需要 Inventory edit 权限。
5. **ST-V05（弱）** 页面以确认对话框要求人工确认，但不是服务端 `human_confirm`。
6. **ST-V06（弱）** 页面类型下拉限制常见类型，服务端接受任意截断字符串。
7. **ST-V07（缺失）** 未校验实盘数量、账面数量和差异三者算术一致。
8. **ST-V08（缺失）** 未校验盘点日期、截点时间、盘点范围或重复盘点。
9. **ST-V09（缺失）** 未见差异绝对值/金额超过阈值时的审批。
10. **ST-V10（缺失）** 未见盘点人与批准人职责分离。
11. **ST-V11（缺失）** 未见盘点期间阻止 PO/DO/调整并发过账。
12. **ST-V12（缺失）** 未见原因码必填、附件、签名或复盘证据校验。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `inventory.stock_qty` | 盘点调整前后的账面现存量 |
| `qty_delta` | 用户直接输入的盈亏差异 |
| `Cycle Count` | 通用流水的交易类型标签 |
| `Manual Adjustment` | 默认人工调整类型 |
| `Damage Write-off` | 可选损耗标签，无独立损耗单 |
| `inventory_ledger.qty` | 已过账差异量 |
| `balance_qty` | 差异过账后的库存余额 |
| `remark` | 自由文本盘点/调整原因或参考 |
| `create_time` | 差异过账时间，不一定是实盘时间 |
| `products.stock_qty` | 同步后的产品库存镜像 |
| 实盘量 | 未独立持久化；只能由使用者外部掌握 |
| 账面截点量 | 未独立持久化 |
| 盘点盈亏金额 | 未独立持久化 |
| 盘点批次/单号 | 未见运行字段 |

## 状态词汇

| 词汇 | 含义/限制 |
|---|---|
| Cycle Count | 流水标签，不是盘点单状态 |
| Manual Adjustment | 默认差异过账标签 |
| Damage Write-off | 损耗标签 |
| Post adjustment | 立即更新库存并写流水 |
| Draft / Counting / Recount | UNKNOWN；未见盘点状态机 |
| Approved / Closed | UNKNOWN；未见盘点审批/关闭 |
| 盈余 | 正 delta |
| 亏损 | 负 delta |

## 证据表

| # | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| ST-E01 | Adjust 表单输入 delta 并可选 Cycle Count | 强 | `templates/adjust_inventory.html` |
| ST-E02 | 调整服务校验、双写和流水追加 | 强 | `apps/inventory/services.py` |
| ST-E03 | validator 只拒绝零调整 | 强 | `apps/inventory/validator.py` |
| ST-E04 | 流水结构无实盘量、盘点单号或金额 | 强 | `runtime/v14/legacy_support.py` |
| ST-E05 | Inventory 路由无专用 stocktake/count 页面 | 强（缺失证据） | `apps/inventory/router.py` |
| ST-E06 | 模板集中无盘点单/复盘页面 | 强（缺失证据） | `templates/` |
| ST-E07 | 模块规范列出 inventory_counts/stock_adjustments | 中（意图） | `business_modules/inventory.md` |
| ST-E08 | 活动 Legacy DDL 未找到上述规范表 | 强（缺失证据） | `runtime/v14/legacy_support.py` |
| ST-E09 | A-002 报告只验证调整，不宣称盘点工作流 | 强 | `docs/reports/Business_Strong_A002_Inventory_Report.md` |
| ST-E10 | A-018 强调人工过账且禁止静默调整 | 强 | `docs/reports/Business_Strong_A018_Inventory_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **盘点单、盘点批次和盘点范围实体 UNKNOWN。** 已查路径：`apps/inventory/`、Legacy DDL、`templates/`。
2. **盲盘、明盘和复盘规则 UNKNOWN。** 已查路径：Inventory routes/services/templates、`docs/reports/`。
3. **盘点截点及过账冻结机制 UNKNOWN。** 已查路径：Inventory、Procurement、Delivery 服务和数据库结构。
4. **盘盈盘亏金额及会计科目处理 UNKNOWN。** 已查路径：`apps/inventory/`、`apps/finance/`、产品成本字段、报告。
5. **差异审批阈值和角色分离 UNKNOWN。** 已查路径：`apps/approval/`、Inventory router、业务模块规范。
6. **原因码、附件、照片和签名证据 UNKNOWN。** 已查路径：Adjust 模板、Inventory schema/repository、上传组件。
7. **同一 SKU 多地点分别盘点 UNKNOWN。** 已查路径：inventory schema、warehouse pack、`business_modules/inventory.md`。
8. **零差异盘点如何留痕 UNKNOWN。** 已查路径：validator、adjust service、inventory ledger schema。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\adjust_inventory.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\inventory_ledger.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\inventory.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
