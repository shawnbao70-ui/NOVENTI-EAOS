# 客户状态、冻结与黑名单（Customer Status Lifecycle）— Legacy Knowledge

**Evidence strength:** Medium for editable lifecycle labels; strong negative for freeze/blacklist/credit-hold enforcement  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

Legacy 客户主数据有 `customer_status` 文本字段，编辑页面提供开发中、已报价、跟进中、已成交、长期客户、暂停跟进、失效客户等选项。状态通过普通客户编辑直接覆盖，没有可观察的状态转换服务、原因、审批、生效时间或历史。

系统另有 `credit_level / credit_limit / payment_days` 扩展字段和按销售/余额计算的 UI 风险带，但它们未形成报价、订单、交付或收款的信用冻结 gate。全库可见的 blacklist 主体是 IP 地址，不是客户。未发现客户冻结、黑名单、制裁名单或解除流程。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| CS-R1 | 新客户默认状态为 `开发中` | 表单/服务默认值 |
| CS-R2 | 用户可在客户编辑中直接覆盖状态 | 无专用转换命令 |
| CS-R3 | 编辑页面状态词包括开发、报价、跟进、成交、长期、暂停和失效 | 部分值来自不稳定的 i18n 键 |
| CS-R4 | Dashboard 把 `跟进中/开发中` 计入 following | 只是统计分组 |
| CS-R5 | Dashboard 把 `已成交/长期客户` 计入 active customers | “active” 是报表口径，不是主状态 |
| CS-R6 | Opportunity Mining 却用 `Active` 或 NULL 统计 active | 与中文生命周期词并行冲突 |
| CS-R7 | `customer_statistics()` 查询 `status`，主业务使用 `customer_status` | 报告已确认字段不一致 |
| CS-R8 | 报价客户选择不按 `customer_status` 过滤 | 暂停/失效客户仍可能被选择 |
| CS-R9 | 状态不阻断订单、交付、收款或催收 | 未见跨模块 gate |
| CS-R10 | 客户余额大于 10k/100k 只产生 Needs Follow-up/Credit Watch 标签 | 启发式提示，不冻结交易 |
| CS-R11 | Credit tab 的 A/B/C/D 按累计销售额计算 | 不是持久化信用评级或授信审批 |
| CS-R12 | `credit_limit` 扩展字段存在，但当前客户编辑/详情主线未使用 | 不能推定执行授信控制 |
| CS-R13 | 未发现客户 blacklist/freeze 表或字段 | `ip_blacklist` 仅属安全中心 |
| CS-R14 | 客户删除是硬级联删除，不是失效/归档 | 会删除跟进、收款、订单和报价 |
| CS-R15 | Customer360 AI 只按余额给建议，`gateway_invoked=False` | 不执行冻结或解冻 |
| CS-R16 | Object360 faceting 展示客户状态 | 不建立生命周期状态机 |
| CS-R17 | “暂停跟进/失效客户”是标签语义 | 未见自动停用联系人、报价或订单 |
| CS-R18 | EAOS 不得把余额风险带自动提升为黑名单 | 缺少政策、授权和申诉流程 |
| CS-R19 | 客户详情入口未见 `Customers.view` 或 owner 复核 | 状态和信用信息存在对象级暴露风险 |
| CS-R20 | 新增客户可写操作日志，更新/状态覆盖和删除未见同等日志 | 生命周期审计不完整 |
| CS-R21 | Customer360 首屏中风险阈值为 10k/100k，Credit tab 中度阈值为 30k | 两套展示阈值不一致，无权威政策 |

---

## 3. Process

### 3.1 当前状态维护

1. 新建客户时默认填入 `开发中`，用户也可提交其他文本。
2. 编辑客户时从下拉框选择或提交状态。
3. 系统直接更新客户行。
4. Dashboard 按若干硬编码状态词计数。
5. 未观察到状态事件、审批、原因或历史记录。

### 3.2 当前风险提示

1. Customer360 计算订单总额减收款总额。
2. 余额超过阈值时显示 Needs Follow-up 或 Credit Watch。
3. Credit tab 同时按累计销售额显示 A/B/C/D。
4. 用户可打开 AR Reminder 或 Risk AI。
5. 这些提示不会阻断创建报价、订单、交付或收款。

### 3.3 缺失的冻结/黑名单流程

未观察到：风险识别 → 提交冻结/黑名单 → 合规/财务审批 → 阻断交易 → 通知负责人 → 定期复核 → 解除/申诉 → 保留审计历史。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| CS-V1 | 客户状态必须来自统一枚举 | Weak | UI 有选项，服务端接受任意文本 |
| CS-V2 | 状态转换必须符合前后顺序 | Missing | 任意覆盖 |
| CS-V3 | 暂停/失效需填写原因 | Missing | 无原因字段 |
| CS-V4 | 冻结/解冻需审批 | Not modeled | 无冻结命令 |
| CS-V5 | 黑名单需唯一记录、依据和有效期 | Not modeled | 无客户黑名单 |
| CS-V6 | 失效客户不得创建新报价 | Missing | 客户选择不筛状态 |
| CS-V7 | 信用余额超过限额不得新订单/交付 | Missing | credit_limit 未接 gate |
| CS-V8 | 状态统计必须使用同一字段和词汇 | Violated risk | `status` 与 `customer_status` 并行 |
| CS-V9 | 状态变更必须记录操作者和时间 | Missing | 更新无日志调用 |
| CS-V10 | 删除前必须无财务/履约记录 | Missing | 当前直接级联删除 |
| CS-V11 | IP blacklist 不得映射为客户 blacklist | Semantic guard | 主体不同 |
| CS-V12 | AI 风险建议不得执行冻结 | Hard boundary | 当前只建议 |
| CS-V13 | 页面新增/编辑必须调用客户 validator | Missing | router 直接构造表单数据 |
| CS-V14 | 客户详情必须执行模块和 owner 权限 | Missing | 列表有 gate，详情无 |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `customers.customer_status` | 可编辑客户生命周期标签 |
| `customers.status` | 部分工具期待的字段；主 DDL/主线不一致 |
| `credit_level` | 客户扩展信用等级槽位；活动维护未证实 |
| `credit_limit` | 客户扩展授信额度槽位；交易 gate 未证实 |
| `payment_days` | 客户付款天数槽位；到期驱动未证实 |
| Dashboard `following` | 开发中+跟进中的计数 |
| Dashboard `active_customers` | 已成交+长期客户的计数 |
| Opportunity `active_customers` | Active/NULL 的另一统计口径 |
| `health=healthy/watch/risk` | Customer360 按余额派生的展示健康度 |
| `Credit Watch` | 余额大于 100,000 的 UI 标签 |
| A/B/C/D credit band | 按累计销售额派生的展示档位 |
| 10k / 30k / 100k thresholds | 两个页面使用的不一致余额告警阈值 |
| `ip_blacklist` | IP 安全黑名单，与客户无关 |
| Customer360 AI recommendation | 只读建议，不是冻结决定 |
| customer freeze / hold | UNKNOWN / 未建模 |
| customer blacklist | UNKNOWN / 未建模 |
| status history | UNKNOWN / 未建模 |

---

## 6. State Vocabulary

| Value | Meaning / caveat |
|-------|------------------|
| `开发中` | 新客户默认/开发阶段 |
| `已报价` | UI 生命周期标签 |
| `跟进中` | Dashboard following 分组 |
| `已成交` | Dashboard active 分组 |
| `长期客户` | Dashboard active 分组 |
| `暂停跟进` | 标签；未见业务阻断 |
| `失效客户` | 标签；未见归档/阻断 |
| `Active` / NULL | Opportunity Mining 的并行 active 口径 |
| Healthy / Needs Follow-up / Credit Watch | 余额阈值派生提示 |
| Frozen / Blacklisted / Credit Hold | 期待执行状态；活动模型 UNKNOWN |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 客户冻结字段、表和命令 | `apps/customer/**`, customer DDL, Object360, freeze/frozen search |
| 客户黑名单及解除流程 | customer/finance/compliance paths；全库 blacklist 命中仅确认 IP 安全域 |
| `credit_limit` 由谁维护、是否阻断交易 | customer forms/services、quotation/sales/inventory services |
| 状态变更历史、原因和审批 | customer history/repository/router、approval paths |
| 暂停/失效是否应阻断报价和订单 | quotation customer picker、sales conversion、customer status searches |
| 制裁/KYC/合规名单与客户绑定 | customer/customs/compliance/security paths |
| `status` 与 `customer_status` 的真实迁移策略 | DDL upgrades、utils、dashboard、Vol007 report |
| 删除客户后的财务审计与恢复 | delete cascade、finance repositories、backup/archive searches |
| 10k 与 30k 中风险阈值哪个是权威政策 | Customer360 first、customer credit tab、AR templates/reports |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `runtime/v14/legacy_support.py` | `customer_status`/信用扩展字段；IP blacklist 与客户无关 |
| `apps/customer/services.py` | 状态随客户整体更新；余额健康提示 |
| `apps/customer/repository.py` | 冲突统计口径及无状态 gate |
| `apps/customer/utils.py` | `status` Active/Inactive 统计与主字段不一致 |
| `apps/customer/router.py` | 状态更新权限及硬删除入口 |
| `apps/customer/validator.py` | 仅 name 必填且页面 CRUD 未调用 |
| `templates/edit_customer.html` | 客户生命周期标签选项 |
| `templates/customer_detail.html` | 风险带为余额启发式 |
| `apps/quotation/repository.py` | 客户选择不按客户状态过滤 |
| `core/object360/customer/runtime.py` | 状态仅用于 facet/摘要，AI 不执行 |
| `business_modules/crm.md` | CRM 边界未定义冻结或黑名单 |
| `docs/reports/V151E_Volume007_Customer_Business_Chain_Extraction_Report.md` | 明确 status/customer_status 不一致 |
| `docs/reports/Business_Strong_A015_Customer_Ops_Report.md` | 信用展示为 heuristic、AI 不静默修改 |
| `locales/zh_CN.json` | 编辑页面状态键的中文值 |
| `templates/customers.html` | 列表状态展示与交易入口边界 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
