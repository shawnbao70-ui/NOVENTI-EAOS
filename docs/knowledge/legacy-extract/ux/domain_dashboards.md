# Domain Dashboards — Legacy Knowledge

**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Boundary:** Dashboard 是读模型、导航与展示聚合，不是业务规则或交易状态权威

---

## 1. Scope 与证据强度

| 范围 | 结论 | 强度 |
|------|------|------|
| 各 `apps/*` dashboard router/service/repository | V17 启动顺序下的主要运行路径 | Strong |
| `apps/ui_center/domain_dashboards.py` | 大部分同名路由被 residual 去重，主要是遗留副本 | Strong |
| `/legacy_dashboard` | 可能仍由 ui_center 遗留聚合实现 | Medium/Strong |
| Role workspace | 只提供 dashboard 链接和 scope 提示 | Strong |
| BI/Report KPI registries | metadata-only，未接管实际计算 | Strong |

Domain Dashboard 不拥有 customers、quotes、SO、DO、receipts、AR/AP 或库存记录。它读取和聚合各域数据；任何状态变更与业务校验仍由所属模块负责。

---

## 2. 业务规则

| ID | 展示/聚合规则 | 触发条件 | 口径风险 |
|----|---------------|----------|----------|
| DD-R1 | 客户 dashboard 展示总数、等级、跟进/活跃、销售和收款 | View | 中文状态与 Active 语义并存 |
| DD-R2 | 报价 dashboard 按 Won/Negotiating/Lost/Open 分桶并计算 win rate | View | Open 包含 Draft/Sent/空值 |
| DD-R3 | 销售 dashboard 按 pending/completed/cancelled 分桶并计算回款率 | View | completed 可能包含“已发货” |
| DD-R4 | 发货 dashboard 统计 open/shipped/delivered 和 delivery rate | View | 遗留副本缺 shipped 桶 |
| DD-R5 | AR dashboard 以客户 SO 总额减 receipts 计算余额 | View | 与 `ar_records` 口径并行 |
| DD-R6 | Profit dashboard 以销售总额减采购总额估算毛利 | View | 不是标准 COGS |
| DD-R7 | Finance dashboard 以 sales−receipts 算 receivable、sales−purchases 算估算利润 | View | 仅展示近似 |
| DD-R8 | Receipt dashboard 以 receipts/sales 计算回款率 | View | 与 SO 头 `received_amount` 口径不同 |
| DD-R9 | Treasury 使用未付 AR/AP 计算 expected cashflow，并硬编码风险/评分阈值 | View | 展示层规则泄漏 |
| DD-R10 | Legacy dashboard 跨多业务表做全局 KPI 和财务分档 | View | 最大 global 聚合面 |
| DD-R11 | Inventory/Purchase/Supplier 等新域 dashboard 由各自服务提供 | View | 相对集中但仍需 scope 检查 |
| DD-R12 | Role workspace 只链接 dashboard，不计算 KPI | Render workspace | owner scope 未自动下推 SQL |
| DD-R13 | BI/Report KPI registry 标记未实现 | Registry | 不可当作当前 KPI 引擎 |

---

## 3. 流程

### 3.1 路由解析

Business page routers 先挂载 → 各域 dashboard 成为主要处理器 → V14 residual 后挂载并过滤重复 path → `domain_dashboards.py` 的重复路由通常不生效。

`/legacy_dashboard` 没有明显的业务 router 竞争者，因此可能仍走跨域遗留聚合。

### 3.2 Dashboard 读取

用户从 role workspace/侧边栏进入 dashboard → 路由执行 view 权限（部分页面缺失）→ service/repository 或 legacy handler 聚合业务表 → template 展示 KPI、趋势、排行与最近记录。

该流程应为只读；Dashboard 不应反向决定单据状态或审批。

### 3.3 多口径并行

- 应收：SO−receipts 与 `ar_records Unpaid`。
- 回款率：SO 头 received_amount / total 与 receipts / SO total。
- 库存价值：部分页面直接用 products 镜像，Inventory 域使用 inventory JOIN cost。

同名 KPI 必须带来源口径解释，不能跨页面直接比较。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| DD-V1 | Customer/Quote/部分 Finance dashboard 需要 view 权限 | Hard | |
| DD-V2 | Sales/Delivery/Profit dashboard 具备等价权限门 | Absent/Weak | 部分入口未见检查 |
| DD-V3 | Dashboard 查询按 tenant 过滤 | Weak/Unknown | 页面 repository 多未显式使用 scoped query |
| DD-V4 | Owner workspace KPI 按 owner 过滤 | Absent | UI scope 与 SQL 脱节 |
| DD-V5 | 状态分桶复用业务域 canonical 常量 | Absent | 多处硬编码字符串 |
| DD-V6 | 重复 dashboard 路由过滤 | Hard | 防双 handler，不消除重复逻辑 |
| DD-V7 | Meta dashboard 表名白名单 | Hard | 仍有 quotes/quotations 命名漂移 |
| DD-V8 | KPI 是只读且不写业务表 | Mostly Hard | 当前主要为 SELECT；评分规则仍越界 |
| DD-V9 | Financial score/risk 可作为业务审批依据 | Absent by design | 仅展示启发式 |

---

## 5. 数据含义

| KPI | Legacy meaning | Caveat |
|-----|----------------|--------|
| `win_rate` | Won quote 数 / 全部 quote 数 | 分母含未结束报价 |
| Sales `collection_rate` | SO 头已收镜像 / SO 总额 | 依赖镜像同步 |
| Receipt `collection_rate` | receipts 合计 / SO 总额 | 与 Sales 口径不同 |
| `total_ar` / `receivable` | SO 总额减 receipts | 不等于 `ar_records` |
| `expected_cashflow` | Unpaid AR 减 Unpaid AP | 台账型财务口径 |
| `estimated_profit` | sales 减 purchases | 展示近似，不是核算利润 |
| `delivery_rate` | Delivered DO 数 / 全部 DO 数 | 单据级，不是数量履约率 |
| `inventory_value` | 库存数量乘产品成本 | 取决于使用 products 镜像还是 inventory |
| `financial_score` / grade | 若干硬编码条件从 100 扣分 | 非财务域权威规则 |
| `risk_level` | AR/AP/余额阈值的展示分级 | 非审批门 |

Dashboard templates 还消费 recent rows、top customers/suppliers、趋势和 warning lists；这些是读模型快照。

---

## 6. 状态词汇

| Domain | Dashboard vocabulary | Drift |
|--------|----------------------|-------|
| Customer | 开发中、跟进中、已成交、长期客户、Active | 多套“活跃”含义 |
| Quote | Draft, Sent, Negotiating, Won, Lost, Open bucket | Open 是派生桶 |
| SO | Open, Pending, 已完成, Delivered, 已发货, 已取消 | completed 桶可能混入 shipped |
| DO | Pending/待出库, 已出库/Shipped, Delivered/已完成 | 遗留副本只认部分英文值 |
| AR/AP | Unpaid | 与 SO−receipts 计算型应收并行 |
| Treasury | GOOD, LOW/MEDIUM/HIGH, A/B/C/D | 展示层启发式 |
| Registry | implemented=False / metadata_only | KPI 引擎未接线 |

---

## 7. UNKNOWN 与核查范围

| UNKNOWN | 已核查路径/范围 |
|---------|-----------------|
| `/legacy_dashboard` 当前是否稳定返回 | 路由和历史报告已读；本轮未启动 HTTP，旧报告曾记录异常 |
| Business router 挂载失败时是否由 residual dashboard 接管 | bootstrap 挂载与过滤逻辑已读；未模拟失败启动 |
| 运行数据库是否所有业务表都有 tenant_id | schema/migration 与 dashboard SQL 已核查；未连接实际 DB |
| Owner scope 下推是否在 DB 连接层隐式执行 | role workspace 和 repository 查询已读；未发现明确 owner WHERE |
| EOC/CEO dashboard 的全部实时来源 | `v15/smart_business_experience` 和 UI 页面仅部分核查；超出本专题主路由范围 |

---

## 8. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `apps/ui_center/domain_dashboards.py` | 遗留 dashboard 聚合与规则泄漏 | Strong |
| `apps/ui_center/v14_residual.py` | residual 挂载 | Strong |
| `bootstrap/enterprise_cutover.py` / `v14_residual.py` | 路由优先级与去重 | Strong |
| `apps/customer/router.py` / `repository.py` | Customer dashboard 权威路径 | Strong |
| `apps/quotation/router.py` / `repository.py` | Quote dashboard 权威路径 | Strong |
| `apps/sales/router.py` / `repository.py` | Sales dashboard 权威路径 | Strong |
| `apps/inventory/router.py` / `services.py` | Inventory/Delivery dashboards | Strong |
| `apps/procurement/router.py` / `services.py` | Purchase dashboard | Strong |
| `apps/supplier/router.py` / `services.py` | Supplier dashboard | Strong |
| `apps/finance/router.py` / `services.py` | Finance/AR/AP/Treasury dashboards | Strong |
| `core/dashboard/routes.py` | Meta dashboard center | Medium |
| `services/dashboard/service.py` / `repositories/dashboard/repository.py` | Widget/layout/meta KPI | Medium |
| `core/ui/role_workspace/**` | Dashboard 导航与 scope context | Strong |
| `core/bi/kpi.py` / `core/reporting/kpi.py` | 未实现 KPI registries | Strong gap evidence |
| `business_modules/dashboard.md` | Dashboard 元模块边界 | Intent |
| `docs/reports/Residual_Decomposition_Vol024_Report.md` | dashboard residual 提取 | Medium |
| `docs/reports/_static_route_ownership.txt` | 重复路由清单 | Medium |
| `templates/*_dashboard.html` | KPI 展示与二次计算 | Medium |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.

---

## 9. 边界声明

Dashboard 中的状态桶、财务评分、风险等级和 KPI 公式仅描述 Legacy 展示口径。它们不得成为订单、库存、财务、审批或 EAOS 域规则的来源。
