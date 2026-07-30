# 供应商（Supplier）— Legacy Knowledge

**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Domain role:** Supplier 主数据；Procurement 通过 `supplier_id` 引用  
**Operational hub:** `/suppliers`

---

## 1. Scope 与证据强度

| 范围 | 结论 | 强度 |
|------|------|------|
| `apps/supplier` 页面、服务、持久化 | 列表、新增、详情、编辑、受保护删除、仪表盘已落地 | Strong |
| `core/supplier` | 域身份、元数据和健康脚手架已落地 | Medium |
| `apps/procurement` | PO 通过供应商 ID 关联，并提供采购统计 | Strong |
| Supplier360/企业增强 | 详情页尽力挂载，失败不影响核心 CRUD | Medium |
| `business_modules/procurement.md` | 表达边界意图，但部分路由与表为未落地目标 | Intent |

供应商模块维护身份与联系信息，不拥有采购单生命周期。采购模块读取供应商并把它写入 PO；供应商详情只读汇总其采购历史。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外/缺口 |
|----|----------|----------|-----------|
| S-R1 | 列表按供应商编号、名称、联系人、电话、WhatsApp 模糊搜索 | List | 不搜索 email/country |
| S-R2 | 列表按累计采购金额降序，而不是按名称排序 | List | |
| S-R3 | 新增、编辑和删除分别要求 Suppliers add/edit/delete 权限 | Mutation | API 脚手架未见同等页面 RBAC |
| S-R4 | 新增直接保存表单中的编号和名称；存在 SU+时间戳生成器但创建流程未调用 | Add | 编号可空 |
| S-R5 | 详情展示采购单数量、累计金额、平均采购额及采购单列表 | Detail | 聚合直接来自 `purchases` |
| S-R6 | 供应商有任一采购单时禁止删除，不区分 PO 状态 | Delete | |
| S-R7 | 无采购单时执行硬删除，不级联删除采购历史 | Delete | 未检查样品供应商匹配等其他引用 |
| S-R8 | 新增、编辑和删除在日志依赖可用时记录操作者、动作、编号与名称 | Mutation | 日志为可选注入 |
| S-R9 | 新建 PO 必须选择供应商，PO 头保存 `supplier_id` | Procurement create | 数据库外键约束未观察到 |
| S-R10 | 仪表盘区分有采购记录和无采购记录的供应商，并按采购金额排名 | Dashboard | 是派生分类，不是供应商状态 |
| S-R11 | 详情中的 A/B/C/D 分档由累计采购额阈值派生 | Detail | 仅展示启发式，不是主数据字段 |
| S-R12 | 迁移声明了等级、付款条款、信用天数和供应商状态，但主表单不维护 | CRUD | 运行数据库是否已执行迁移为 UNKNOWN |

---

## 3. 流程

### 3.1 主数据维护

供应商列表 → 权限校验 → 新增基础身份/联系字段 → 查看详情与采购汇总 → 编辑基础字段。

删除时：

1. 校验供应商存在。
2. 统计关联 PO。
3. 有 PO 则返回详情并提示阻断。
4. 无 PO 则删除供应商并记录日志。

### 3.2 与采购交界

供应商 → Procurement 创建 Draft PO → PO 行与收货流程。Supplier 模块不创建或更新 PO，只提供选择、展示和删除前存在性门。

### 3.3 现存旁路

Procurement repository 仍保留部分供应商查询，属于拆分后的交叉读取；Supplier 的运行主数据写路径在 `apps/supplier`。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| S-V1 | 供应商名称必填 | Weak/Detached | validator 有规则，但页面服务未调用；新增表单也未形成可靠服务端门 |
| S-V2 | 供应商编号唯一且非空 | Absent | 无应用查重或已观察到的 UNIQUE |
| S-V3 | email、phone、WhatsApp 格式 | Absent | |
| S-V4 | 删除前检查关联采购单 | Hard | 任一 PO 都阻断 |
| S-V5 | 删除前检查全部跨域引用 | Absent | 样品匹配等引用未纳入 |
| S-V6 | Supplier 页面 view/add/edit/delete RBAC | Hard | |
| S-V7 | Supplier API records 鉴权 | Absent/Unclear | 路由脚手架未见页面等价门 |
| S-V8 | 数据范围/租户过滤一致 | Weak | 工具方法有 scope，页面 repository 未显式体现 |
| S-V9 | 删除必须使用非 GET 的有保护命令 | Absent | Legacy 使用 GET 删除 |
| S-V10 | `purchases.supplier_id` 引用完整性 | Weak | 主要靠应用选择 |
| S-V11 | 自动供应商编号接入创建 | Absent | 生成器未调用 |
| S-V12 | 状态字段与“活跃供应商”查询一致 | Weak/Unknown | 查询使用 `status`，迁移字段为 `supplier_status` |

---

## 5. 数据含义

### 5.1 基础主数据

| Field | Meaning |
|-------|---------|
| `id` | 系统主键 |
| `supplier_code` | 供应商业务编号；Legacy 可空、可重复 |
| `supplier_name` | 供应商名称 |
| `contact_person` | 联系人 |
| `phone` | 电话 |
| `whatsapp` | WhatsApp 联系方式 |
| `email` | 邮箱 |
| `country` | 国家/地区 |
| `remark` | 备注 |

### 5.2 迁移/增强字段

| Field | Meaning | Runtime evidence |
|-------|---------|------------------|
| `supplier_level` | 供应商等级 | 主 CRUD 未维护 |
| `payment_term` | 付款条款 | 主 CRUD 未维护 |
| `credit_days` | 信用账期天数 | 主 CRUD 未维护 |
| `supplier_status` | 启用/生命周期状态 | 主 CRUD 未维护 |
| Supplier360 qualification/audit/evaluation | 资格、审计与评价视图 | 增强层，不是基础表单权威 |

### 5.3 采购派生数据

| Data | Meaning |
|------|---------|
| `po_count` | 供应商关联采购单数量 |
| `po_amount` | PO 头金额合计 |
| `avg_po` | 累计采购额除以采购单数量 |
| With PO / Idle | 是否存在采购记录的展示分类 |
| A/B/C/D band | 按累计采购额推导的展示分档 |

---

## 6. 状态词汇

| Value / family | Meaning | Evidence |
|----------------|---------|----------|
| Active | 迁移字段默认供应商状态 | Schema upgrade；主 CRUD 未使用 |
| active | API DTO 默认展示值 | 不证明数据库值 |
| With PO / Idle | 有/无采购记录 | 仪表盘派生 |
| A/B/C/D | 采购额展示分档 | 模板派生 |
| onboarded / qualified / preferred / suspended 等 | Supplier360 生命周期词汇 | 增强层，不是基础 CRUD 状态机 |

Legacy 未观察到可运行的供应商启用、停用、审核或恢复流程。

---

## 7. UNKNOWN 与核查范围

| UNKNOWN | 已核查路径/范围 |
|---------|-----------------|
| 生产数据库是否已执行供应商扩展列迁移 | `runtime/v14/legacy_support.py`；未连接运行数据库 |
| `supplier_contacts` 是否有运行表或 CRUD | 全库检索 `supplier_contacts`；仅 `business_modules/procurement.md` 声明 |
| “活跃供应商”查询在实际数据库是否成功 | `apps/procurement/repository.py` 查询 `status`；迁移声明 `supplier_status`，未运行 SQL |
| v14 残留路由实际被跳过数量 | `bootstrap/enterprise_cutover.py`、`apps/supplier/v14_residual.py`；需运行时挂载结果 |
| `/api/suppliers`、`/api/v2/suppliers` | 全库路径检索；未发现实现，仅规格目标 |

---

## 8. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `apps/supplier/router.py` | 页面路由与 RBAC | Strong |
| `apps/supplier/services.py` | 主数据维护、统计与删除保护 | Strong |
| `apps/supplier/repository.py` | 字段读写、搜索与采购聚合 | Strong |
| `apps/supplier/validator.py` | 未接线的名称校验 | Strong gap evidence |
| `apps/supplier/utils.py` | SU 编号与 scoped 查询 | Medium |
| `apps/supplier/routes.py` | API 脚手架 | Strong |
| `core/supplier/` | 域身份与元数据 | Medium |
| `apps/procurement/services.py` / `repository.py` | PO 选择和供应商引用 | Strong |
| `templates/suppliers.html` / `supplier_detail.html` | 列表、分档与采购摘要 | Medium |
| `templates/edit_supplier.html` / `supplier_dashboard.html` | 编辑字段和 KPI | Medium |
| `runtime/v14/legacy_support.py` | 基础表与扩展列定义 | Strong static |
| `business_modules/procurement.md` | Supplier/Procurement 边界意图 | Intent |
| `docs/reports/Business_Strong_A001_Supplier_Report.md` | 删除保护与采购交界 | Strong |
| `docs/reports/Business_Strong_A019_Supplier_Ops_Report.md` | 运营页面诚实性 | Strong |
| `docs/reports/V151E_Volume011_Supplier_Procurement_Business_Chain_Extraction_Report.md` | Supplier 拆分历史 | Strong historical |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
