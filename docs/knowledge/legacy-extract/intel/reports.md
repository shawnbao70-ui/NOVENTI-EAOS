# Report Center — Legacy Knowledge

**Evidence strength:** Strong（目录表、读取路由、统计 API）/ Weak（V15.1 registry/schedule/distribution metadata）/ Missing（通用报表执行与可见目录渲染）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件覆盖 `/reports`、`/report/{id}`、`/report_dashboard`、`/api/report/statistics`，以及 report templates/categories/history/favorites/cache/queue 与 V15.1 Report Center metadata。

Legacy 路由能读取目录、分类、历史和统计，但当前 `reports.html`、`report_detail.html`、`report_dashboard.html` 是统一占位页面，未消费传入的目录数据。未找到按模板执行销售/财务查询、参数表单、导出结果、调度 worker 或邮件分发的通用闭环。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| REPORT-RULE-001 | Report Center 的 legacy 目录来自 `report_templates`，按 template_name 排序 | 存在重复 helper 定义，后加载定义可能覆盖 | Strong |
| REPORT-RULE-002 | 分类来自 `report_categories`，用于目录组织 | 当前页面未渲染分类 | Strong data / Missing UI |
| REPORT-RULE-003 | 历史来自 `report_history`，默认按 id 倒序读取 | 历史是否由真实执行写入取决于调用点 | Strong |
| REPORT-RULE-004 | `/reports` 同时装配 reports、categories、history | 模板为占位，不显示集合 | Strong |
| REPORT-RULE-005 | `/report/{id}` 按 id 读取单个模板 | 未见不存在时 404 或执行动作 | Strong |
| REPORT-RULE-006 | `/report_dashboard` 装配目录、历史和统计 | 模板 KPI 固定为 `—/Review/Ready` | Strong |
| REPORT-RULE-007 | `/api/report/statistics` 返回目录/历史等计数 | 无权限门证据 | Strong |
| REPORT-RULE-008 | legacy schema 还声明 favorites、cache、queue | 本波未找到完整用户操作和 worker 闭环 | Medium |
| REPORT-RULE-009 | V15.1 Report Center 可登记 report modules、templates、categories、dashboards、KPIs | 主要是 registry metadata | Strong metadata |
| REPORT-RULE-010 | V15.1 schedule/distribution upsert 强制 `implemented=0`，默认 `metadata_only` | 不得视为定时发送已实现 | Strong metadata |
| REPORT-RULE-011 | Repository 兼容 legacy 与 V15.1 两套 template/category/history 列名 | schema 漂移被运行时探测掩盖 | Strong |
| REPORT-RULE-012 | 财务/销售交界主要表现为独立 dashboard 和打印/NDE，而非 Report Center 执行器 | report catalog 与业务查询未找到绑定 | Strong negative boundary |
| REPORT-RULE-013 | 报表参数、日期范围、币种、组织/tenant、owner scope 为 `UNKNOWN` | 无通用参数合同 | Missing |
| REPORT-RULE-014 | 报表生成、缓存失效、队列消费、文件保存、调度和分发状态机为 `UNKNOWN` | 表名存在不足以证明执行 | Missing |

## 3. 流程

### 3.1 目录浏览

1. GET `/reports`。
2. 读取模板、分类、历史。
3. 将集合传给 `reports.html`。
4. 当前模板只显示占位 KPI、保留图表和保留时间线；目录内容未展示。

### 3.2 详情与 dashboard

- GET `/report/{id}`：读取模板记录并传给占位详情页。
- GET `/report_dashboard`：计算统计并读取模板/历史，传给占位 dashboard。
- GET `/api/report/statistics`：直接返回统计 JSON。

### 3.3 报表执行/调度

`选择模板 → 输入参数 → 查询财务/销售数据 → 生成结果 → 导出 → 记录历史 → 定时分发`

该通用闭环为 `UNKNOWN`。独立财务/销售 dashboard 与 Print/NDE 有各自运行路径，不能当作 Report Center 已执行模板的证据。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| REPORT-VAL-001 | module/template/category/dashboard/KPI/schedule/distribution key 唯一 | 强（V15.1 schema） | 只保护 metadata key |
| REPORT-VAL-002 | Repository 按列存在性选择 legacy/V15.1 查询 | 强 | 不校验语义兼容 |
| REPORT-VAL-003 | report id 存在 | 缺失 | 详情未见显式 not-found 处理 |
| REPORT-VAL-004 | Reports.view 或财务/销售权限 | 缺失/不明确 | 目录、详情、统计 API 未见权限门 |
| REPORT-VAL-005 | 查询参数类型、范围和必填 | 缺失 | 无通用执行参数 |
| REPORT-VAL-006 | 财务/销售数据 owner/tenant 过滤 | 缺失 | `UNKNOWN` |
| REPORT-VAL-007 | schedule frequency/channel 白名单 | 弱 | metadata 接收字符串 |
| REPORT-VAL-008 | 缓存 freshness、队列幂等、分发重试 | 缺失 | `UNKNOWN` |
| REPORT-VAL-009 | 导出文件权限与审计 | 缺失 | Print Center 属独立边界 |

## 5. 数据含义

| 实体 | 含义 |
|---|---|
| legacy `report_templates` | 模板目录：code/name/type 等 |
| legacy `report_categories` | 报表分类与排序 |
| legacy `report_history` | 报表历史记录 |
| `report_favorites` | 用户收藏声明；运行闭环未确认 |
| `report_cache` | 缓存存储声明；刷新规则未确认 |
| `report_queue` | 队列记录声明；消费者未确认 |
| V15.1 `report_registry` | 按模块登记报告能力 metadata |
| `dashboard_registry` / `kpi_registry` | dashboard/KPI 目录，不是计算结果 |
| `report_schedules` / `report_distributions` | 调度/分发 metadata，默认未实现 |
| NDE/Print | 业务单据打印能力，与 Report Center 模板执行不同 |

财务/销售报表的具体目录项、数据集 SQL、维度和输出格式在可执行链中未确认，标 `UNKNOWN`。

## 6. 状态词汇

| 状态 | 所属语境 | 含义 |
|---|---|---|
| `active` | report registry | metadata 条目启用标签 |
| `metadata_only` | schedule/distribution | 仅登记，未实现 |
| `implemented=0` | dashboard/KPI/schedule/distribution | 未实现 |
| `report_generated` | history 默认 event type | 生成事件词汇；不保证真实生成器存在 |
| `completed` | history 默认 status | metadata/history 默认值 |
| queued/running/failed/retrying/sent | — | `UNKNOWN`；未确认统一状态机 |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\report_center\v14_residual.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\report_center\report_api.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\report_center\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v151_report_center_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\templates\reports.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\report_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\report_dashboard.html`
- `H:\Workspace\EZAM_CRM - 9.0\apps\platform\v14_residual.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\print_center\v14_residual.py`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\analytics.md`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\V41_Print_Report_Document_Matrix.md`

**Negative search:** 已查 report template 执行器、参数 schema、销售/财务 dataset 绑定、cache invalidation、queue worker、schedule runner、distribution sender、导出历史；未找到完整通用闭环。
