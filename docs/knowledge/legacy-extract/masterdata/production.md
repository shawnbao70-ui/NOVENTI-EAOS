# 生产（Production）— Legacy 规范与落地核查

**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Honesty classification:** Intent（规范）/ Scaffold（脚手架）/ Runnable（可运行）/ Missing（未落地）

---

## 1. Scope 与证据强度

| 范围 | 结论 | 强度 |
|------|------|------|
| `business_modules/production.md` | 声明 Sample、BOM、生产订单、工单、排程和耗料目标 | Intent |
| `apps/production` / `core/production` | 目录不存在 | Missing |
| `apps/sample` / `core/sample` | 样品主链可运行，但不是制造执行模块 | Strong |
| BOM、生产订单、工单、排程、生产耗料 | 未发现表、路由、模板或服务 | Strong negative evidence |
| GTFIP production tracking | 有可运行的贸易订单生产进度记录 | Strong, separate context |
| 导航/工作区 | “Manufacturing/Production Orders” 多指向 GTFIP 或 Product/Sample 区 | Medium |

结论：`production.md` 主要是目标架构说明。Legacy 中可运行的相邻能力是 Sample 链和 GTFIP 订单生产进度；它们不能证明 BOM、工单或 MES 已落地。

---

## 2. 业务规则

| ID | 规则描述 | 分类 | 证据/缺口 |
|----|----------|------|-----------|
| M-R1 | Production 应拥有 BOM 生命周期、生产订单、工单与排程 | Intent | 仅模块规格 |
| M-R2 | Product 应拥有目录链接，Production 应拥有 BOM 结构生命周期 | Intent | 双方规格声明；无 BOM 实现 |
| M-R3 | 生产订单应使用 Approval 门 | Intent/UNKNOWN | 有依赖声明，无生产订单实体 |
| M-R4 | 生产应向 Inventory 形成材料消耗 | Intent/Missing | Inventory 规格声明依赖；无耗料写路径 |
| M-R5 | Sample 新建后状态为 New | Runnable adjacent | `apps/sample` 可运行 |
| M-R6 | Sample 绑定产品后可一次性入库，写 `Sample Receipt` 并置 Stocked | Runnable adjacent | 这是样品入库，不是生产领料或完工入库 |
| M-R7 | Sample 可转 Quote 并保留 `sample_id` 追溯 | Runnable adjacent | 实际在 Quotation 执行，URL 与 production 规范不同 |
| M-R8 | GTFIP 可维护贸易订单的工厂、物料描述、延期和完成百分比 | Runnable separate | 绑定 `gfip_orders`，不是 `production_orders` |
| M-R9 | GTFIP 进度达到完成阈值时记录完成事件 | Runnable separate | 不生成工单、BOM 或库存过账 |
| M-R10 | Production 与 Product 共享工作区或未来拥有独立 workspace | Intent/Scaffold | 当前导航混用 Product、Sample 与 GTFIP |
| M-R11 | Sample360 企业阶段不自动改写样品数据库状态 | Scaffold boundary | Shadow/enrichment 不是状态权威 |
| M-R12 | “Production Orders” 导航指向 `/gtfip` | Runnable navigation | 名称可能让用户误认 MES |

---

## 3. 流程

### 3.1 规范设想流程（未落地）

产品/BOM → 生产订单 → 审批 → 工单 → 排程 → 材料领用/消耗 → 完工入库。

该流程没有可运行证据：未发现 BOM、生产订单、工单和材料消耗实体或路由。

### 3.2 实际可运行的 Sample 相邻链

客户 → 新建 Sample → 记录测量/需求/分析/质量/供应商匹配 → 绑定产品 → 可选 Sample Receipt 入库；另一路可由 Quotation 创建带 Sample 追溯的报价。

这条链用于样品与售前，不等同于批量生产。

### 3.3 实际可运行的 GTFIP 相邻链

GTFIP 贸易订单 → 读取/更新工厂生产进度、物料描述和延期 → 完成时记录 GTFIP 事件。

它不引用 BOM、工单、生产订单表，也未观察到库存耗料或完工入库。

---

## 4. 校验

| ID | 校验 | 分类/强度 | 说明 |
|----|------|-----------|------|
| M-V1 | BOM 头、行与版本校验 | Missing | 无实体 |
| M-V2 | 生产订单数量、日期、产品与 BOM 校验 | Missing | 无实体 |
| M-V3 | 工单状态转移与排程校验 | Missing | 无实体 |
| M-V4 | 生产领料库存充足与幂等 | Missing | 无 material consumption |
| M-V5 | 生产订单 Approval 门 | UNKNOWN | `business_modules/production.md` 声明；`apps/approval` 未发现生产订单连接 |
| M-V6 | Sample 新建 customer_id | Weak/Scaffold | 表单要求，validator 存在但未稳定接入主路径 |
| M-V7 | Sample 入库要求样品存在、已绑定产品、正数量且未重复 | Runnable/Hard | 通过 Sample Receipt 台账幂等 |
| M-V8 | Sample 绑定与入库要求 Samples edit | Runnable/Hard | |
| M-V9 | GTFIP 生产进度范围与状态约束 | Partial | 有进度 API；不代表制造状态机 |

---

## 5. 数据含义

### 5.1 规范声明但未落地

| Entity | Intended meaning | Runtime finding |
|--------|------------------|-----------------|
| `bom_headers` | BOM 头、版本与产品关联 | Missing |
| `bom_items` | BOM 材料行 | Missing |
| `production_orders` | 生产订单 | Missing |
| `work_orders` | 工单 | Missing |
| `sample_items` | 样品行 | Missing |
| material consumption | 生产领料/耗料事实 | Missing |

### 5.2 可运行的相邻实体

| Entity | Meaning | Boundary |
|--------|---------|----------|
| `samples` 及 `sample_*` 子表 | 样品、测量、需求、分析、质量、供应商匹配与图片 | Sample/售前 |
| `samples.product_id` | 样品绑定目录产品 | Product 交界 |
| `quotes.sample_id` | 样品转报价追溯 | Quotation |
| `inventory_ledger` 的 `Sample Receipt` | 样品物化入库 | Inventory；非生产完工 |
| `gtfip_production` | GTFIP 贸易订单生产进度 | GTFIP；非 MES |

### 5.3 规范归属冲突

Product 规格声明 BOM 表为共享目录能力；Production 规格声明 Production 拥有 BOM 生命周期。由于 BOM 完全未落地，当前无法从运行证据判断最终所有权。

---

## 6. 状态词汇

| Value / family | Meaning | Classification |
|----------------|---------|----------------|
| New | 新建样品 | Runnable Sample |
| Stocked | 样品已物化入库 | Runnable Sample |
| received → measured → analyzed → matched → quoted → ordered → closed | Sample360 影子阶段 | Scaffold，不自动写 DB |
| `progress_pct`, `material_status`, delay | GTFIP 生产进度描述 | Runnable GTFIP |
| Production Orders / Manufacturing | 导航标签 | Scaffold/alias to GTFIP |
| Draft / Released / Scheduled / In Progress / Completed 等制造状态 | 生产订单/工单可能需要的词汇 | UNKNOWN/Missing；未发现权威枚举 |
| BOM Draft/Released/Obsolete 等 | BOM 生命周期可能需要的词汇 | UNKNOWN/Missing；未发现权威枚举 |

---

## 7. UNKNOWN 与核查范围

| UNKNOWN | 已核查路径/范围 |
|---------|-----------------|
| BOM 表、路由、模板和服务是否存在 | 全库检索 `bom_headers`、`bom_items`、`/bom/`、`bom.html`；只命中规格/导航文档 |
| 生产订单/工单是否存在 | 全库检索 `production_orders`、`work_orders`、对应模板与 DDL；无运行实现 |
| 生产材料消耗是否以其他名称存在 | `apps/inventory/**` 及全库检索 `material_consumption`、production issue/consumption 相关词；未发现生产耗料链 |
| Production Approval 规则 | `business_modules/production.md`、`apps/approval/**` 与 production-order 检索；无连接实体 |
| 运行数据库是否有代码库外遗留表 | 静态 DDL 与迁移脚本已检索；未连接实际数据库，因此仍 UNKNOWN |
| `/convert_sample_to_quotation/{id}` 是否存在别名 | 全库路径检索；实际观察到 `/create_quote_from_sample/{id}` |
| 独立 `production` workspace 是否存在 | workspace registry、导航和 manifest 检索；未发现独立可运行中心 |

---

## 8. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `business_modules/production.md` | Production 目标边界 | Intent |
| `business_modules/product.md` | BOM 共享归属声明 | Intent |
| `business_modules/inventory.md` | Production material consumption 依赖声明 | Intent |
| `apps/sample/router.py` / `services.py` / `repository.py` | 可运行 Sample 主链 | Strong |
| `core/sample/` / `core/object360/sample/` | Sample metadata 与影子阶段 | Medium |
| `apps/quotation/services.py` / `router.py` | Sample → Quote 实际交界 | Strong |
| `v15/gtfip/routes.py` / `repository.py` | GTFIP production tracking | Strong |
| `v15/gtfip/engines/production.py` | GTFIP 进度完成事件 | Strong |
| `runtime/v14/legacy_support.py` | Sample 与 GTFIP 相关 DDL；生产核心表缺失证据 | Strong static |
| `bootstrap/manifest/business_manifest.py` | Sample 挂载；无 Production app | Strong |
| `templates/samples.html` / `sample360.html` | Sample 运行界面 | Medium |
| `templates/gtfip_center.html` | GTFIP 界面 | Medium |
| `templates/components/v11/heroes/hero_manufacturing.html` | Manufacturing 导航表现 | Weak/Navigation |
| `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` | Sample/Quote 与入库链验证 | Strong |
| `docs/reports/Business_Strong_A017_Sample_Ops_Report.md` | Sample 运营诚实性 | Strong |
| `docs/reports/Volume49_Production_Cutover_Preparation_Report.md` | Production cutover 规划背景 | Intent/Historical |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.

---

## 9. 诚实结论

Legacy 没有已落地的制造 Production 模块。BOM、生产订单、工单、排程和生产耗料均为规范意图或 UNKNOWN，不得据此生成 CRUD 或状态机。可运行的 Sample 与 GTFIP 能力是相邻域，不能替代 MES 证据。
