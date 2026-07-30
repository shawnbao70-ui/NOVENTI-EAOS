# Sample360 观察与缺口 — Legacy Knowledge

**Evidence strength:** Strong（旧页面查询与保存）/ Medium（Sample detail 并行 runtime）/ Missing（统一生命周期、发样与审计闭环）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件覆盖 `/sample360/{sample_id}` 页面、其分析区块，以及 `/sample/{sample_id}` 详情上并行生成的 `_sample360_runtime`。样品主流程见 [../sample/sample.md](../sample/sample.md)，发样/POD 缺口见 [../sample/outbound.md](../sample/outbound.md) 和 [../sample/pod.md](../sample/pod.md)。

旧 Sample360 页面有真实查询与保存能力；但 Object360 runtime hook 接在普通 sample detail context，未见 `/sample360/{id}` 页面消费 `_sample360_runtime`。因此“旧 Sample360 页面”和“并行 Sample360 bundle”是两层证据，不可合并为统一平台已接管。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 证据强度 |
|---|---|---|
| SAMPLE360-RULE-001 | `/sample360/{id}` 以样品为中心连接客户名称，并读取最近一条测量、需求、材料分析和质量评估 | Strong |
| SAMPLE360-RULE-002 | 供应商匹配读取全部匹配记录并装配供应商名称；另加载供应商清单，但当前模板不展示这些 context | Strong |
| SAMPLE360-RULE-003 | 样品需求、材料分析、质量评估和供应商匹配各有独立 POST 路由；当前 templates 未找到对应表单 | Strong（端点）/ Strong negative（UI） |
| SAMPLE360-RULE-004 | 页面可绑定目录产品；仅绑定产品且未物化时显示入库动作 | Strong |
| SAMPLE360-RULE-005 | 物化以 `Sample Receipt` 增加库存并把样品状态改为 `Stocked`；这不是客户发样 | Strong |
| SAMPLE360-RULE-006 | 页面可跳转从样品创建报价，追溯和权限缺口以 sample 知识包为准 | Strong |
| SAMPLE360-RULE-007 | 当前 service context 未装配 template 使用的 `images`、`materials`、`logs`，相应图片区、材料表和 Timeline 可能只显示空态 | Strong negative |
| SAMPLE360-RULE-008 | 普通 sample detail 会用 sample、最近测量和 images 构造并行 runtime bundle；失败不阻断旧详情 | Medium |
| SAMPLE360-RULE-009 | 并行 bundle 派生 identity、lifecycle、measurement、relationship、knowledge、search、AI 等 section；其 AI 标记并不等于业务执行 | Medium |
| SAMPLE360-RULE-010 | shadow helper 明示 template 当时不消费 `_sample360`；runtime 后续由 adapter 复用 shadow 构建逻辑 | Strong |
| SAMPLE360-RULE-011 | Sample360 未形成申请、审批、备样、发出、签收/POD 的可执行闭环 | Missing |
| SAMPLE360-RULE-012 | 相关报价/订单在并行 relationship 中是否真实装配为 `UNKNOWN` | Missing；已查 sample detail context 未见 `related_quotations` / `related_orders` |
| SAMPLE360-RULE-013 | Enterprise360 registry 可识别 `/sample360/{id}` 与 `/sample/{id}`，但未见 Sample360 专用业务 API | Medium / Strong negative |
| SAMPLE360-RULE-014 | lifecycle 面板直接装配客户、业务需求和关联报价；未直接装配商机链接，`opportunity_id` 主要用于转报价传播 | Strong / Medium |

## 3. 流程

### 3.1 旧 Sample360 页面

1. 请求 `/sample360/{sample_id}`。
2. 读取样品和客户名称。
3. 分别读取最近测量、最近样品需求、最近材料分析、最近质量评估、供应商匹配及供应商清单。
4. 判断产品绑定与是否已有 `Sample Receipt`。
5. 后端 POST 端点可保存分析区块，但当前模板未提供对应表单；页面可绑定产品、执行入库物化或转报价。
6. 保存后重定向回 Sample360。

### 3.2 并行 runtime

1. 普通 `/sample/{id}` 详情先装配样品、最近测量和图片。
2. 服务尝试生成 `_sample360_runtime`。
3. runtime 复用 shadow/integration builder 派生多个 context。
4. Legacy detail renderer 保持权威；hook 异常被隔离。

申请 → 审批 → 发样 → POD：`UNKNOWN`，已查 `apps/sample/`、`core/object360/sample/`、相关 templates 与 runtime docs。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| SAMPLE360-VAL-001 | `sample_id` 为整数 | 强（HTTP 类型） | Sample360 service 未显式处理样品不存在 |
| SAMPLE360-VAL-002 | 保存分析时样品必须存在 | 缺失/不明确 | 未见统一对象存在校验 |
| SAMPLE360-VAL-003 | 产品绑定必须 `product_id > 0` | 强 | 缺失时返回 bind error |
| SAMPLE360-VAL-004 | 物化前必须有产品、数量 > 0 且未重复物化 | 强 | 以库存台账判重 |
| SAMPLE360-VAL-005 | 分析评分、目标价、年需求和风险等级范围 | 弱/缺失 | 未见统一业务区间 |
| SAMPLE360-VAL-006 | 绑定产品与物化权限 | 强 | router 要求 `Samples.edit` |
| SAMPLE360-VAL-007 | runtime context 与页面字段一致 | 弱 | 两者使用不同入口和输入 context |
| SAMPLE360-VAL-008 | Timeline 完整性 | 缺失 | 页面 service 未装配 `logs` |
| SAMPLE360-VAL-009 | Sample360 页面访问权限 | 缺失 | GET 路由未见统一权限门 |
| SAMPLE360-VAL-010 | 分析类 POST 的页面可操作性 | 缺失 | 路由存在，但 templates 未找到对应表单 |

## 5. 数据含义

| 数据/区块 | 业务含义 |
|---|---|
| `sample` | 样品主记录及客户名称 |
| `measurement` | 最新一条尺寸、重量、节距、齿数、材质、硬度 |
| `sample_requirements` | 样品层应用、环境、寿命、目标价等描述；service 读取，当前模板不展示；不是业务需求主表 |
| `sample_material_analysis` | 材质、等级与风险分析；service 读取，模板使用不匹配的 `materials` 变量 |
| `sample_quality_assessment` | 多项质量评分及 overall grade；service 读取，当前模板不展示 |
| `sample_supplier_matching` | 候选供应商、价格、MOQ、交期、质量评分；service 读取，当前模板不展示 |
| `sample_product_id` / `sample_materialized` | 目录产品绑定与是否已通过 Sample Receipt 入库 |
| `_sample360_runtime` | 普通样品详情的并行派生 bundle，不是 Sample360 页面持久模型 |
| `sample_logs` | 可表达 action/remark/operator/time，但当前 Sample360 context 未读取 |

## 6. 状态词汇

| 词汇 | 含义/限制 |
|---|---|
| `New` | Legacy 新收样品 |
| `Stocked` | 已作为 Sample Receipt 入库；不是已发样 |
| shadow | 早期并行装配模式，template 明示未消费 |
| runtime / skipped | runtime bundle 模式，不是样品业务状态 |
| lifecycle stage | Object360 builder 派生词汇；不得覆盖 Legacy 已证状态 |
| approved / dispatched / delivered / POD | `UNKNOWN`；未见 Sample360 可执行转换 |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\routes.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\history.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sample\utils.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample360.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\sample_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\runtime.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\runtime_context.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\shadow.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\sample_integration.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\object360\sample\sample_context.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\context360.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\enterprise360\registry.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\runtime\Sample360_Runtime_Integration.md`
