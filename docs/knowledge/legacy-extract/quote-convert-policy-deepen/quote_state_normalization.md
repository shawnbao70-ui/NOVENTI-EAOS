# 报价中英状态归一风险（Quote State Normalization）— Legacy Knowledge

**Evidence strength:** Strong for stored writers/readers; strong negative for a canonical cross-language state machine  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块深化报价 `Draft / Sent / Negotiating / Won / Lost / 已确认 / NULL / 空字符串` 的写入者、读取者和统计分组。核心边界是：这些值并非可安全一一翻译的同一枚举。`Sent` 来自 V18 Human Approved 发布，`Won` 是手工成交标签，`已确认` 是 Convert 成功后的中文写回；三者分别表达不同事件。

报价生命周期基线交叉引用 `../quotation-deepen/quote_lifecycle.md`，此处聚焦归一化风险，不修改原文。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| QSN-R1 | 普通、样品和引导创建主要落为 Draft | Draft 是新建主状态 |
| QSN-R2 | V18 Quote Approve 只执行 Draft→Sent | Sent 表达人审发布，不证明送达 |
| QSN-R3 | 状态快捷动作只接受五个英文值 | Draft/Sent/Negotiating/Won/Lost |
| QSN-R4 | 五值动作不校验前序 | 可 Draft→Won 或 Lost→Draft |
| QSN-R5 | Convert 不要求任何特定 quote status | Draft、Lost 等也可转 |
| QSN-R6 | Convert 成功硬写中文 `已确认` | 不写 Sent 或 Won |
| QSN-R7 | `已确认` 不在五值状态白名单 | 后续快捷动作仍可覆盖为英文值 |
| QSN-R8 | Won KPI 只统计精确英文 `Won` | 已转单的 `已确认` 不计成交 |
| QSN-R9 | open KPI 只含 Draft、Sent、NULL 和空字符串 | 不含 Negotiating 或已确认 |
| QSN-R10 | 列表模板对未识别状态回退到 Draft 风格 | 外观不等于存储归一 |
| QSN-R11 | NULL/空值在 Dashboard 可被当作 open | 不是规范 Draft 写入 |
| QSN-R12 | Sent 不绑定邮件、门户送达或客户查看事件 | 只能证明本地批准动作 |
| QSN-R13 | Won 不要求已转 SO | 成交标签与订单事实分离 |
| QSN-R14 | 已确认表示曾执行 Convert，但不是稳定终态 | 可被状态菜单覆盖 |
| QSN-R15 | 复制报价生成新 Draft | 不继承源状态 |
| QSN-R16 | status 是自由文本列和直接更新 | schema 未约束枚举 |
| QSN-R17 | 报价详情、列表和 Dashboard 使用不同硬编码集合 | 同一记录可落入不同业务桶 |
| QSN-R18 | i18n 翻译只改变显示，不建立数据库映射 | 不可用语言包修复历史值 |
| QSN-R19 | `已确认` 不可安全等价为 Sent | Convert 可绕过 Approve |
| QSN-R20 | `已确认` 不可安全等价为 Won | Won 可能无 SO，已确认必有 SO |
| QSN-R21 | EAOS 迁移不得仅按中文文案做枚举映射 | 必须依据来源事件和关联 SO |
| QSN-R22 | AI semantics 将 `已确认` 视为终态，但 forewarn 的 open 排除集合未覆盖该中文值 | AI 读取层内部也存在口径漂移 |
| QSN-R23 | UI Center 复制精确英文 KPI 口径 | 状态漂移不只存在于 Quotation Dashboard |

---

## 3. Process

### 3.1 状态产生

1. 新报价写 Draft。
2. Type A Approve 在 Draft、有行和 Human Confirm 后写 Sent。
3. 状态菜单可直接覆盖任一英文白名单值。
4. Convert 忽略当前状态，成功后写已确认。
5. Copy 建立新的 Draft，不复制原状态。

### 3.2 状态消费

1. 列表按明确值显示 badge，其余回退为 Draft 风格。
2. Dashboard 分别按 Won、Negotiating、Lost、Draft/Sent/空值统计。
3. Sales 转换只按 quote ID 读取，不消费状态政策。

### 3.3 归一化诚实策略

迁移时需保留原始值、writer/source event、是否存在 SO、批准日志和时间。没有这些证据时只能标 UNKNOWN，不能把 Sent、Won、已确认合并为“Approved/Won”。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| QSN-V1 | 快捷状态必须属于英文五值 | Hard on that route | |
| QSN-V2 | Approve 前必须 Draft | Hard | |
| QSN-V3 | Approve 必须有行和 human confirm | Hard | |
| QSN-V4 | 状态转换必须符合顺序矩阵 | Missing | |
| QSN-V5 | Convert 前必须 Sent/Won | Missing | |
| QSN-V6 | `已确认` 必须映射到规范 enum | Missing | |
| QSN-V7 | NULL/空值必须在写时归一 | Missing | 仅读时回退 |
| QSN-V8 | Sent 必须绑定实际发送证据 | Missing | |
| QSN-V9 | Won 必须绑定决定人/时间/原因 | Missing | |
| QSN-V10 | 已确认必须保持 SO 关联存在 | Weak | 可通过 quote_id 推导 |
| QSN-V11 | 状态更新必须用版本条件防并发覆盖 | Missing | |
| QSN-V12 | 所有 writer 必须写统一历史事件 | Missing | 覆盖不完整 |

---

## 5. Data Semantics

| Entity / value | Honest Legacy meaning |
|----------------|-----------------------|
| `quotes.status` | 自由文本报价标签 |
| Draft | 新建/复制草稿，可进入 Type A Approve |
| Sent | 本地 Human Approved 后的发布标签 |
| Negotiating | 手工洽谈标签，无进入门 |
| Won | 手工成交标签及 KPI 计数值 |
| Lost | 手工丢单标签，可被覆盖 |
| `已确认` | Convert 成功后的中文写回 |
| NULL / `''` | 非规范旧值，Dashboard 视为 open |
| `won_quotes` | 精确 `Won` 的计数 |
| `open_quotes` | Draft/Sent/NULL/空值计数 |
| `win_rate` | Won count / total quotes |
| SO existence | `sales_orders.quote_id` 表示已转单事实 |
| Approve operation log | 人工发布动作证据，不是中心审批 |
| quote history/version | 能力槽位，未覆盖所有状态 writer |
| locale translation | 显示标签，不改变存储状态 |
| AI `_QUOTE_DONE` | 包含 confirmed/已确认的语义终态集合 |
| AI forewarn open | 另一套 open 判断，未安全归一中文已确认 |

---

## 6. State Vocabulary

| Stored value | Safe interpretation | Unsafe equivalence |
|--------------|---------------------|--------------------|
| Draft | 草稿 | 未批准 ≠ 不可转单 |
| Sent | 本地人审发布 | ≠ 实际发送/客户收到 |
| Negotiating | 洽谈标签 | ≠ 工作流阶段保证 |
| Won | 成交标签 | ≠ 已有 SO |
| Lost | 丢单标签 | ≠ 不可恢复/不可转单 |
| 已确认 | 已执行 Convert | ≠ Sent；≠ Won |
| NULL / empty | 非规范旧值 | ≠ 可靠 Draft |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| Sent 是否对应实际邮件/门户发送和送达 | quotation/communication services、templates、reports |
| Negotiating 的正式进入/退出规则 | quotation services/repository/templates |
| Won/Lost 的决定理由、操作者和时间 | quotation history/version/log paths |
| `已确认` 的原始产品意图 | sales/quotation services、i18n、business modules |
| NULL/空状态来自哪些历史 writer | runtime schema、legacy quote pages、migrations |
| 所有状态变更是否写 quote history | quotation history/utils/services、document events |
| 并发状态覆盖的最后写者策略 | repository updates、transaction/version searches |
| 过期报价应进入何种状态 | validity/scheduler/monitor searches |
| 已确认后是否允许回写 Lost/Won | status menu/service、reports；当前技术上允许 |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/quotation/services.py` | Draft 创建、五值更新、Approve→Sent |
| `apps/quotation/repository.py` | 状态直接更新及 Dashboard 口径 |
| `apps/quotation/router.py` | 状态与 Approve routes |
| `apps/quotation/quote_pages.py` | legacy writer 与 Convert 副本 |
| `apps/sales/services.py` | Convert 忽略 quote status |
| `apps/sales/repository.py` | Convert 写 `已确认` |
| `templates/quotes.html` | 列表 badge 回退与 Convert CTA |
| `templates/quote_detail.html` | 状态菜单与 Approve/Convert 表面 |
| `templates/quote_approve.html` | Draft→Sent Type A |
| `locales/zh_CN.json` | 英文状态显示翻译 |
| `business_modules/quotation.md` | 目标状态边界与漂移 |
| `docs/reports/Business_Strong_A013_Quote_Ops_Report.md` | 报价状态诚实审计 |
| `docs/reports/V18_Quote_Approve_Gate_Report.md` | Approve 与 Convert 分离 |
| `apps/ui_center/domain_dashboards.py` | 英文状态 KPI 口径复制 |
| `v15/ai_operating_depth/semantics.py` | AI 终态集合包含已确认 |
| `v15/ai_operating_depth/forewarn.py` | AI open 判断与终态集合不一致 |
| `docs/knowledge/legacy-extract/quotation-deepen/quote_lifecycle.md` | EAOS 只读交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为 EAOS 只读交叉引用）。
