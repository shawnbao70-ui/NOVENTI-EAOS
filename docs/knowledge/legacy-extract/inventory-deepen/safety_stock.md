# 安全库存与补货建议交界

## Scope与证据强度

本页覆盖 `safe_stock`、低库存判断、补货建议数量和 Draft PO 生成。安全库存检测及补货草稿流程证据强；需求预测、在途扣减、预留量、采购提前期、EOQ、服务水平和多仓补货未见运行证据。

采购单生命周期边界交叉引用 [`../procurement-deepen/README.md`](../procurement-deepen/README.md) 与 [`../ops/procurement.md`](../ops/procurement.md)。当前 `procurement-deepen/INDEX.md` 列出的正文尚未在工作区落地，本页不虚构链接。

## 业务规则（稳定ID）

1. **SS-R01** 每条库存行保存一个 `safe_stock` 数值，运行逻辑以它作为低库存阈值。
2. **SS-R02** 当 `inventory.stock_qty <= inventory.safe_stock` 时判为低库存，包括等于阈值。
3. **SS-R03** 库存列表、详情和 Dashboard 使用同一比较，详情暴露 `is_low_stock`。
4. **SS-R04** 低库存列表按现存量升序，最多取 20 条。
5. **SS-R05** Safety/Loc 编辑可直接更新安全库存；解析失败回退为 0。
6. **SS-R06** 缺库存行时由产品镜像建立的新行安全库存为 0，而原始 DDL 默认值为 10，创建路径存在默认差异。
7. **SS-R07** 采购补货页面只读取低库存 SKU，并带出产品当前成本供 Draft PO 行定价。
8. **SS-R08** 当安全库存大于 0，建议量为 `max(safe_stock - stock_qty, 1)`。
9. **SS-R09** 当安全库存不大于 0，建议量退化为 `max(1, 10 - stock_qty)`；即使阈值为 0 仍可能建议补到 10。
10. **SS-R10** 用户可修改或排除建议数量；生成时只保留大于零的所选行。
11. **SS-R11** 生成补货必须选择供应商，并创建 Draft PO；不会直接增加库存。
12. **SS-R12** Draft PO 需要后续批准进入 Open，之后独立 Receive 才过账库存。
13. **SS-R13** 补货建议不扣除已有开放 PO/在途数量，也不考虑开放 DO、预留或需求预测。
14. **SS-R14** 建议选择首个活动供应商作为默认，但未见按 SKU 的首选供应商/价格/交期匹配。
15. **SS-R15** 页面称 AI suggests，但算法是确定性阈值公式；AI 不可静默建单或收货。
16. **SS-R16** 安全库存与 location 一起作为库存元数据维护，不形成库存流水。

## 流程

### 阈值维护与预警

1. 用户以 Inventory edit 权限更新 `safe_stock`。
2. 页面查询时实时比较现存量和阈值。
3. 符合 `<=` 的 SKU 进入低库存 KPI和列表。
4. 修改阈值本身不写库存流水。

### 补货建议到库存

1. 打开 `/purchases/replenish`，读取最多 20 个低库存 SKU。
2. 计算默认建议量并读取产品成本。
3. 用户选择供应商并人工调整数量。
4. 系统创建 Draft PO及其行，跳到 PO Approve。
5. 人工批准后 PO Open。
6. Receive 才增加库存、产品镜像并写 `PO Receipt`。

## 校验（强/弱/缺失）

1. **SS-V01（强）** 补货页面查看需要 Purchases view 权限。
2. **SS-V02（强）** 生成 Draft PO需要 Purchases add 权限。
3. **SS-V03（强）** 生成时必须有供应商。
4. **SS-V04（强）** 至少选择一条大于零的数量。
5. **SS-V05（强）** 只有低库存查询返回的 SKU 被默认建议。
6. **SS-V06（弱）** 页面数量设置 `min=0`，服务端再过滤非正数。
7. **SS-V07（缺失）** 安全库存不得为负的校验未见；负值可保存。
8. **SS-V08（缺失）** 未见建议量上限、包装倍数、最小订购量或整数约束。
9. **SS-V09（缺失）** 未检查已有 Draft/Open PO，可能重复补货。
10. **SS-V10（缺失）** 未检查供应商是否供应该 SKU。
11. **SS-V11（缺失）** 未考虑采购提前期、需求速率、服务水平或季节性。
12. **SS-V12（缺失）** 未见多仓阈值、在途量、预留量和可用量校验。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `inventory.safe_stock` | 低库存触发阈值 |
| `inventory.stock_qty` | 参与阈值比较的现存量 |
| `is_low_stock` | `stock_qty <= safe_stock` 的布尔结果 |
| `low_stock_count` | 当前满足阈值的库存行数 |
| `low_stock_items` | 最低现存量优先、最多 20 条的候选 |
| `suggest_qty` | 阈值公式计算的 Draft PO 建议量 |
| `products.cost_price` | 生成采购行时采用的单位成本 |
| `supplier_id` | 整张建议 PO 的供应商 |
| `default_supplier_id` | 首个活动供应商，不是 SKU 首选关系 |
| `line_qty` | 用户确认/修改后的按 product_id 数量 |
| Draft PO | 补货建议持久化结果，但尚不可收货 |
| Open PO | 批准后可收货状态 |
| `PO Receipt` | 真正入库过账流水 |
| on-order / in-transit | 未纳入建议公式 |
| reserved / demand | 未纳入建议公式 |

## 状态词汇

| 状态/词汇 | 含义 |
|---|---|
| Low Stock | 现存量小于等于安全库存 |
| Safe Stock | 人工维护的单一阈值 |
| Suggestion | 确定性公式结果，可人工修改 |
| Draft | 补货 PO 已建但未开放 |
| Open | PO 已批准，可收货 |
| Received | PO 已实际入库 |
| Medium risk | 页面对存在低库存建议的摘要标签 |
| AI suggestion | 展示措辞，不是预测模型证据 |

## 证据表

| # | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| SS-E01 | inventory DDL含 safe_stock，默认 10 | 强 | `runtime/v14/legacy_support.py` |
| SS-E02 | 低库存统一使用 stock_qty <= safe_stock | 强 | `apps/inventory/repository.py`、`services.py` |
| SS-E03 | Safety/Loc 可直接更新阈值 | 强 | `apps/inventory/router.py`、`repository.py` |
| SS-E04 | 缺行补建时 safe_stock=0 | 强 | `apps/inventory/repository.py` |
| SS-E05 | 补货建议公式及产品成本读取 | 强 | `apps/procurement/services.py`、`repository.py` |
| SS-E06 | 生成只接受供应商和正数所选行 | 强 | `apps/procurement/router.py`、`services.py` |
| SS-E07 | 页面允许人工调整建议数量并生成 Draft PO | 强 | `templates/purchase_replenish.html` |
| SS-E08 | Draft→Approve→Open 与 Receive 分离 | 强 | `apps/procurement/services.py`、router |
| SS-E09 | Receive 才写库存和 PO Receipt | 强 | `apps/procurement/services.py` |
| SS-E10 | A-018 报告拒绝 AI forecast 过度声明 | 强 | `docs/reports/Business_Strong_A018_Inventory_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **安全库存的计算依据、责任人和复核周期 UNKNOWN。** 已查路径：`apps/inventory/`、`apps/procurement/`、templates、报告。
2. **开放 PO/在途量是否应从建议量扣除 UNKNOWN。** 已查路径：补货查询、purchase repository、PO状态逻辑。
3. **销售需求、预测和预留如何进入补货公式 UNKNOWN。** 已查路径：Inventory、Sales、Quotation、Procurement apps。
4. **采购提前期、服务水平和需求波动参数 UNKNOWN。** 已查路径：产品/供应商/采购 schema 与模板。
5. **最小订购量、包装倍数、EOQ和最大库存 UNKNOWN。** 已查路径：Procurement services/repository、产品和供应商主数据。
6. **SKU 首选供应商和价格合同 UNKNOWN。** 已查路径：`apps/procurement/`、`apps/supplier/`、purchase templates。
7. **多仓分别设置安全库存与调拨优先补货 UNKNOWN。** 已查路径：Inventory schema、Warehouse360、fulfillment-deepen/warehouse。
8. **负安全库存的业务含义 UNKNOWN。** 已查路径：update_inventory_meta、router parse、DDL；未见拒绝或解释。
9. **重复生成补货 Draft PO 的去重策略 UNKNOWN。** 已查路径：generate_replenish_draft、低库存查询、PO查重方法。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\purchase_replenish.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\inventory.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\inventory_dashboard.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\inventory.md`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\procurement.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
# 安全库存 / 再订货点 / 补货建议 — Legacy Deep Extract

**Evidence strength:** Strong（inventory/procurement 运行 SQL 与页面服务）/ Strong negative（无 reorder/EOQ/在途净额）/ Medium（AI 与 BI 口径漂移）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Chain role:** 低库存判定 → 人工补货页 → Draft PO → 审批 → 收货（采购侧细节见 [`../procurement-deepen/README.md`](../procurement-deepen/README.md)，规则 ID 交叉引用 [`../ops/procurement.md`](../ops/procurement.md) P-R4–P-R7，不复制正文）

---

## 1. Scope 与字段权威

Legacy 运行层**唯一可写阈值**是 `inventory.safe_stock`；UI/i18n 以 `safety_stock` 展示，编辑入口在 `/edit_inventory/{id}`（仅改安全库存与库位，不改 on-hand）。  
**未发现**运行中的 `min_stock`、`reorder_level`、`reorder_point` 列或等价持久字段；AI/报表偶用 “reorder level” 措辞，但 SQL 与页面逻辑均对比 `safe_stock`。  
`products.stock_qty` 是 on-hand 镜像，**不是**再订货阈值；产品主数据维护路径不含安全库存字段。

**硬门槛计数：** 规则 14；校验 9；数据含义 12；证据 10；`UNKNOWN + 已查路径` 8。

---

## 2. 业务规则（14 条）

| ID | 规则 | 证据强度 |
|---|---|---|
| SAFETY-RULE-001 | 低库存权威判定：`inventory.stock_qty <= inventory.safe_stock`（含等于） | Strong |
| SAFETY-RULE-002 | 阈值字段仅存于 `inventory` 表；新建库存行默认 `safe_stock=0` | Strong |
| SAFETY-RULE-003 | 列表/仪表盘/详情 KPI 共用 repository 低库存计数与 Top-N 查询（上限 20，按 stock 升序） | Strong |
| SAFETY-RULE-004 | 详情页 `is_low_stock` 与 repository 判定一致；用于 KPI 着色与 AI brief | Strong |
| SAFETY-RULE-005 | 安全库存仅人工编辑（Inventory edit 权限）；Adjust 只改 on-hand 并写台账，不改阈值 | Strong |
| SAFETY-RULE-006 | 低库存**不**触发自动建 PO；补货是 `/purchases/replenish` 上的人工 Type A 表单动作 | Strong |
| SAFETY-RULE-007 | 补货候选 SQL 与库存低库存 SQL 同 predicate，且要求 `product_id IS NOT NULL` | Strong |
| SAFETY-RULE-008 | 建议量启发式：`safe>0` 时 `max(safe - stock, 1)`；`safe=0` 时 `max(10 - stock, 1)` | Strong |
| SAFETY-RULE-009 | 补货提交创建 **Draft** PO 并跳转审批页；Approve 变 Open；**Receive 才加库存**（交叉 P-R7、P-R9） | Strong |
| SAFETY-RULE-010 | 建议行成本取 `products.cost_price` 快照；不读供应商报价或价格表 | Strong |
| SAFETY-RULE-011 | 低库存计算**不扣减** open PO 在途量、SO/DO 需求、预留或占用（与 reservation 包一致） | Strong negative |
| SAFETY-RULE-012 | Ship 出库只校验 on-hand ≥ DO qty，**不**保留 safety stock 硬底线 | Strong |
| SAFETY-RULE-013 | 企业仪表盘/BI 的 `low_stock_products` 常来自 `products ORDER BY stock_qty ASC LIMIT 10`，**不是** safe_stock  breach | Strong（口径漂移） |
| SAFETY-RULE-014 | Warehouse360 runtime 仅透传 `low_stock_count` 等到 shadow/dashboard；**不**重算策略 | Medium |

---

## 3. 流程

### 3.1 低库存识别 → 补货建议（运行链）

1. 操作者维护 `inventory.safe_stock`（Edit Inventory）与 on-hand（Adjust / PO Receive / DO Ship）。
2. 任意库存列表/仪表盘执行 `stock_qty <= safe_stock` 统计与 watchlist（最多 20 SKU）。
3. 采购员打开 `/purchases/replenish`（Purchases **view**）；服务读取低库存行并计算 `suggest_qty`。
4. 选择供应商、确认各 `qty_{product_id}`，提交（Purchases **add**）→ 创建 Draft PO + 行 → 重定向 `/purchase/{id}/approve`。
5. 人工 Approve（Purchases **edit** + `human_confirm=1`）→ Open；库存不变。
6. Receive（独立动作）增加 on-hand；低库存状态可能解除。

### 3.2 非自动路径

- 无定时任务、无 event bus、无后台 job 自动生成 PO。
- AI recommendation / risk_engine / operating brief 仅**提示**访问 `/inventory` 或 `/purchases`；不写库、不建单。
- `purchase_replenish.html` 的 `require_human_confirm=false` 指生成 Draft 步；真正 Open 仍在 approve 页要求 Human Confirm。

---

## 4. 校验（9 条）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| SAFETY-VAL-001 | 低库存 SQL 使用 `<=` 而非 `<` | 强 | safe=stock 仍算低库存 |
| SAFETY-VAL-002 | Edit safe_stock 需 Inventory **edit** | 强 | view 不可改阈值 |
| SAFETY-VAL-003 | safe_stock 表单为 required number；解析失败回落 0 | 弱 | 无负数/上限服务校验 |
| SAFETY-VAL-004 | 补货生成需 supplier_id 与至少一行 qty>0 | 强 | 错误码 `v18_supplier_required` / `v18_approve_needs_lines` |
| SAFETY-VAL-005 | 补货页 GET 需 Purchases **view**；POST 需 **add** | 强 | |
| SAFETY-VAL-006 | PO Approve 需 Draft、有行、`human_confirm=1`、Purchases **edit** | 强 | 交叉 P-V9 |
| SAFETY-VAL-007 | Adjust 拒绝 qty=0 与负余额 | 强 | 不改变 safe_stock |
| SAFETY-VAL-008 | 低库存判定**不**校验 open PO 是否已覆盖缺口 | 缺失 | 可能重复建议 |
| SAFETY-VAL-009 | safe_stock 与 stock_qty 双 0 仍计为低库存 | 强（副作用） | 阈值未配置时的噪声 |

---

## 5. 数据含义（12 项）

| 数据 | 业务含义 |
|---|---|
| `inventory.stock_qty` | On-hand 现存量；低库存与补货计算的分子 |
| `inventory.safe_stock` | 安全库存阈值；UI 称 safety stock；**事实上的 reorder point** |
| `inventory.location` | 库位文本；与低库存策略无关 |
| `inventory.product_id` | 补货候选必须非空 |
| `products.stock_qty` | 镜像 on-hand；ensure_inventory 建行基线；**不参与**低库存 SQL |
| `products.cost_price` | 补货 Draft 行默认成本 |
| `suggest_qty` | 服务层计算字段，非持久列；可被人为改表单覆盖 |
| `low_stock_count` | `COUNT(*)` where `stock_qty <= safe_stock` |
| `low_stock_items` | 同上 predicate + LIMIT 20 + ORDER BY stock ASC |
| `is_low_stock` | 详情布尔：`stock_qty <= safe_stock` |
| `min_stock` / `reorder_level` / `reorder_point` | **无运行列**；仅文案/规格意图 |
| `open_po` / in-transit qty | KPI 统计 PO 头状态；**不**进入 suggest_qty 净额 |

---

## 6. 权限边界

| 动作 | RBAC 模块 |  scope |
|---|---|---|
| 查看低库存列表/仪表盘/详情 | Inventory | view |
| 编辑 safe_stock / location | Inventory | edit |
| 库存 Adjust / Delete | Inventory | edit |
| 打开补货建议页 | Purchases | view |
| 生成 Draft PO（replenish POST） | Purchases | add |
| Draft → Open 审批 | Purchases | edit |
| 收货加库存 | Purchases | （receive 路由权限见 procurement 包） |

`apps/inventory/permissions.py` 与 `apps/procurement/permissions.py` 仅 re-export `scopes_for`；实际门在 router 的 `has_permission` 调用。

---

## 7. AI / Alerts / Runtime 交界

| 来源 | 行为 | 是否自动 PO |
|---|---|---|
| `v15/ai_operating_depth/brief.py` `_brief_inventory` | 低库存时 primary → `/purchases` | 否 |
| `v15/ai_platform/recommendations.py` | “below reorder level” 文案 → `/inventory` | 否 |
| `v15/enterprise_intelligence/risk_engine.py` | shortage risk → `/inventory` | 否 |
| `v15/ai_platform/intelligence.py` | warning alert 计数 | 否 |
| `templates/inventory*.html` | `below_safety_not_ai` 诚实标签 | 否 |
| `core/object360/warehouse/runtime.py` | 附加 dashboard 低库存 KPI | 否 |

---

## 8. 证据索引（10 条，不含源码）

| EV | 结论 | 路径 |
|---|---|---|
| EV-01 | 低库存 SQL predicate 与 safe_stock 列 | `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\repository.py` |
| EV-02 | 详情 `is_low_stock` 与服务 KPI 组装 | `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\services.py` |
| EV-03 | 补货候选 + suggest_qty 启发式 | `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\services.py` |
| EV-04 | 补货 SQL 与 limit 20 | `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\repository.py` |
| EV-05 | 路由权限 view/add/edit | `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\router.py` |
| EV-06 | Edit 仅 safe_stock+location 表单 | `H:\Workspace\EZAM_CRM - 9.0\templates\edit_inventory.html` |
| EV-07 | 补货 UI 与 suggest 列 | `H:\Workspace\EZAM_CRM - 9.0\templates\purchase_replenish.html` |
| EV-08 | V18 域门：replenish → approve，非 receive | `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V18_P3_Domain_Roll_Report.md` |
| EV-09 | A-002 门：brief 低库存 → Purchases | `H:\Workspace\EZAM_CRM - 9.0\docs\reports\Business_Strong_A002_Inventory_Report.md` |
| EV-10 | BI 低库存=products 最小库存 Top10 | `H:\Workspace\EZAM_CRM - 9.0\apps\ui_center\domain_dashboards.py` |

---

## 9. UNKNOWN（8 项 + 已查路径）

| 项 | 说明 | 已查路径 |
|---|---|---|
| U-01 | `min_stock` 是否在任一 migration/seed 存在 | `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\**` · `H:\Workspace\EZAM_CRM - 9.0\apps\product\**` · `H:\Workspace\EZAM_CRM - 9.0\core\**` |
| U-02 | EOQ 或经济批量是否在任何库存/采购计算中使用 | `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\**` · `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\**` · `H:\Workspace\EZAM_CRM - 9.0\docs\reports\**` |
| U-03 | `lead_time` 是否参与补货量或再订货点 | `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\**` · `H:\Workspace\EZAM_CRM - 9.0\apps\sample\services.py` · `H:\Workspace\EZAM_CRM - 9.0\apps\supplier\v14_residual.py` |
| U-04 | Open PO 行数量是否应从 suggest_qty 扣除 | `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\services.py` · `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\repository.py`（`fetch_open_purchase_for_product` 仅 scan receive） |
| U-05 | 未发货 SO/DO 需求是否影响低库存 | `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\**` · `H:\Workspace\EZAM_CRM - 9.0\apps\sales\**` · [`../fulfillment-deepen/reservation.md`](../fulfillment-deepen/reservation.md) |
| U-06 | `safe_stock=0` 的批量初始化或产品级默认策略 | `H:\Workspace\EZAM_CRM - 9.0\apps\product\**` · `H:\Workspace\EZAM_CRM - 9.0\business_modules\product.md` |
| U-07 | `core/inventory/metadata.py` 是否声明 reorder 字段 | `H:\Workspace\EZAM_CRM - 9.0\core\inventory\metadata.py` · `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\metadata.py` |
| U-08 | 定时/AI 自动 Draft PO 的后台任务 | `H:\Workspace\EZAM_CRM - 9.0\v15\ai_platform\automation.py` · `H:\Workspace\EZAM_CRM - 9.0\docs\design\v18\V18_IMPLEMENTATION_ROADMAP.md` |

---

## 10. 与 procurement-deepen 边界（交叉引用）

| 主题 | 本文件 | 采购深化 / ops |
|---|---|---|
| 低库存候选 predicate | SAFETY-RULE-001/007 | P-R4（[`../ops/procurement.md`](../ops/procurement.md)） |
| suggest_qty 启发式 | SAFETY-RULE-008 | P-R5 |
| Draft → Approve → Receive 分段 | SAFETY-RULE-009 | P-R7–P-R10 · [`../procurement-deepen/INDEX.md`](../procurement-deepen/INDEX.md) |
| 在途/开放 PO 净额 | SAFETY-RULE-011（无） | purchase_order / goods_receipt 深化包（待写） |
| 预留/ATP | SAFETY-RULE-011–012 | [`../fulfillment-deepen/reservation.md`](../fulfillment-deepen/reservation.md) RESERVATION-RULE-008 |

---

## 11. EAOS 重写提示（非 Legacy 继承）

1. 将 `safe_stock` 显式建模为 reorder point 或拆分为 `min_stock` + `safety_stock` + `order_up_to`，避免零阈值噪声。  
2. 补货建议应 net：on-hand + in-transit − reserved − forecast demand。  
3. 引入 lead time 与 MOQ/倍数；EOQ 仅在有 holding/order cost 数据时可选。  
4. 统一 BI 与 operational 低库存定义；禁止 `products.stock_qty ASC` 冒充 breach。  
5. 自动建议可保留 AI 提示，但 PO 创建保持人工或 workflow 门；服务端强制 Approve 后才能 Receive（消 P-V10 旁路）。
