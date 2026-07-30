# 产品主数据（Product）— Legacy Knowledge

**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Domain role:** Product 是目录权威；Inventory 是库存过账权威  
**Chain role:** Product → Quotation / Inventory / Procurement / Sales

---

## 1. Scope 与证据强度

| 范围 | 结论 | 强度 |
|------|------|------|
| `apps/product` 页面、服务、持久化 | 产品查询、详情、更新、删除、分类、附件、应用与智能查找已落地 | Strong |
| 新增产品 | POST 仍由 v14 residual 补洞，主 router 只有新增页面 | Strong but split |
| `core/product` | 域身份、元数据、注册和健康脚手架已落地 | Medium |
| Quotation/Inventory/Procurement | 对产品、价格和库存镜像有直接读写 | Strong |
| 模块规格中的价格层级、属性、BOM | 部分仅是目标声明 | Intent/Missing |

产品主数据权威回答“产品是谁、有什么规格、默认成本/售价是什么”。`products.stock_qty` 只是 Legacy 库存镜像；库存审计应以 `inventory` 与 `inventory_ledger` 为准。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外/缺口 |
|----|----------|----------|-----------|
| PR-R1 | 产品目录以 `products` 为主表，保存编码、名称、分类、规格、ERP 编码、材料、价格和知识字段 | CRUD | 库存字段例外，见 PR-R10 |
| PR-R2 | 列表可按编码、名称、分类、规格、ERP 编码及知识文本搜索 | List | |
| PR-R3 | 列表附加历史销售数量与金额，并按销售金额降序 | List | 统计来自 SO 行 |
| PR-R4 | 详情加载图片、附件、同类/同应用/替代产品，并按资料完整度形成展示评分 | Detail | 评分不是审批或质量结论 |
| PR-R5 | Product CRUD 的成本主档为 `cost_price`，销售价主档为 `sale_price` | Update | 另有 `selling_price` 命名路径，未统一 |
| PR-R6 | 报价加行以产品为目录来源；行成本缺失或非正时回退主档成本 | Quote item add | |
| PR-R7 | 报价售价按成本和利润率计算，不直接采用产品 `sale_price` | Quote item add | 利润率 100 的保护不明确 |
| PR-R8 | 报价行保存成本、价格以及部分材料规格快照，后续主档变化不自动回写 | Quote item add | 通用 `specification` 未形成完整版本快照 |
| PR-R9 | 采购补货使用产品成本价作为建议行默认成本；采购行保留自己的交易成本 | Replenish/PO item | 收货不回写产品主档成本 |
| PR-R10 | `products.stock_qty` 是镜像：库存调整、PO 收货、DO Ship、样品入库会同步增减 | Stock posting | 同时还可被产品表单直接覆盖 |
| PR-R11 | 缺少库存记录时，可以产品库存镜像作为新库存记录基线 | Inventory ensure | 镜像若已漂移会污染新记录 |
| PR-R12 | 产品详情的 Healthy/Low/Critical 基于产品镜像数量阈值计算 | Detail | 不一定等于库存台账余额 |
| PR-R13 | 产品删除先清理图片记录和文件，再硬删产品 | Delete | 未检查报价、订单、采购、库存引用 |
| PR-R14 | 分类、别名、知识、应用场景、图片和附件作为产品卫星数据存在 | Auxiliary pages | 权限覆盖不一致 |
| PR-R15 | Smart Lookup 通过产品编码、ERP 编码、名称和关键词匹配，并可跳转库存扫码 | Lookup | 图片识别实际只用文件名 token，不是 OCR |
| PR-R16 | 成本价在列表 UI 受额外 Cost Price view 门控 | View | 后端更新仍可接受成本价 |

---

## 3. 流程

### 3.1 产品维护

列表/搜索 → 查看产品与销售统计 → 编辑目录字段、默认价格和知识字段 → 可维护图片、附件、分类与应用。

新增路径仍由残留路由接收表单并写入产品；更新走当前 Product 服务；删除不做跨模块引用保护。

### 3.2 产品 → 报价

选择产品 → 读取目录身份、材料、成本、销售价和库存镜像 → 成本为空时回退主档成本 → 依据利润率计算报价单价 → 将交易快照写入报价行。

报价不回写产品价格或规格。

### 3.3 产品 → 库存

产品提供 SKU 身份与成本估值 → Inventory 保存现存量与台账 → 正规收发/调整同步 `products.stock_qty` 镜像。

产品表单直接写镜像是旁路，不产生库存台账。

### 3.4 产品 → 采购

低库存候选由 Inventory 提供 → Procurement 读取产品身份与主档成本 → 建采购行交易成本 → 收货只改库存及其镜像，不更新主档成本。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| PR-V1 | 产品编码和名称必填 | Weak/Detached | validator 有规则，但主页面新增/更新未可靠接线 |
| PR-V2 | 产品编码唯一 | Absent | 无应用查重或已观察到的 UNIQUE |
| PR-V3 | 主 CRUD 的 Products view/add/edit/delete RBAC | Hard | 新增分散在 residual |
| PR-V4 | 成本价读取权限 | Medium | 主要是 UI 隐藏 |
| PR-V5 | 图片/文档上传安全校验 | Hard | 使用上传类型与文件名校验 |
| PR-V6 | 删除前跨模块引用检查 | Absent | 可能留下或破坏引用 |
| PR-V7 | `sale_price >= cost_price` | Absent | 仅有事后异常告警 |
| PR-V8 | 产品库存镜像与库存台账一致 | Absent | 无自动对账 |
| PR-V9 | 产品表单不得直接改库存 | Absent | 可直接覆盖镜像 |
| PR-V10 | 报价利润率不能导致除零 | Weak/Unknown | 已核查 `apps/quotation/services.py` 公式，未见明确 100% 门 |
| PR-V11 | 分类、应用、附件等辅助路由统一 RBAC | Weak | 多个辅助路由未见主 CRUD 等价检查 |
| PR-V12 | 租户范围在页面 repository 一致执行 | Weak/Unknown | scoped 工具有过滤，页面 SQL 未显式体现 |

---

## 5. 数据含义

### 5.1 产品主档

| Field | Meaning |
|-------|---------|
| `product_code` | 产品业务编码 |
| `product_name` | 产品名称 |
| `category` | 自由文本分类 |
| `specification` | 通用规格描述 |
| `erp_code` | ERP/外部编码 |
| `pitch`, `teeth`, `width`, `length` | 传动类规格 |
| `material`, `hardness` | 材料与硬度 |
| `cost_price` | 目录默认成本 |
| `sale_price` | 目录默认销售价 |
| `stock_qty` | 库存镜像/快捷显示，不是库存审计事实 |
| `keywords`, `application`, `alternative_model`, `technical_notes` | 搜索、应用与替代知识 |
| `remark` | 备注 |

### 5.2 价格交界

| Data | Meaning |
|------|---------|
| `products.cost_price` | 目录默认成本；报价/补货的回退或建议值 |
| `products.sale_price` | 主 CRUD 维护的目录销售价 |
| `quote_items.cost_price` / `price` | 报价交易快照 |
| `purchase_items.cost_price` | 采购交易成本，不自动更新主档 |
| `product_price_rules.selling_price` | 并行规则表字段；与 `sale_price` 命名分裂 |
| `product_costing` | 分项成本核算结构；现有页面能力偏脚手架 |

### 5.3 库存交界

| Data | Meaning |
|------|---------|
| `inventory.stock_qty` | 库存操作余额 |
| `inventory_ledger` | 收发、调整的审计流水 |
| `products.stock_qty` | 产品目录中的库存镜像和缺行初始化种子 |

### 5.4 卫星数据

`product_categories`、`product_images`、`product_files`、`product_aliases`、`product_knowledge`、`product_applications` 已观察到运行读写。规格声明的 `product_prices`、`product_attributes` 与 BOM 表未观察到对应实现。

---

## 6. 状态词汇

| Value / family | Meaning | Authority |
|----------------|---------|-----------|
| Healthy / Low Stock / Critical | 基于产品库存镜像的详情展示等级 | UI 派生 |
| Active / Inactive | 部分工具使用的产品启停值 | 未统一到主 CRUD |
| `product_status` / `status` | 并存的状态列名 | 未统一 |
| DO Ship / PO Receipt / Manual Adjustment / Sample Receipt | 库存台账交易类型 | Inventory |
| Draft/Sent/Won 等 | 报价状态，不是产品状态 | Quotation |

未观察到产品主档中完整、受校验的 Active → Inactive/Discontinued 生命周期。

---

## 7. UNKNOWN 与核查范围

| UNKNOWN | 已核查路径/范围 |
|---------|-----------------|
| `product_prices`、`product_attributes` 是否落地 | 全库名称与 DDL 检索；仅 `business_modules/product.md` 声明 |
| `bom_headers`、`bom_items` 是否由 Product 实现 | 全库名称、路由、模板与 DDL 检索；未发现运行实现 |
| `sale_price` 与 `selling_price` 的最终权威 | `apps/product/utils.py`、主 CRUD、`product_price_rules` DDL；未统一 |
| `status` 与 `product_status` 的最终权威 | 产品升级列和工具查询；主 CRUD 未形成状态机 |
| 运行数据库中的实际列集合 | `runtime/v14/legacy_support.py` 与补丁；未连接运行数据库 |
| `/api/products`、`/api/v2/products` | `apps/product/routes.py` 与全库路径检索；未发现，与规格目标不一致 |

---

## 8. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `apps/product/router.py` | 主页面路由与权限 | Strong |
| `apps/product/services.py` | 列表、详情、更新、删除、查找规则 | Strong |
| `apps/product/repository.py` | 产品与卫星表读写 | Strong |
| `apps/product/validator.py` | 未接线的编码/名称校验 | Strong gap evidence |
| `apps/product/v14_residual.py` | POST 新增补洞与残留页面 | Strong |
| `apps/product/utils.py` | Legacy 新增、状态与价格写入 | Medium |
| `core/product/` | 域身份与元数据 | Medium |
| `apps/quotation/services.py` / `repository.py` | 产品到报价的成本和快照交界 | Strong |
| `apps/inventory/services.py` / `repository.py` | 库存权威与产品镜像同步 | Strong |
| `apps/procurement/services.py` / `repository.py` | 补货成本、采购行与收货 | Strong |
| `templates/products.html` / `product_detail.html` | 字段、成本权限和库存提示 | Medium |
| `templates/product_lookup.html` | Smart Lookup 行为 | Medium |
| `runtime/v14/legacy_support.py` | 主表与价格/成本结构 | Strong static |
| `business_modules/product.md` | Product 边界与未落地目标 | Intent |
| `docs/reports/V151E_Volume008_Product_Business_Chain_Extraction_Report.md` | Product 提取历史 | Strong historical |
| `docs/reports/Business_Strong_A016_Product_Ops_Report.md` | 产品运营诚实性 | Strong |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
