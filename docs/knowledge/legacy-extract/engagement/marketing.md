# Marketing — Legacy Knowledge

**Evidence strength:** Medium — distributor operations are observable; campaign, lead, journey and send capabilities are mostly schema/registry shells  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块覆盖 `/marketing_center`、`apps/marketing`、V15 Marketing connector registry，以及被 Marketing Hub 作为主要运营入口的 Distributor Center。

Legacy 的“Marketing”不是一套完整营销自动化产品：

- Hub 展示八类渠道注册位，但默认全部未配置；
- Hub 的 live campaign 与 new lead 数明确为零；
- `campaigns` 有建表和只读 records API，但没有活动的生产 Campaign CRUD、受众分群、发送、回执或归因闭环；
- 最强的可运行能力是经销商主数据、等级、客户关联、佣金/结算展示和搜索。

---

## 2. 业务规则

| ID | 规则描述 | 证据 / 缺口 |
|----|----------|-------------|
| MKT-R1 | Marketing Hub 固定链接为 `/marketing_center` | 活动 HTML 路由 |
| MKT-R2 | 渠道清单是 architecture registry，不代表连接可用 | 页面明确显示 `not connected` |
| MKT-R3 | 注册渠道包括 WhatsApp、Email、Facebook、Instagram、LinkedIn、TikTok、Google Business、Website Leads | 仅注册名称与类型 |
| MKT-R4 | Connector 默认状态为 `not_configured`，配置键为空 | 未见凭证或发送管线 |
| MKT-R5 | Hub 的活动 Campaign 和近七日 Lead 数当前固定为 0 | 不从 `campaigns` 或 lead 事实计算 |
| MKT-R6 | 页面不得宣称自动建立 Campaign、Lead、Journey 或 WhatsApp blast | 诚实性报告与页面边界 |
| MKT-R7 | `campaigns` 表可保存名称、渠道、状态、lead_count、预算和日期 | 仅见 schema、列表和计数 |
| MKT-R8 | Campaign records API 只读返回有限条记录 | 未见创建、修改、发送或状态推进 API |
| MKT-R9 | Campaign API DTO 默认 `status=active`，数据库默认 `draft` | 状态默认值不一致，不能推断真实生命周期 |
| MKT-R10 | 经销商具有唯一编号、国家、等级、联系人、信用额度、余额和状态 | 活动 Legacy 表与页面 |
| MKT-R11 | 经销商等级包含折扣率、目标金额和佣金率 | 是否自动应用到报价/订单 UNKNOWN |
| MKT-R12 | 经销商可创建、编辑、搜索和删除 | 活动 residual handlers |
| MKT-R13 | 更新经销商时可维护名称、等级、联系人、地址和状态 | 未观察到字段级审批 |
| MKT-R14 | Distributor detail 可展示佣金与 settlement 信息 | 与 Finance Commission 的一致性/主账归属 UNKNOWN |
| MKT-R15 | Marketing Hub 只导航到 Distributor、Customer、Communication 和 Quote 等工作区 | 导航不等于自动同步 |
| MKT-R16 | AI 不得从 Hub 静默创建 Campaign、Lead 或群发 | 页面硬边界 |
| MKT-R17 | Journey map、转化归因、退订、同意管理、频控、模板审批均 UNKNOWN | 已检索 `apps/marketing/`、`v15/marketing/`、Marketing 模板和运行时表 |

---

## 3. 流程

### 3.1 当前 Marketing Hub

1. 打开 `/marketing_center`。
2. 读取固定的 connector registry。
3. 显示渠道槽位，并明确为未连接。
4. 显示 0 个 live campaign 与 0 个 new lead。
5. 用户可人工跳转到 Distributor、Customer、Communication 或 Quote。
6. Hub 本身不创建 Campaign、不导入 Lead、不发送消息。

### 3.2 经销商运营

1. 查看经销商列表和等级选项。
2. 人工新增经销商及联系信息。
3. 在详情页查看佣金/结算派生信息。
4. 可更新经销商资料与 Active 等状态。
5. 可按名称、联系人、电话或邮箱搜索。
6. 删除为直接数据库删除；页面层有人类确认提示，但服务端未见审批流程。

### 3.3 Campaign 数据壳

1. 初始化 Marketing repository 时尝试确保 `campaigns` 表存在。
2. Records API 可列出和计数 Campaign 行。
3. **流程终止**：没有活动创建表单、受众选择、审批、调度、发送、回执、Lead 转化或效果归因。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| MKT-V1 | Campaign 名称非空 | Schema-level | 表定义要求；无活动创建路径 |
| MKT-V2 | Campaign 状态必须来自统一枚举 | Missing | DTO、表默认值与 V15 enum 不一致 |
| MKT-V3 | Campaign limit 参数范围 | UNKNOWN | 列表 API 接受 limit，未见业务范围限制 |
| MKT-V4 | 经销商名称、国家、等级必填 | Form-level | 服务端业务校验证据有限 |
| MKT-V5 | 经销商编号唯一 | Database-level | 表字段唯一 |
| MKT-V6 | 经销商等级代码必须有效 | UNKNOWN | 未确认 FK 或显式拒绝 |
| MKT-V7 | 经销商删除需 Human Confirm | UI only | 删除端点为 GET，缺少服务端确认令牌 |
| MKT-V8 | Campaign 发布前需内容/预算/合规审批 | Missing |
| MKT-V9 | 发送渠道必须已配置且健康 | Not implemented |
| MKT-V10 | Lead 同意、退订与地区合规 | Not implemented |
| MKT-V11 | 预算、日期区间和负值校验 | UNKNOWN | 已检索 Campaign schema/repository/routes |
| MKT-V12 | Marketing AI 建议不得直接写业务事实 | Hard boundary in page/report |

---

## 5. 数据含义

| Entity / field | 含义 |
|----------------|------|
| `campaigns` | Campaign 元数据壳；不证明已发送 |
| Campaign `channel` | 计划使用的渠道标签；不证明 connector 已连接 |
| Campaign `status` | 规划生命周期；活动推进机制未见 |
| Campaign `lead_count` | 可存储的计数字段；来源与去重规则 UNKNOWN |
| `MARKETING_CONNECTORS` | 八个架构注册项 |
| `distributor_levels` | 经销等级、折扣目标与佣金参数 |
| `distributors` | 合作渠道主数据 |
| `distributor_customers` | 经销商与客户关联 |
| `distributor_commission` | 经销佣金记录 |
| “New leads (7d)” | Hub 当前固定为零，不是可靠数据集 |

---

## 6. 状态词汇

| Status | 使用位置 | 含义 |
|--------|----------|------|
| `not_configured` | Connector | 仅注册，未连接 |
| `draft` | Campaign 表 / enum | 草稿 |
| `scheduled` | V15 Campaign enum | 计划状态；推进器未见 |
| `active` | DTO / enum | 活动；DTO 默认不证明事实 |
| `paused` | V15 Campaign enum | 暂停；操作流程未见 |
| `completed` | V15 Campaign enum | 完成；完成判据未见 |
| `Active` | Distributor / level | 活动主数据 |

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `templates/marketing_center.html` | Hub 诚实边界、KPI 与导航 |
| `apps/master/v14_residual.py` | `/marketing_center` 活动路由 |
| `runtime/v14/legacy_support.py` | Hub context、Distributor 表与业务 helpers |
| `v15/marketing/center.py` | Connector registry、Campaign 状态枚举与空列表 |
| `apps/marketing/schema.py` | Campaign 数据结构 |
| `apps/marketing/repository.py` | Campaign 只读列表和计数 |
| `apps/marketing/routes.py` | health/records/workspace API |
| `apps/marketing/workspace.py` | metadata-only 迁移声明 |
| `apps/marketing/v14_residual.py` | Distributor CRUD/search/dashboard |
| `apps/marketing/marketing_api.py` | Distributor JSON 查询 |
| `docs/reports/Business_Strong_A024_Marketing_Ops_Report.md` | Marketing 诚实性审计 |
| `templates/distributors.html` / `distributor_detail.html` / `distributor_dashboard.html` | 经销运营表面 |
| `apps/marketing/` / `v15/marketing/` / Marketing templates | UNKNOWN 检索范围 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
