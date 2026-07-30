# AI Advisory Surfaces — Legacy Knowledge

**Evidence strength:** Strong for metadata/static advisory boundaries; Medium for per-object heuristic analyses; no evidence of autonomous decision authority  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块只记录面向用户的 AI 顾问类表面：`/ai_decision_center`、V15.1 AI Decision registry，以及产品、样品、报价、客户、销售和 CRM 的搜索/分析/建议页面。

这些表面混合了四种不同能力：

1. **静态页面文案**：固定分数、风险级别和建议；
2. **数据库检索/启发式计算**：从业务表读取后生成评分或标签；
3. **Metadata registry**：登记模块、策略、建议、预测、风险和场景；
4. **对话/导航表面**：回答、解释或引导用户打开业务工作区。

本模块的绝对边界：

- Advisory 只可解释、分析、建议、草拟或导航；
- Advisory **≠ Brain execute**；
- Advisory **≠ Twin authorize**；
- Advisory **≠ Cap→grant**；
- 建议、置信度和风险标签不授予业务写权限，也不绕过目标模块审批。

---

## 2. 业务规则

| ID | 规则描述 | 证据 / 缺口 |
|----|----------|-------------|
| AIA-R1 | `/ai_decision_center` 是 Legacy 静态决策支持页 | 分数 92/88/90/86/89/89 为模板常量 |
| AIA-R2 | 页面中的销售、采购、风险和 recommended actions 是通用建议文本 | 不随运行数据计算 |
| AIA-R3 | Roadmap 对若干中心显示完成标记，不证明对应决策引擎已实现 | 页面同时列预测/forecast 为 next |
| AIA-R4 | V15.1 AI Decision Center 是 additive metadata standard | 报告明确无 reasoning/prediction implementation |
| AIA-R5 | V15.1 默认未启用，且不替代已有 AI 工作流 | `enabled_by_default=False` |
| AIA-R6 | Registry 涵盖 Sales、Purchase、Inventory、Finance、Production、Customer、Supplier、Logistics、Risk、Executive | 模块注册不等于各域模型已运行 |
| AIA-R7 | Strategy、Recommendation、Prediction、Risk、Scenario 持久化时强制 `implemented=0` | 默认状态 `metadata_only` |
| AIA-R8 | Decision History 可记录 registry/history 事件 | 不等于业务决策已执行 |
| AIA-R9 | Decision Center 对外 API 只提供 health | 其他列表供 framework context，不是执行接口 |
| AIA-R10 | Product search 本质上是多字段数据库搜索 | 不应标为模型推理 |
| AIA-R11 | CRM assistant 的推荐列表由最近客户行拼装，动作/风险为通用占位 | overdue/opportunity 指标当前为零 |
| AIA-R12 | Sales assistant POST 返回固定机会分 75 与“24小时内报价”动作 | 输入产品被原样作为 recommended product |
| AIA-R13 | 产品、样品、材料、报价、客户页面可调用 Legacy helper 生成分析 | 算法多为启发式；异常时降级为 Unknown/空列表/错误文本 |
| AIA-R14 | AI Search、Assistant 和 Chat 可返回检索或回答结果 | 来源、模型、版本和引用完整度依场景而异 |
| AIA-R15 | AI 建议可以形成 working task/adopt-ignore 反馈 | 反馈面板明确 `mutates_facts=False`；任务不等于业务写入 |
| AIA-R16 | 建议被采纳后，实际业务动作仍需在目标工作区按权限和审批完成 | 不允许静默 mutation |
| AIA-R17 | 失败通常降级为空、Unknown、通用说明或页面仍可打开 | 不应把降级值当作低风险结论 |
| AIA-R18 | 置信度字段只是 advisory metadata | 未观察到统一校准、数据漂移或阈值治理 |
| AIA-R19 | AI 输出不得修改审批、财务、库存、客户、报价等事实 | 人类责任与业务模块边界 |
| AIA-R20 | AI 表面不具备授权、能力授予或数字孪生批准语义 | 绝对硬边界 |
| AIA-R21 | 部分 Legacy 客户分析使用固定 credit score/level，报价、样品和材料分析使用 Waiting/Unknown/0 confidence 占位 | 不能当作模型测算 |
| AIA-R22 | `create_task` 最多建立 AI Working / Digital Employee 待办 | 不执行报价审批、订单转换、库存过账或其他业务事务 |

---

## 3. 流程

### 3.1 Legacy Decision Center

1. 用户打开 `/ai_decision_center`。
2. 系统渲染固定 executive score。
3. 展示固定销售/采购建议和风险等级。
4. 展示 recommended actions 文案。
5. 用户可导航到其他工作区。
6. 页面本身不读取事实计算分数，也不执行建议。

### 3.2 V15.1 Metadata Registry

1. 初始化时确保七张 additive 表存在。
2. 从 core registry seed 决策模块、策略、建议、预测、风险和场景 metadata。
3. 所有策略型记录标为 `implemented=0` / `metadata_only`。
4. Framework page 和 health API展示注册与健康信息。
5. 不调用推理引擎，不预测，不写业务对象。

### 3.3 对象级顾问页面

1. 用户从产品、样品、报价、客户等对象打开分析页。
2. helper 读取对象及相关业务数据。
3. 生成推荐、评分、风险或知识关联。
4. 异常时返回空值、Unknown 或错误说明。
5. 用户自行判断并进入目标业务流程。
6. 顾问页不拥有目标对象的写授权。

### 3.4 建议反馈

1. 用户看到建议或任务。
2. 可 Adopt 或 Ignore，用于反馈计数。
3. Dashboard 聚合采纳/忽略趋势。
4. 反馈不修改业务事实。
5. 如需行动，仍由用户进入目标模块。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| AIA-V1 | Registry module_key/strategy_key 等唯一 | Database-level |
| AIA-V2 | Strategy/Recommendation/Prediction/Risk/Scenario 必须保持 implemented=0 | Hard in repository seed |
| AIA-V3 | Metadata 状态默认 `metadata_only` | Database/service |
| AIA-V4 | 对象 ID 必须存在 | Weak | 异常通常降级显示 |
| AIA-V5 | 置信度必须在统一范围并经过校准 | UNKNOWN |
| AIA-V6 | 建议必须标注来源、算法、时间和数据范围 | Inconsistent / missing |
| AIA-V7 | 静态分数必须明确为 demo/constant | Missing on Legacy template |
| AIA-V8 | Unknown/异常不得显示为安全或通过 | Required boundary；现有降级表达不统一 |
| AIA-V9 | 建议采纳不得直接修改业务事实 | Hard boundary |
| AIA-V10 | 业务动作必须重新执行目标模块权限/审批 | Required boundary |
| AIA-V11 | AI History 不能冒充业务审计日志 | Semantic boundary |
| AIA-V12 | 敏感数据访问需与原业务对象同粒度权限 | UNKNOWN / inconsistent |
| AIA-V13 | AI 输出不得授予能力或授权 | Absolute boundary |
| AIA-V14 | 建议不得等同 Brain execute、Twin authorize、Cap→grant | Absolute boundary |
| AIA-V15 | Prediction/optimization/scenario 输出真实性 | Not implemented in V15.1 registry |

---

## 5. 数据含义

| Entity / concept | 含义 |
|------------------|------|
| `ai_decision_registry` | 可提供决策支持的业务模块 metadata |
| `ai_decision_strategy` | 策略目录；`implemented=0` |
| `ai_decision_recommendation` | 建议类型目录；不是具体已执行建议 |
| `ai_decision_prediction` | 预测能力目录；无预测引擎 |
| `ai_decision_risk` | 风险类型目录；不是实时风险事实 |
| `ai_decision_scenarios` | 场景目录；不是模拟结果 |
| `ai_decision_history` | Registry/history 事件，不是业务过账审计 |
| Executive score | Legacy 模板常量 |
| Recommendation | 顾问输出，需人工判断 |
| Confidence | 辅助字段；统一校准规则 UNKNOWN |
| Adopt / Ignore | 对建议的反馈，不改变业务事实 |
| AI task | 待办/工作项，不等于目标域事务 |

---

## 6. 状态词汇

| Status | 使用位置 | 含义 |
|--------|----------|------|
| `metadata_only` | V15.1 strategy/recommendation/prediction/risk/scenario | 仅能力目录 |
| `implemented=0` | 同上 | 未实现执行能力 |
| `active` | Decision module registry | 注册项活动，不等于模型在线 |
| `completed` | AI decision history 默认 | metadata 事件完成，不等于业务完成 |
| `Unknown` | 对象分析异常降级 | 无法得出结果，不能解释为低风险 |
| `Normal` | 部分 fallback 风险标签 | 可能是默认值，不能作为已验证结论 |
| `Pending AI match` | Sales assistant 占位 | 尚无真实匹配 |
| `Adopt` / `Ignore` | 建议反馈 | 用户反馈选择 |
| `next` | Roadmap | 规划能力 |

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `templates/ai_decision_center.html` | 静态分数、建议、风险和 roadmap |
| `apps/ai_decision_center/ai_assistant_pages.py` | Decision Center、Sales/CRM assistant 页面 |
| `apps/ai_decision_center/ai_action_routes.py` | 搜索及对象级顾问入口、异常降级 |
| `apps/ai_decision_center/ai_hub_pages.py` | AI Center 与 adopt/ignore Dashboard |
| `apps/ai_decision_center/services.py` | V15.1 registry seed 和 framework context |
| `apps/ai_decision_center/repository.py` | `implemented=0`、metadata_only 与 history |
| `apps/ai_decision_center/routes.py` | 对外 health API |
| `apps/ai_decision_center/router.py` | 默认未启用、无 reasoning replacement |
| `database/v151_ai_decision_center_schema.py` | 七张 metadata 表 |
| `core/ai_decision/` | Registry 类型和默认 metadata |
| `docs/reports/V151_Volume019_AI_Decision_Center_Report.md` | Metadata-only 与限制声明 |
| `templates/ai_*.html` | 对象分析、对话、历史和任务表面 |
| `runtime/v14/legacy_support.py` | Legacy AI helpers 与启发式来源 |
| `v15/ai_operating_depth/` | Adopt/Ignore 不修改事实 |
| `v15/ai_working/decisions.py` / `task_engine.py` | Adopt/approve/create_task 的非业务执行边界 |
| `apps/ai_decision_center/` / `core/ai_decision/` / AI templates | UNKNOWN 检索范围 |

**Hard boundary:** Advisory only; never interpreted as Brain execute, Twin authorize, or Cap→grant.

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
