# AI Employee Center — Legacy Observation

**Evidence strength:** Strong（registry/schema/framework page）/ Medium（邻接 digital employee/workforce APIs）/ Missing（AI Employee Center 自身执行闭环）  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

## 1. Scope 与证据强度

本文件覆盖 `/ai_employee_center`、`/ai_employee_registry`、`/api/v15/ai_employee_center/health`，以及员工、角色、技能、知识、任务、会话、历史 registry。

Center 明确默认关闭，legacy AI/gateway 仍权威，并声明“不替换 AI runtime or agent”。邻接的 digital employee/workforce API 可列员工、询问、切换 work mode、计算 performance、创建任务或协作，但属于另一套运行面，不能反推 AI Employee Center 已执行任务。

本文件不打开或分析 Brain/Twin；AI Employee Center ≠ Brain execute。

## 2. 业务规则（稳定 ID）

| ID | 规则 | 触发/例外 | 证据强度 |
|---|---|---|---|
| AI-EMP-OBS-RULE-001 | AI Employee Center 首次读取时 seed employees、roles、skills、knowledge、tasks、conversations、history | seed 是 registry 初始化，不是执行 | Strong |
| AI-EMP-OBS-RULE-002 | framework page 只展示版本、health、员工/角色/技能数量及样例 key | 无操作 UI | Strong |
| AI-EMP-OBS-RULE-003 | registry page 展示 employee key/name | 不提供 create/edit/delete | Strong |
| AI-EMP-OBS-RULE-004 | 中心 API 当前只暴露 health | list 方法存在于 service，但 routes 未暴露 | Strong |
| AI-EMP-OBS-RULE-005 | employee registry 可优先读取持久化 seed，resolve 仍来自 core registry | metadata 来源并不完全统一 | Strong |
| AI-EMP-OBS-RULE-006 | roles/skills/knowledge/tasks/conversations 默认 `implemented=0`、`metadata_only` | employee registry 自身状态默认 active | Strong |
| AI-EMP-OBS-RULE-007 | AI employee history 可记录 employee/event/actor/detail/status | 未找到 Center 任务执行自动写历史的闭环 | Medium |
| AI-EMP-OBS-RULE-008 | 邻接 digital employee API 可按 session 上下文列员工、详情和 ask | 属 legacy authoritative runtime，不是 Center registry 执行 | Medium |
| AI-EMP-OBS-RULE-009 | 邻接 workforce API 可设置 work mode、查看 performance、创建 task、运行 collaboration pipeline | 部分 scenario 无 runner 时只返回 defined | Medium |
| AI-EMP-OBS-RULE-010 | AI Employee Center 本身没有 execute/approve/cancel/retry/result API | 不得等同 Brain execute | Strong negative |
| AI-EMP-OBS-RULE-011 | 中心级任务输入/输出 schema、工具权限、数据范围、预算、超时、重试和幂等为 `UNKNOWN` | registry task 仅 metadata | Missing |
| AI-EMP-OBS-RULE-012 | 人工确认、职责分离、可撤销、业务写入审计和责任归属为 `UNKNOWN` | 未见 Center execution gate | Missing |
| AI-EMP-OBS-RULE-013 | performance 的业务公式、质量样本与审计依据为 `UNKNOWN` | 邻接 API 返回计算结果但非本中心规则 | Missing |
| AI-EMP-OBS-RULE-014 | 邻接 Digital Employee 任务词汇含 Pending/In Progress/Completed/Failed/Cancelled，但 `complete_task` 未找到调用闭环 | 不能把枚举当自动执行证据 | Strong negative |
| AI-EMP-OBS-RULE-015 | 邻接 work mode 声明 human/assist/copilot/autonomous；Workforce task 默认 requires_approval | 未找到专用 approve/confirm API，不能证明人工确认闭环 | Medium |

## 3. 流程

### 3.1 Center framework

1. 访问 AI Employee Center。
2. Service 首次调用各 registry facade seed metadata。
3. health 汇总 registry 状态。
4. 页面读取 employees/roles/skills 并展示样例。
5. 不触发任务执行或业务写入。

### 3.2 邻接 workforce 表象

1. 从 session 取得 username/role。
2. 列员工或打开员工详情。
3. ask、work-mode、task、collaborate API 调用独立 digital employee/workforce 组件。
4. 有 pipeline 时运行协作；无 runner 的场景只返回 `defined`。

此邻接流程不属于 AI Employee Center 的 registry 执行链。

### 3.3 Center 执行流程

`选择 AI employee → 创建受控任务 → 权限/预算/人工确认 → 执行工具 → 结果审批 → 业务提交 → 审计/回滚`

整条 Center 流程为 `UNKNOWN`；未找到对应 API 和状态机。

## 4. 校验（强 / 弱 / 缺失）

| ID | 校验 | 强度 | 说明 |
|---|---|---|---|
| AI-EMP-OBS-VAL-001 | registry 各 key 唯一且 employee/task 等必填 key/name | 强（schema） | 只校验 metadata |
| AI-EMP-OBS-VAL-002 | Center health/page 的认证与权限 | 缺失/不明确 | 路由未见 RBAC |
| AI-EMP-OBS-VAL-003 | 邻接 ask/workforce API 的 module/action 权限 | 缺失/不明确 | 多路由未见显式 checker |
| AI-EMP-OBS-VAL-004 | work mode 值由 safety/store 接受性判断 | 中 | 具体枚举与授权不属于 Center |
| AI-EMP-OBS-VAL-005 | task type、employee、skill 兼容性 | 缺失（Center） | `UNKNOWN` |
| AI-EMP-OBS-VAL-006 | 高风险业务动作必须 human approve | 缺失（Center） | `UNKNOWN` |
| AI-EMP-OBS-VAL-007 | 工具 allowlist、tenant/owner 数据范围 | 缺失 | `UNKNOWN` |
| AI-EMP-OBS-VAL-008 | 重试、取消、超时、幂等、补偿 | 缺失 | `UNKNOWN` |
| AI-EMP-OBS-VAL-009 | 输出质量、引用证据和责任人 | 缺失 | `UNKNOWN` |

## 5. 数据含义

| 实体 | Legacy 表象 |
|---|---|
| `ai_employee_registry` | AI employee metadata：key/name/capabilities/status |
| `ai_employee_roles` | employee 的角色/scope metadata |
| `ai_employee_skills` | employee/domain skill metadata |
| `ai_employee_knowledge` | knowledge scope metadata |
| `ai_employee_tasks` | task key/employee/priority metadata，不是运行实例 |
| `ai_employee_conversations` | conversation/channel metadata，不是完整对话日志证明 |
| `ai_employee_history` | 通用 history 记录槽位 |
| digital employee/workforce | 邻接运行组件；与 Center registry 非同一能力层 |
| work mode / performance | 邻接 workforce 表象 |

未找到 Center 运行实例的 input、output、tool calls、approval、cost/token、started/finished time、error、retry、business mutation reference。全部 `UNKNOWN`。

## 6. 状态词汇

| 词汇 | 含义 |
|---|---|
| active | employee registry metadata 状态 |
| metadata_only | role/skill/knowledge/task/conversation 尚未实现 |
| implemented=0 | schema 明示未接运行 |
| completed | history 默认状态 |
| defined | 邻接 cooperation scenario 无 pipeline runner |
| enabled_by_default=false | Center 默认不接管 |
| legacy_ai_active=true | 旧 AI/gateway 权威 |
| Pending / In Progress / Completed / Failed / Cancelled | 邻接 Digital Employee task 状态；Center runtime 仍为 `UNKNOWN` |
| human / ai_assist / ai_copilot / ai_autonomous | 邻接 work mode；不等于 Center execution 状态 |

## 7. 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\router.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\routes.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\services.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\repository.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\employee_registry.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\role_registry.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\skill_registry.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\knowledge_registry.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\task_registry.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\conversation_registry.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\history.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\health.py`
- `H:\Workspace\EZAM_CRM - 9.0\apps\ai_employee_center\workforce_api.py`
- `H:\Workspace\EZAM_CRM - 9.0\database\v151_ai_employee_center_schema.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\ai_employee\employee.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\ai_employee\task.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\digital_employees\tasks.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\digital_employees\work_modes.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\workforce\task_queue.py`

**Excluded:** 未打开或分析 Brain/Twin 文件与实现。

## 8. EAOS 重写备注

- 可提炼为产品需求的只有：员工目录、角色/技能/知识声明、受控任务、会话与审计可见性。
- EAOS 不继承 Center schema、seed-on-read、legacy workforce API 或任何旧执行架构。
- AI Employee 必须通过 EAOS 独立的权限、工具、审批、证据、预算、幂等和审计机制工作。
- AI Employee Center 永远不等同 Brain execute；不得因 employee/task key 存在就授予业务写权限。
